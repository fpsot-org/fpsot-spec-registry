#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Tests examples/check-examples.py: the repository passes, and each broken copy fails
# for the reason that its case names. Each case copies the files that the check reads,
# breaks one rule, and expects the check to report that rule.
set -uo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
check="$here/examples/check-examples.py"
fail=0
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

if ! python3 -I "$check" "$here"; then
  echo "FAIL: the repository itself does not pass"; fail=1
fi

# case_fails NAME EXPECTED-REGEX PYTHON: the script runs in a copy of the repository.
case_fails() {
  local name=$1 want=$2 script=$3 dir="$tmp/$1" out
  mkdir -p "$dir"
  cp -r "$here/model" "$here/packs" "$here/profiles" "$here/registry" "$here/examples" "$dir/"
  (cd "$dir" && python3 -I -c "import hashlib, json, yaml
def rj(p): return json.load(open(p, encoding='utf-8'))
def wj(p, d): json.dump(d, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
def ry(p): return yaml.safe_load(open(p, encoding='utf-8'))
def wy(p, d): yaml.safe_dump(d, open(p, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False)
D = 'examples/pleasure-craft/'
F2, F4, F5, F6 = D + 'filings/02-ownership-transfer.json', D + 'filings/04-destruction-order.json', D + 'filings/05-filing-correction.json', D + 'filings/06-license-renewal.json'
CH, SA, SN, VW, LG = D + 'chain.json', D + 'salts.json', D + 'snapshots.json', D + 'views.json', D + 'log.json'
QC = 'examples/ca-qc/beneficiary-views.json'
def canon(d): return json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
def mth(l):
    if len(l) == 1: return hashlib.sha256(b'\\x00' + bytes.fromhex(l[0])).digest()
    k = 1
    while k * 2 < len(l): k *= 2
    return hashlib.sha256(b'\\x01' + mth(l[:k]) + mth(l[k:])).digest()
E1, E2 = D + 'events/filing-recorded.json', D + 'events/state-changed.json'
CF, PK = 'profiles/ca-federal.yaml', 'packs/pleasure-craft.yaml'
$script") || { echo "FAIL: case $name: the setup script failed"; fail=1; return; }
  if out=$(python3 -I "$check" "$dir" 2>&1); then
    echo "FAIL: case $name passed but should fail"; fail=1
  elif ! grep -qE -- "$want" <<<"$out"; then
    echo "FAIL: case $name failed for another reason:"; echo "$out" | head -5; fail=1
  else
    echo "ok: case $name fails"
  fi
}

# Filings and the light chain (REG-020 to REG-033).
case_fails filing-edited-in-place 'commitment of sequence 2 does not match the filing and its salt \(REG-031, REG-022\)' \
  'd = rj(F2); d["transferCause"] = "death"; wj(F2, d)'
case_fails chain-gap 'sequences must run from 1 with no gap \(REG-030\)' \
  'd = rj(CH); d["chainEntries"][2]["sequence"] = 6; wj(CH, d)'
case_fails broken-chain-link 'previousCommitment of sequence 3 is not the commitment of sequence 2 \(REG-030\)' \
  'd = rj(CH); d["chainEntries"][1]["commitment"] = "0" * 64; wj(CH, d)'
case_fails salt-kept-after-destruction 'content and its salt destroyed together \(REG-093, LOG-081\)' \
  'd = rj(SA); d[rj(CH)["tombstones"][0]["filingId"]] = "00" * 32; wj(SA, d)'
case_fails destruction-without-tombstone 'must leave a tombstone \(REG-094\)' \
  'd = rj(CH); d["tombstones"] = []; wj(CH, d)'
case_fails destruction-without-basis 'a destruction filing needs legalBasis \(REG-093\)' \
  'd = rj(F4); del d["legalBasis"]; wj(F4, d)'
case_fails late-transfer-marked-met 'deadlineStatus must be missed, from the deadline of the profile \(REG-033\)' \
  'd = rj(F2); d["submittedAt"] = "2026-07-20T15:00:00Z"; wj(F2, d)'
case_fails term-not-from-profile 'validity must be 2031-05-20 to 2036-05-20, from the term of the profile \(REG-058, REG-014\)' \
  'd = rj(F6); d["changes"]["opens"]["entitlements"][0]["validity"]["end"] = "2041-05-20"; wj(F6, d)'
case_fails time-state-set-by-filing 'sets expired, which is not an act-driven state \(REG-045\)' \
  'd = rj(F6); d["changes"]["opens"]["entitlements"][0]["lifecycleState"] = "expired"; wj(F6, d)'
case_fails unknown-filing-type 'filing type license-extension is not in the catalog of the pack \(REG-021\)' \
  'd = rj(F6); d["filingType"] = "license-extension"; wj(F6, d)'
case_fails transfer-without-cause 'states one of the causes .* \(REG-055\)' \
  'd = rj(F2); del d["transferCause"]; wj(F2, d)'
case_fails history-slots-in-filing 'holds history slots, which only the replay adds \(REG-041\)' \
  'd = rj(F6); d["changes"]["opens"]["entitlements"][0]["createdByFiling"] = d["id"]; wj(F6, d)'
case_fails correction-of-later-filing 'must be an earlier filing \(REG-027\)' \
  'd = rj(F5); d["corrects"] = rj(F6)["id"]; wj(F5, d)'
case_fails representation-without-id 'authority representation needs representationId \(REG-025\)' \
  'd = rj(F2); d["authority"] = {"kind": "representation"}; wj(F2, d)'
case_fails unknown-party 'is not a Party of parties.json \(REG-061\)' \
  'd = rj(F2); d["onBehalfOfPartyId"] = "019a1b2c-3d4e-7f01-8a01-000000000999"; wj(F2, d)'
case_fails not-retroactive 'takes no effective instant before submission \(REG-023\)' \
  'd = rj(F6); d["effectiveAt"] = "2031-05-19T16:00:00Z"; wj(F6, d)'
case_fails status-not-in-pack 'the payment and review statuses come from the lists of the pack \(REG-024\)' \
  'd = rj(F6); d["paymentStatus"] = "waived"; wj(F6, d)'
case_fails evidence-without-retention 'names no retention class of the profile for its type \(REG-090\)' \
  'd = rj(F2); d["evidence"][0]["retentionClass"] = "forever"; wj(F2, d)'

# The log series of the register (REG-031, REG-032).
case_fails tail-filing-rewritten 'chain entry 6 has no leaf in the log series of the register \(REG-032\)' \
  'd = rj(F6); d["paymentStatus"] = "exempt"; wj(F6, d)
c = rj(CH); c["chainEntries"][5]["commitment"] = hashlib.sha256(bytes.fromhex(rj(SA)[d["id"]]) + canon(d)).hexdigest(); wj(CH, c)'
case_fails tail-truncated 'leaf 0 of shard registry.example.org/pleasure-craft-licenses-2031 matches no chain entry or tombstone \(REG-032\)' \
  'import os; d = rj(F6); os.remove(F6)
c = rj(CH); c["chainEntries"].pop(); wj(CH, c)
a = rj(SA); del a[d["id"]]; wj(SA, a)'
case_fails log-order-mismatch 'the log indexes must increase with the sequence \(REG-032\)' \
  'g = rj(LG); sh = g["logShards"][0]; sh["leaves"][1], sh["leaves"][2] = sh["leaves"][2], sh["leaves"][1]
sh["checkpoints"] = [{"treeSize": n, "rootHash": mth(sh["leaves"][:n]).hex()} for n in (2, 5)]; wj(LG, g)'
case_fails checkpoint-not-matching 'checkpoint 2 of shard registry.example.org/pleasure-craft-licenses-2026 does not match the leaves' \
  'g = rj(LG); g["logShards"][0]["checkpoints"][0]["rootHash"] = "0" * 64; wj(LG, g)'

# Completion, corrections, restatements and destruction (REG-022, REG-029, REG-093, REG-094).
case_fails updated-after-final 'updatedAt must be the completion: nothing changes after a final status \(REG-022\)' \
  'd = rj(F6); d["updatedAt"] = "2031-06-01T12:00:00Z"; wj(F6, d)'
case_fails retroactive-without-restatement 'must restate the entitlement .* that filing .* opened \(REG-029\)' \
  'd = rj(F5); del d["changes"]["restates"]; wj(F5, d)'
case_fails tombstone-drops-corrects 'must keep the corrected filing \(REG-094\)' \
  'c = rj(CH); del c["tombstones"][1]["corrects"]; wj(CH, c)'
case_fails destroyed-value-survives 'still holds the value .* that destruction filing .* targets: destroy it or list it as retained \(REG-093\)' \
  'd = rj(F5); t = rj(F4)["destructionTargets"][0]["id"]; d["evidence"].append({"evidenceType": "identity-document", "documentId": t, "digest": "a" * 64, "retentionClass": "license-evidence"}); wj(F5, d)'
case_fails tenancy-not-in-profile 'tenancy undivided-co-ownership is not a code of the profile \(REG-053\)' \
  'd = rj(F2); d["changes"]["opens"]["ownerGroups"][0]["tenancy"] = "undivided-co-ownership"; wj(F2, d)'
case_fails count-from-completion 'validity must be 2031-05-20 to 2036-05-20, from the term of the profile' \
  'd = ry(CF); d["registers"][0]["terms"][0]["countFrom"] = "completion-date"; wy(CF, d)
d = rj(F2); d["changes"]["opens"]["entitlements"][0]["validity"] = {"start": "2026-06-26", "end": "2031-06-26"}; wj(F2, d)
d = rj(F6); d["changes"]["opens"]["entitlements"][0]["validity"]["end"] = "2041-05-20"; wj(F6, d)'
case_fails public-view-confirms-record 'neither confirms nor denies a record \(REG-012\)' \
  'd = rj(VW); d["extracts"][1]["subjects"] = d["extracts"][0]["subjects"]; wj(VW, d)'
case_fails conditional-field-shown 'field UltimateBeneficiary.homeAddress is agency for this record, so a public view cannot show it \(REG-070, REG-071\)' \
  'd = rj(QC); r = d["records"][0]; x = d["extracts"][0]; x["fields"].append({"path": "UltimateBeneficiary.homeAddress", "entityId": r["id"], "value": r["homeAddress"]}); x["omissions"] = x["omissions"][1:]; wj(QC, d)'

# Assets, ownership and entitlements (REG-050 to REG-061).
case_fails search-key-not-normalized 'search key that is not the normalized value \(REG-051\)' \
  'd = rj(F6); d["changes"]["opens"]["entitlements"][0]["number"]["searchKey"] = "EX-000001"; wj(F6, d)'
case_fails sole-group-two-members 'a sole group has one member and the whole asset \(REG-053\)' \
  'd = rj(F2); g = d["changes"]["opens"]["ownerGroups"][0]; g["members"].append({"partyId": d["parties"][0]["partyId"]}); wj(F2, d)'
case_fails pack-redefines-party 'the pack schema redefines Party \(REG-101\)' \
  'd = ry("model/pleasure-craft.yaml"); d["classes"]["Party"] = {"description": "A local party."}; wy("model/pleasure-craft.yaml", d)'
case_fails act-transition-to-time-state 'by a filing must reach an act-driven state \(REG-045\)' \
  'd = ry(PK); d["entitlementClasses"][0]["transitions"].append({"from": "active", "to": "expired", "filingType": "license-cancellation"}); wy(PK, d)'

# Derived state (REG-040 to REG-046, REG-095).
case_fails snapshot-not-from-filings 'does not match the replay of the filings \(REG-040, REG-042\)' \
  'd = rj(SN); d["snapshots"][4]["ownerGroups"][0]["members"][0]["partyId"] = rj(F2)["parties"][0]["partyId"]; wj(SN, d)'
case_fails destroyed-row-shown-as-value 'does not match the replay of the filings \(REG-040, REG-042\)' \
  'd = rj(SN); d["snapshots"][0].pop("destroyedRows"); wj(SN, d)'

# Profiles (REG-010 to REG-016).
case_fails source-not-listed 'cites source sor-2099-1, which the profile does not list \(REG-013\)' \
  'd = ry(CF); d["registers"][0]["terms"][0]["sourceId"] = "sor-2099-1"; wy(CF, d)'
case_fails title-effect 'declares title, which no profile of this release declares \(REG-011\)' \
  'd = ry(CF); d["registers"][0]["legalEffect"] = "title"; wy(CF, d)'
case_fails closed-register-public-field 'closed register pleasure-craft-licenses makes a field public \(REG-012\)' \
  'd = ry(CF); d["registers"][0]["fieldPolicies"][3]["visibility"] = "public"; wy(CF, d)'
case_fails similar-without-algorithm 'uses similar matching without its algorithm \(REG-081\)' \
  'd = ry(CF); d["registers"][0]["searchModes"][0]["matching"] = "similar"; wy(CF, d)'
case_fails access-without-logging 'must log each read \(REG-076\)' \
  'd = ry(CF); d["registers"][0]["accessPolicies"][0]["loggingDuty"] = False; wy(CF, d)'

# Views (REG-070 to REG-084).
case_fails public-view-shows-holder 'a public view of a closed register shows no field and neither confirms nor denies a record \(REG-012\)' \
  'd = rj(VW); x = d["extracts"][1]; x["fields"] = [d["extracts"][0]["fields"][2]]; x["omissions"] = [o for o in x["omissions"] if o["path"] != "Entitlement.parties.partyId"]; wj(VW, d)'
case_fails agency-view-without-policy 'needs an access policy of the profile that grants it \(REG-074\)' \
  'd = rj(VW); del d["extracts"][0]["accessPolicy"]; wj(VW, d)'
case_fails wrong-omission-reason 'must give the reason not-public-by-law \(REG-073\)' \
  'd = rj(VW); d["extracts"][1]["omissions"][0]["reason"] = "withheld-on-application"; wj(VW, d)'
case_fails extract-value-not-replayed 'does not hold the replayed value \(REG-084\)' \
  'd = rj(VW); d["extracts"][0]["fields"][0]["value"] = "EX 000002"; wj(VW, d)'
case_fails search-without-last-filing 'must state the last filing that its result reflects \(REG-082\)' \
  'd = rj(VW); d["searchRecords"][0]["lastFilingSequence"] = 2; wj(VW, d)'

# Events (REG-102, REG-103).
case_fails party-id-in-event 'holds a party id or an identifier value: events hold no personal value \(REG-103\)' \
  'd = rj(E1); d["subject"] = rj(F2)["onBehalfOfPartyId"]; wj(E1, d)'
case_fails license-number-in-event 'is not allowed by the event schema \(API-103\)' \
  'd = rj(E1); d["data"]["licenseNumber"] = "EX 000001"; wj(E1, d)'
case_fails event-not-matching-filing 'data.sequence must match the filing \(REG-102\)' \
  'd = rj(E1); d["data"]["sequence"] = 3; wj(E1, d)'
case_fails state-event-missing-row 'data.rows must list the rows that the filing opened and ended \(REG-102\)' \
  'd = rj(E2); d["data"]["rows"].pop(); wj(E2, d)'

# Features (REG-105, TST-032).
case_fails feature-parity 'same tags and steps \(TST-032\)' \
  'p = "examples/features/fr/pleasure-craft-license.feature"; s = open(p, encoding="utf-8").read().replace("@pleasure-craft-license-002", "@pleasure-craft-license-009"); open(p, "w", encoding="utf-8").write(s)'
case_fails feature-unknown-filing-type 'names filing type license-extension, which the pack does not declare' \
  'p = "examples/features/en/pleasure-craft-license.feature"; s = open(p, encoding="utf-8").read().replace("the filing \"license-renewal\"", "the filing \"license-extension\""); open(p, "w", encoding="utf-8").write(s)'

[ $fail -eq 0 ] && echo "PASS: every case"
exit $fail
