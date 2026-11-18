# SPDX-License-Identifier: Apache-2.0
"""Checks the example files of the FPSOT registry specification.

Usage: python3 -I examples/check-examples.py [ROOT]

ROOT is the repository root, by default the parent of this folder. The check reads
model/registry.yaml with its imports and the pack schemas, packs/, profiles/,
registry/events/ and examples/. It needs the Python standard library and PyYAML only
(examples/requirements.txt).

It runs three kinds of checks, and reports every failure with the rule it breaks.

- Schema checks: each file against its class of the LinkML model, through a small
  reader of the parts of LinkML that the model uses (inheritance and mixins, required
  slots, ranges, types, patterns, enumerations, lists and closed classes). It is not a
  LinkML validator.
- Structural checks of the rules: profiles cite their sources, a closed register shows
  nothing in public, filing types come from the pack catalog, statuses from the pack
  lists, authority and parties resolve, terms and deadlines follow the profile,
  identifiers carry their normalized search key, owner groups hold the whole asset,
  views show only what their visibility class allows, and events hold no personal value.
- Chain and log: the light chain verifies, with each destroyed filing replaced by its
  tombstone; the leaves of the log series of the register map one-to-one, in order, onto the
  chain entries; each checkpoint matches its leaves; and the head of the chain is the last leaf
  of the newest checkpoint. log.json stands in for the read interface of LOG-036.
- Replay: replaying the filings, with corrections, restatements and tombstones, rebuilds each
  expected bitemporal snapshot; a retroactive filing restates the later versions it affects; no
  value that a destruction targets survives in another filing; and views apply conditional
  visibility to the record they show, including a view of a register whose pack is planned.

The fixture stands in the compact JSON form of each filing, with sorted keys, for its
sealed bytes: the commitment is SHA-256 over the salt, then those bytes (REG-031).
"""
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys
from fractions import Fraction
from zoneinfo import ZoneInfo

import yaml

BUILTIN = {"string", "integer", "boolean", "uri", "date", "datetime", "double", "float"}
URI = re.compile(r"^(https?://|mailto:|tel:)\S+$")
VISIBILITY = ["public", "parties", "agency", "restricted"]
FINAL = {"completed", "rejected", "withdrawn"}
HISTORY = {"createdByFiling", "endedByFiling", "validFrom", "validTo"}
COUNT_FROM = {"effective-date": "effectiveAt", "submission-date": "submittedAt", "completion-date": "completedAt"}
REGISTER = "pleasure-craft-licenses"
KIND_LIST = {"asset": "assets", "owner-group": "ownerGroups", "entitlement": "entitlements",
             "encumbrance": "encumbrances"}

failures = []


def fail(where, message, rule):
    failures.append(f"FAIL: {where}: {message} ({rule})")


def load(path):
    with open(path, encoding="utf-8") as f:
        if path.endswith((".yaml", ".yml")):
            return yaml.safe_load(f)
        return json.load(f)


def canonical(doc):
    """The stand-in for the sealed bytes of a filing."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def commitment(salt_hex, doc):
    return hashlib.sha256(bytes.fromhex(salt_hex) + canonical(doc)).hexdigest()


class Model:
    """The parts of a LinkML schema that the check reads."""

    def __init__(self, *paths):
        self.types, self.classes, self.enums, self.slots = {}, {}, {}, {}
        self.seen = set()
        for p in paths:
            self._read(p)
        self.polymorphic = {}

    def _read(self, path):
        path = os.path.normpath(path)
        if path in self.seen:
            return
        self.seen.add(path)
        schema = load(path)
        for imp in schema.get("imports") or []:
            if not imp.startswith("linkml:"):
                # LinkML 1.12 resolves an import against the folder of the schema that imports it.
                self._read(os.path.join(os.path.dirname(path), imp + ".yaml"))
        self.types.update(schema.get("types") or {})
        self.classes.update(schema.get("classes") or {})
        self.enums.update(schema.get("enums") or {})
        self.slots.update(schema.get("slots") or {})

    def ancestors(self, cls):
        out, todo = [], [cls]
        while todo:
            c = todo.pop(0)
            if c in out or c not in self.classes:
                continue
            out.append(c)
            spec = self.classes[c]
            if spec.get("is_a"):
                todo.append(spec["is_a"])
            todo += spec.get("mixins") or []
        return out

    def attrs(self, cls):
        merged = {}
        for c in reversed(self.ancestors(cls)):
            spec = self.classes[c]
            for name in spec.get("slots") or []:
                merged[name] = dict(self.slots.get(name) or {})
            for name, slot in (spec.get("attributes") or {}).items():
                merged[name] = dict(slot or {})
            for name, usage in (spec.get("slot_usage") or {}).items():
                merged.setdefault(name, {}).update(usage or {})
        return merged

    def identifier(self, cls):
        for name, slot in self.attrs(cls).items():
            if slot.get("identifier"):
                return name, slot
        return None, None

    def base(self, rng):
        patterns = []
        while rng not in BUILTIN:
            t = self.types[rng]
            if t.get("pattern"):
                patterns.append(t["pattern"])
            rng = t["typeof"]
        return rng, patterns

    def check(self, obj, cls, where, path="$"):
        if isinstance(obj, dict) and cls in self.polymorphic:
            cls = self.polymorphic[cls](obj) or cls
        spec = self.classes[cls]
        if spec.get("class_uri") == "linkml:Any":
            return
        if not isinstance(obj, dict):
            fail(where, f"{path} must be an object of class {cls}", "REG-021")
            return
        attrs = self.attrs(cls)
        open_class = any(self.classes[c].get("extra_slots") for c in self.ancestors(cls))
        for key in obj:
            if key not in attrs and not open_class:
                fail(where, f"{path}.{key} is not a slot of {cls}", "REG-021")
        for name, slot in attrs.items():
            if name not in obj:
                if slot.get("required") or slot.get("identifier"):
                    fail(where, f"{path}.{name} is required in {cls}", "REG-021")
                continue
            value = obj[name]
            if slot.get("multivalued"):
                if not isinstance(value, list) or not value:
                    fail(where, f"{path}.{name} must be a list with at least one item", "REG-021")
                    continue
                for i, item in enumerate(value):
                    self.value(item, slot, where, f"{path}.{name}[{i}]")
            else:
                self.value(value, slot, where, f"{path}.{name}")

    def value(self, v, slot, where, path):
        rng = slot.get("range", "string")
        if rng in self.enums:
            if v not in (self.enums[rng].get("permissible_values") or {}):
                fail(where, f"{path} has {v!r}, which is not a value of {rng}", "REG-021")
            return
        if rng in self.classes:
            ident, ident_slot = self.identifier(rng)
            if slot.get("inlined") or slot.get("inlined_as_list") or ident is None:
                self.check(v, rng, where, path)
            else:
                self.value(v, ident_slot, where, path)
            return
        base, patterns = self.base(rng)
        if slot.get("pattern"):
            patterns.append(slot["pattern"])
        ok = {"integer": isinstance(v, int) and not isinstance(v, bool),
              "boolean": isinstance(v, bool),
              "double": isinstance(v, (int, float)) and not isinstance(v, bool),
              "float": isinstance(v, (int, float)) and not isinstance(v, bool),
              "uri": isinstance(v, str) and bool(URI.match(v))}.get(base, isinstance(v, str))
        if not ok:
            fail(where, f"{path} has {v!r}, which is not a {rng}", "REG-021")
            return
        for p in patterns:
            if isinstance(v, str) and not re.search(p, v):
                fail(where, f"{path} has {v!r}, which does not match the pattern of {rng}", "REG-021")
        if "minimum_value" in slot and v < slot["minimum_value"]:
            fail(where, f"{path} is below {slot['minimum_value']}", "REG-021")


def instant(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def add_period(day, duration):
    """Adds a duration of whole years, months or days to a date, as DAT-020 writes it."""
    m = re.fullmatch(r"P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?", duration)
    if not m:
        raise ValueError(f"unsupported duration {duration}")
    years, months, days = (int(x or 0) for x in m.groups())
    month = day.month - 1 + months
    year = day.year + years + month // 12
    month = month % 12 + 1
    d = min(day.day, [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.date(year, month, d) + dt.timedelta(days=days)


def normalize(value, steps):
    for s in steps:
        if s == "upper-case":
            value = value.upper()
        elif s == "remove-spaces":
            value = value.replace(" ", "")
        elif s == "remove-hyphens":
            value = value.replace("-", "")
    return value


def in_force(item, day):
    v = item["validity"]
    return v["start"] <= day and ("end" not in v or day < v["end"])


def strip_history(row):
    return {k: v for k, v in row.items() if k not in HISTORY}


def replay(filings, tombstones, valid_at, recorded_at, pack, tz):
    """Rebuilds derived state as of valid_at, as recorded at recorded_at (REG-040, REG-042).

    filings and tombstones map a filing id to its document. A correction, live or destroyed,
    replaces the filing that it corrects, at the place of that filing's sequence. A restatement
    replaces the later version that it restates. A tombstone gives rows by id only, so the rows
    that only it supports come out as destroyed rows (REG-095). Returns a StateSnapshot."""
    known = [f for f in filings.values()
             if f.get("processingStatus") == "completed" and f["completedAt"] <= recorded_at]
    known += [t for t in tombstones.values() if t["completedAt"] <= recorded_at]

    def fid(x):
        return x.get("id") or x.get("filingId")

    replaced, restated = {}, {}
    for x in sorted(known, key=lambda x: x["sequence"]):
        if x.get("category") == "correction" and x.get("corrects"):
            replaced[x["corrects"]] = x
        if "filingId" in x:
            for r in x.get("restated") or []:
                restated[(r["filingId"], r["kind"], r["entityId"])] = None
        for r in (x.get("changes") or {}).get("restates") or []:
            for kind, lst in KIND_LIST.items():
                for row in (r.get("opens") or {}).get(lst) or []:
                    restated[(r["filingId"], kind, row["id"])] = row

    def rows_of(src):
        """The opened rows, as (kind, id, row or None when destroyed), and the ended rows."""
        if "filingId" in src:
            return [(r["kind"], r["entityId"], None) for r in src.get("opened") or []], src.get("ended") or []
        changes = src.get("changes") or {}
        opened = [(kind, row["id"], row) for kind, lst in KIND_LIST.items()
                  for row in (changes.get("opens") or {}).get(lst) or []]
        return opened, changes.get("ends") or []

    entries = []
    for x in known:
        if x["category"] != "change":
            continue
        src = replaced.get(fid(x), x)
        opened, ended = rows_of(src)
        # A correction keeps the place of the filing it corrects (REG-040).
        entries.append((src["effectiveAt"], x["sequence"], fid(src), opened, ended))
    entries.sort(key=lambda e: (e[0], e[1]))
    current, versions = {}, []
    for eff, _, by, opened, ended in entries:
        for ref in ended:
            key = (ref["kind"], ref["entityId"])
            if key in current:
                v = current.pop(key)
                v["validTo"], v["endedByFiling"] = eff, by
        for kind, rid, row in opened:
            key = (kind, rid)
            if key in current:
                v = current.pop(key)
                v["validTo"], v["endedByFiling"] = eff, by
            if (by, kind, rid) in restated:
                row = restated[(by, kind, rid)]
            v = {"kind": kind, "id": rid, "row": row, "createdByFiling": by, "validFrom": eff,
                 "destroyed": row is None}
            current[key] = v
            versions.append(v)
    snap = {"registerCode": REGISTER, "validAt": valid_at, "recordedAt": recorded_at,
            "lastFilingSequence": max([x["sequence"] for x in known], default=0)}
    day = instant(valid_at).astimezone(tz).date().isoformat()
    time_state = {c["code"]: [t["to"] for t in c["transitions"] if t.get("scheduledEvent") == "validity-ended"]
                  for c in pack.get("entitlementClasses") or []}
    for v in sorted(versions, key=lambda v: (v["kind"], v["id"], v["validFrom"])):
        if not (v["validFrom"] <= valid_at and ("validTo" not in v or valid_at < v["validTo"])):
            continue
        if v["destroyed"]:
            snap.setdefault("destroyedRows", []).append(
                {"kind": v["kind"], "entityId": v["id"], "createdByFiling": v["createdByFiling"]})
            continue
        row = dict(strip_history(v["row"]))
        row["createdByFiling"], row["validFrom"] = v["createdByFiling"], v["validFrom"]
        if "validTo" in v:
            row["endedByFiling"], row["validTo"] = v["endedByFiling"], v["validTo"]
        if v["kind"] == "entitlement":
            ends = row["validity"].get("end")
            ts = time_state.get(row["entitlementClass"]) or []
            row["state"] = ts[0] if ends and day >= ends and ts else row["lifecycleState"]
        snap.setdefault(KIND_LIST[v["kind"]], []).append(row)
    return snap


def effective_policy(path, register, pack, core, record=None):
    """The visibility, opposability and omission reason of a field (REG-070, REG-071)."""
    for policies in (register.get("fieldPolicies") or [], pack.get("fieldDefaults") or []):
        for p in policies:
            if p["path"] == path:
                vis = p["visibility"]
                if "when" in p and record is None:
                    # Without the record, the narrower of the two classes applies.
                    vis = max(vis, p["otherwise"], key=VISIBILITY.index)
                elif "when" in p:
                    present = bool(record.get(p["when"]["field"].split(".")[-1]))
                    holds = present if p["when"]["test"] == "present" else not present
                    vis = vis if holds else p["otherwise"]
                return vis, p["opposable"], p["omissionReason"]
    d = core["defaults"]
    return d["unlistedFieldVisibility"], d["unlistedFieldOpposable"], "not-public-by-law"


def find_row(snapshot, entity_id):
    for lst in ("assets", "ownerGroups", "entitlements", "encumbrances"):
        for row in snapshot.get(lst) or []:
            if row["id"] == entity_id:
                return row
    return None


def mth(leaves):
    """The root of an RFC 6962 Merkle tree over leaves given as hexadecimal hashes."""
    if not leaves:
        return hashlib.sha256(b"").digest()
    if len(leaves) == 1:
        return hashlib.sha256(b"\x00" + bytes.fromhex(leaves[0])).digest()
    k = 1
    while k * 2 < len(leaves):
        k *= 2
    return hashlib.sha256(b"\x01" + mth(leaves[:k]) + mth(leaves[k:])).digest()


def field_value(snapshot, path, entity_id):
    """The value of a field path in a row of a snapshot, for an extract."""
    cls, *slots = path.split(".")
    for lst in ("assets", "ownerGroups", "entitlements", "encumbrances"):
        for row in snapshot.get(lst) or []:
            if row["id"] != entity_id:
                continue
            vals = [row]
            for s in slots:
                nxt = []
                for x in vals:
                    y = x.get(s) if isinstance(x, dict) else None
                    nxt += y if isinstance(y, list) else ([] if y is None else [y])
                vals = nxt
            return vals
    return None


def gherkin(path):
    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f]
    scenarios, tags, current = [], [], None
    for line in lines[1:]:
        s = line.strip()
        if s.startswith("@"):
            tags = s.split()
        elif re.match(r"^(Scenario|Scénario|Scenario Outline|Plan du scénario):", s):
            current = {"tags": tags, "steps": []}
            scenarios.append(current)
            tags = []
        elif current is not None and re.match(r"^(Given|When|Then|And|But|Étant donné|Quand|Alors|Et|Mais)\b", s):
            current["steps"].append(s)
    return lines[0], scenarios


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
    ex = os.path.join(root, "examples", "pleasure-craft")

    def rel(p):
        return os.path.relpath(p, root)

    # Packs (REG-100, REG-101) and the model with each pack schema.
    packs, schemas = {}, [os.path.join(root, "model", "registry.yaml")]
    for p in sorted(glob.glob(os.path.join(root, "packs", "*.yaml"))):
        doc = load(p)
        packs[(doc.get("code"), doc.get("version"))] = (rel(p), doc)
        schemas.append(os.path.join(root, doc.get("schema", "")))
    for s in schemas[1:]:
        if not os.path.exists(s):
            fail("packs", f"pack schema {rel(s)} is missing", "REG-100")
    model = Model(*[s for s in schemas if os.path.exists(s)])
    asset_class = {}
    for where, doc in packs.values():
        model.check(doc, "DomainPack", where)
        if os.path.basename(where) != doc.get("code", "") + ".yaml":
            fail(where, "the file name must be the code of the pack", "REG-100")
        for k in doc.get("assetKinds") or []:
            if "Asset" not in model.ancestors(k["schemaClass"]) or k["schemaClass"] == "Asset":
                fail(where, f"asset kind {k['code']} needs a class of the pack schema that is_a Asset", "REG-050")
            asset_class[k["code"]] = k["schemaClass"]
        for c in ("Party", "Asset", "Filing", "OwnerGroup", "Entitlement", "Encumbrance"):
            schema = load(os.path.join(root, doc.get("schema", "")))
            if c in (schema.get("classes") or {}):
                fail(where, f"the pack schema redefines {c}", "REG-101")
        schemes = {s["code"] for s in doc.get("identifierSchemes") or []}
        types = {t["code"]: t for t in doc.get("filingTypes") or []}
        for ec in doc.get("entitlementClasses") or []:
            if ec["numberScheme"] not in schemes:
                fail(where, f"class {ec['code']} names an unknown number scheme", "REG-051")
            for t in ec["transitions"]:
                if ("filingType" in t) == ("scheduledEvent" in t):
                    fail(where, f"transition {t['from']} to {t['to']} needs a filing type or a scheduled event", "REG-045")
                if "filingType" in t and (t["filingType"] not in types or t["to"] not in ec["actStates"]):
                    fail(where, f"transition to {t['to']} by a filing must reach an act-driven state", "REG-045")
                if "scheduledEvent" in t and t["to"] not in ec["timeStates"]:
                    fail(where, f"transition to {t['to']} by a scheduled event must reach a time-driven state", "REG-045")
    model.polymorphic["Asset"] = lambda o: asset_class.get(o.get("assetKind"))

    # Profiles (REG-010 to REG-016).
    profiles = {}
    for p in sorted(glob.glob(os.path.join(root, "profiles", "*.yaml"))):
        doc = load(p)
        model.check(doc, "Profile", rel(p))
        if os.path.basename(p) != doc.get("code", "") + ".yaml":
            fail(rel(p), "the file name must be the code of the profile", "REG-013")
        profiles[doc.get("code")] = (rel(p), doc)
    if "core" not in profiles or "defaults" not in profiles["core"][1]:
        fail("profiles", "the core profile with its defaults is missing", "REG-016")
        core = {"defaults": {"unlistedFieldVisibility": "restricted", "unlistedFieldOpposable": False}}
    else:
        core = profiles["core"][1]
    registers = {}
    for code, (where, prof) in profiles.items():
        if code != "core" and "jurisdiction" not in prof:
            fail(where, "a jurisdiction profile names its jurisdiction", "REG-013")
        ids = {s["id"] for s in prof.get("sources") or []}
        for reg in prof.get("registers") or []:
            registers[reg["code"]] = (where, prof, reg)
            cited = reg["legalInstruments"] + reg["legalEffectSources"] + reg["publicitySources"]
            for group in ("fieldPolicies", "accessPolicies", "searchModes", "retentionClasses", "terms",
                          "deadlines", "scheduledExpiries", "externalRightsRegisters"):
                for item in reg.get(group) or []:
                    cited += item.get("legalBasisSourceIds") or []
                    if "sourceId" in item:
                        cited.append(item["sourceId"])
                    elif group in ("terms", "deadlines", "retentionClasses", "scheduledExpiries"):
                        fail(where, f"a parameter of {group} in {reg['code']} cites no source", "REG-013")
            for s in cited:
                if s not in ids:
                    fail(where, f"register {reg['code']} cites source {s}, which the profile does not list", "REG-013")
            if reg["legalEffect"] == "title":
                fail(where, f"register {reg['code']} declares title, which no profile of this release declares",
                     "REG-011")
            pk = reg["pack"]
            if pk["status"] == "published" and (pk["code"], pk.get("version")) not in packs:
                fail(where, f"pack {pk['code']} {pk.get('version')} is not in packs/", "REG-010")
            if reg["publicityRegime"] == "closed":
                if any(f["visibility"] == "public" or f.get("otherwise") == "public"
                       for f in reg.get("fieldPolicies") or []):
                    fail(where, f"closed register {reg['code']} makes a field public", "REG-012")
                if any("public" in m["openTo"] for m in reg.get("searchModes") or []):
                    fail(where, f"closed register {reg['code']} opens a search mode to the public", "REG-012")
            for f in reg.get("fieldPolicies") or []:
                if ("when" in f) != ("otherwise" in f):
                    fail(where, f"conditional policy of {f['path']} needs both when and otherwise", "REG-071")
            for a in reg.get("accessPolicies") or []:
                if a["loggingDuty"] is not True:
                    fail(where, f"access policy {a['code']} must log each read", "REG-076")
            for m in reg.get("searchModes") or []:
                if m["matching"] == "similar" and not m.get("algorithm"):
                    fail(where, f"search mode {m['code']} uses similar matching without its algorithm", "REG-081")
    if REGISTER not in registers:
        fail("profiles", f"no profile declares the register {REGISTER}", "REG-010")
        print("\n".join(failures))
        sys.exit(1)
    reg_where, profile, register = registers[REGISTER]
    tz = ZoneInfo(register["timeZone"])
    _, pack = packs[(register["pack"]["code"], register["pack"]["version"])]
    types = {t["code"]: t for t in pack["filingTypes"]}
    schemes = {s["code"]: s for s in pack["identifierSchemes"]}
    classes = {c["code"]: c for c in pack.get("entitlementClasses") or []}
    retention = register.get("retentionClasses") or []
    tenancies = register.get("tenancies") or core["defaults"].get("tenancies") or []
    for t in types:
        if not any(r["appliesTo"] == "filing-type" and t in r["types"] for r in retention):
            fail(reg_where, f"filing type {t} has no retention class", "REG-090")

    # Parties (REG-061, DMO-040).
    parties_path = os.path.join(ex, "parties.json")
    parties_doc = load(parties_path)
    model.check(parties_doc, "PartyContainer", rel(parties_path))
    parties = {p["id"] for lst in ("persons", "organizations") for p in parties_doc.get(lst) or []}

    def date_of(t):
        return instant(t).astimezone(tz).date().isoformat()

    def check_identifier(ident, where, path, scheme=None):
        s = schemes.get(ident.get("scheme"))
        if s is None:
            fail(where, f"{path} uses scheme {ident.get('scheme')}, which the pack does not declare", "REG-051")
            return
        if scheme and ident["scheme"] != scheme:
            fail(where, f"{path} must use scheme {scheme}", "REG-051")
        if ident.get("searchKey") != normalize(ident.get("value", ""), s["normalization"]):
            fail(where, f"{path} has a search key that is not the normalized value", "REG-051")

    # Filings (REG-020 to REG-033).
    filings, files = {}, {}
    for p in sorted(glob.glob(os.path.join(ex, "filings", "*.json"))):
        f = load(p)
        model.check(f, "Filing", rel(p))
        if f.get("id") in filings:
            fail(rel(p), f"filing id {f.get('id')} is used twice", "REG-021")
        filings[f.get("id")] = f
        files[f.get("id")] = rel(p)
    chain_doc = load(os.path.join(ex, "chain.json"))
    model.check(chain_doc, "RegistryContainer", "examples/pleasure-craft/chain.json")
    tombstones = {t["filingId"]: t for t in chain_doc.get("tombstones") or []}
    salts = load(os.path.join(ex, "salts.json"))
    all_by_id = {**{k: v for k, v in filings.items()}, **tombstones}

    for fid, f in filings.items():
        where = files[fid]
        if f.get("registerCode") != REGISTER:
            fail(where, f"register {f.get('registerCode')} is not declared", "REG-010")
        t = types.get(f.get("filingType"))
        if t is None:
            fail(where, f"filing type {f.get('filingType')} is not in the catalog of the pack", "REG-021")
            continue
        if f.get("category") != t["category"]:
            fail(where, f"category must be {t['category']}, as the catalog says", "REG-021")
        final = f.get("processingStatus") in FINAL
        if final and ("completedAt" not in f or "sequence" not in f):
            fail(where, "a filing with a final status needs completedAt and a sequence", "REG-023, REG-030")
        if f.get("completedAt", f["submittedAt"]) < f["submittedAt"]:
            fail(where, "completedAt comes before submittedAt", "REG-023")
        if final and f.get("updatedAt") != f.get("completedAt"):
            fail(where, "updatedAt must be the completion: nothing changes after a final status", "REG-022")
        if not t["retroactive"] and f["effectiveAt"] < f["submittedAt"]:
            fail(where, f"filing type {t['code']} takes no effective instant before submission", "REG-023")
        if f.get("paymentStatus") not in pack["paymentStatuses"] or f.get("reviewStatus") not in pack["reviewStatuses"]:
            fail(where, "the payment and review statuses come from the lists of the pack", "REG-024")
        a = f.get("authority") or {}
        need = {"representation": ["representationId"], "statutory-power": ["legalSource"],
                "order": ["legalSource", "orderReference"]}.get(a.get("kind"), [])
        for k in need:
            if k not in a:
                fail(where, f"authority {a.get('kind')} needs {k}", "REG-025")
        for pid in [f.get("onBehalfOfPartyId")] + [x["partyId"] for x in f.get("parties") or []]:
            if pid not in parties:
                fail(where, f"party {pid} is not a Party of parties.json", "REG-061")
        for x in f.get("parties") or []:
            if x["role"] not in pack["partyRoles"]:
                fail(where, f"party role {x['role']} is not in the pack", "REG-025")
        cat = f.get("category")
        if cat == "correction":
            target = all_by_id.get(f.get("corrects"))
            if target is None or target.get("sequence", 0) >= f.get("sequence", 0):
                fail(where, f"the corrected filing {f.get('corrects')} must be an earlier filing", "REG-027")
            if "changes" not in f:
                fail(where, "a correction carries the full corrected changes", "REG-027")
        elif "corrects" in f:
            fail(where, "only a correction names a corrected filing", "REG-027")
        if cat == "destruction":
            for k in ("destroys", "legalBasis", "legalHoldCheckedAt"):
                if k not in f:
                    fail(where, f"a destruction filing needs {k}", "REG-093")
            if "changes" in f:
                fail(where, "a destruction filing changes no row", "REG-093")
            if f.get("legalHoldCheckedAt", "") > f.get("completedAt", ""):
                fail(where, "the legal hold check must come before completion", "REG-093")
        elif "destroys" in f:
            fail(where, "only a destruction filing destroys filings", "REG-093")
        # The catalog of the corrected filing governs the rows of a correction.
        rule_type = t
        if cat == "correction" and f.get("corrects") in all_by_id:
            rule_type = types.get(all_by_id[f["corrects"]]["filingType"], t)
        changes = f.get("changes") or {}
        for ref in changes.get("ends") or []:
            if ref["kind"] not in (rule_type.get("mayEnd") or []):
                fail(where, f"filing type {rule_type['code']} may not end a row of kind {ref['kind']}", "REG-029")
        for kind, lst in KIND_LIST.items():
            for i, row in enumerate((changes.get("opens") or {}).get(lst) or []):
                path = f"$.changes.opens.{lst}[{i}]"
                if kind not in (rule_type.get("mayOpen") or []):
                    fail(where, f"filing type {rule_type['code']} may not open a row of kind {kind}", "REG-029")
                if HISTORY & set(row):
                    fail(where, f"{path} holds history slots, which only the replay adds", "REG-041")
                if kind == "asset":
                    for j, ident in enumerate(row.get("identifiers") or []):
                        check_identifier(ident, where, f"{path}.identifiers[{j}]")
                if kind == "owner-group":
                    if row["tenancy"] not in tenancies:
                        fail(where, f"{path}: tenancy {row['tenancy']} is not a code of the profile", "REG-053")
                    n, d, members = row["interest"]["numerator"], row["interest"]["denominator"], row["members"]
                    if row["tenancy"] == "sole" and (len(members) != 1 or n != d):
                        fail(where, f"{path}: a sole group has one member and the whole asset", "REG-053")
                    if row["tenancy"] == "joint" and (len(members) < 2 or n != d):
                        fail(where, f"{path}: a joint group has two or more members and the whole asset", "REG-053")
                    if row["tenancy"] == "in-common" and n >= d:
                        fail(where, f"{path}: a group in common holds less than the whole asset", "REG-053")
                if kind == "entitlement":
                    ec = classes.get(row["entitlementClass"])
                    if ec is None:
                        fail(where, f"{path} has an unknown entitlement class", "REG-058")
                        continue
                    check_identifier(row["number"], where, f"{path}.number", ec["numberScheme"])
                    if row["lifecycleState"] not in ec["actStates"]:
                        fail(where, f"{path} sets {row['lifecycleState']}, which is not an act-driven state", "REG-045")
                    for term in register.get("terms") or []:
                        day = date_of(f[COUNT_FROM[term.get("countFrom", "effective-date")]])
                        if term["entitlementClass"] == ec["code"] and rule_type["code"] in term["startsWith"] \
                                and in_force(term, day):
                            want = {"start": day, "end": add_period(dt.date.fromisoformat(day), term["term"]).isoformat()}
                            if row["validity"] != want:
                                fail(where, f"{path}.validity must be {want['start']} to {want['end']}, from the "
                                     f"term of the profile", "REG-058, REG-014")
        if t.get("transferCauses") and f.get("transferCause") not in t["transferCauses"]:
            fail(where, f"a transfer of type {t['code']} states one of the causes {t['transferCauses']}", "REG-055")
        deadline = [d for d in register.get("deadlines") or []
                    if d["filingType"] == t["code"] and in_force(d, date_of(f["effectiveAt"]))]
        if deadline:
            start = f[COUNT_FROM[deadline[0].get("countFrom", "effective-date")]]
            limit = add_period(instant(start).astimezone(tz).date(), deadline[0]["within"])
            want = "met" if instant(f["submittedAt"]).astimezone(tz).date() <= limit else "missed"
            if f.get("deadlineStatus") != want:
                fail(where, f"deadlineStatus must be {want}, from the deadline of the profile", "REG-033")
            if want == "missed" and f.get("processingStatus") == "rejected" and not deadline[0]["lateFilingBarred"]:
                fail(where, "the profile bars no late filing, so lateness alone cannot reject it", "REG-033")
        elif "deadlineStatus" in f:
            fail(where, "no deadline of the profile applies to this filing", "REG-033")
        for e in f.get("evidence") or []:
            if e["evidenceType"] not in (pack.get("evidenceTypes") or []):
                fail(where, f"evidence type {e['evidenceType']} is not in the pack", "REG-092")
            if not any(r["code"] == e["retentionClass"] and r["appliesTo"] == "evidence-type"
                       and e["evidenceType"] in r["types"] for r in retention):
                fail(where, f"evidence {e['documentId']} names no retention class of the profile for its type", "REG-090")

    # Retroactive filings restate the later versions that they affect (REG-029).
    def opened_ids(x):
        return {(kind, row["id"]) for kind, lst in KIND_LIST.items()
                for row in ((x.get("changes") or {}).get("opens") or {}).get(lst) or []}

    for xid, x in filings.items():
        if x.get("processingStatus") != "completed" or x.get("category") == "destruction":
            continue
        restates = {(r["filingId"], kind, row["id"]) for r in (x.get("changes") or {}).get("restates") or []
                    for kind, lst in KIND_LIST.items() for row in (r.get("opens") or {}).get(lst) or []}
        for yid, y in filings.items():
            if yid == xid or y.get("processingStatus") != "completed" or y.get("category") == "destruction":
                continue
            if not (y["completedAt"] < x["completedAt"] and y["effectiveAt"] > x["effectiveAt"]):
                continue
            for kind, eid in opened_ids(x) & opened_ids(y):
                if (yid, kind, eid) not in restates:
                    fail(files[xid], f"the filing takes effect before filing {yid}, which completed first; it must "
                         f"restate the {kind} {eid} that filing {yid} opened", "REG-029")

    # Light chain and destruction (REG-030, REG-031, REG-093 to REG-095).
    entries = {e["sequence"]: e for e in chain_doc.get("chainEntries") or []}
    if sorted(entries) != list(range(1, len(entries) + 1)):
        fail("examples/pleasure-craft/chain.json", "sequences must run from 1 with no gap", "REG-030")
    seq_of = {}
    for fid, x in all_by_id.items():
        if x.get("processingStatus", "completed") in FINAL:
            seq_of[x["sequence"]] = fid
    for seq, e in sorted(entries.items()):
        where = "examples/pleasure-craft/chain.json"
        if seq_of.get(seq) != e["filingId"]:
            fail(where, f"chain entry {seq} names filing {e['filingId']}, which does not hold that sequence", "REG-030")
            continue
        x = all_by_id[e["filingId"]]
        prev = x.get("previousCommitment")
        if seq == 1 and prev is not None:
            fail(where, "the first filing has no previous commitment", "REG-030")
        if seq > 1 and (seq - 1 not in entries or prev != entries[seq - 1]["commitment"]):
            fail(files.get(e["filingId"], where), f"previousCommitment of sequence {seq} is not the commitment of "
                 f"sequence {seq - 1}", "REG-030")
        if e["filingId"] in tombstones:
            if tombstones[e["filingId"]]["commitment"] != e["commitment"]:
                fail(where, f"the tombstone of sequence {seq} keeps another commitment", "REG-094")
            continue
        salt = salts.get(e["filingId"])
        if salt is None:
            fail(where, f"the salt of filing {e['filingId']} is missing", "REG-031")
        elif commitment(salt, x) != e["commitment"]:
            fail(files[e["filingId"]], f"the commitment of sequence {seq} does not match the filing and its salt",
                 "REG-031, REG-022")
    for fid, x in all_by_id.items():
        if x.get("processingStatus", "completed") in FINAL and x.get("sequence") not in entries:
            fail(files.get(fid, "chain.json"), f"filing {fid} has a final status but no chain entry", "REG-030")
    destroyed_by = {}
    for fid, f in filings.items():
        for d in f.get("destroys") or []:
            destroyed_by[d] = fid
    for d, by in destroyed_by.items():
        if d in filings or d in salts:
            fail(files[by], f"filing {d} must have its content and its salt destroyed together", "REG-093, LOG-081")
        if d not in tombstones:
            fail(files[by], f"filing {d} must leave a tombstone", "REG-094")
    for did, d in filings.items():
        if d.get("category") != "destruction":
            continue
        retained = {r["filingId"] for r in d.get("retainedFilings") or []}
        for target in d.get("destructionTargets") or []:
            for xid, x in filings.items():
                if xid == did or xid in retained:
                    continue
                if any(v == target["id"] for _, v in leaves(x)):
                    fail(files[xid], f"filing {xid} still holds the value {target['id']} that destruction filing "
                         f"{did} targets: destroy it or list it as retained", "REG-093")
    for fid, t in tombstones.items():
        if t["category"] == "correction" and not t.get("corrects"):
            fail("examples/pleasure-craft/chain.json", f"the tombstone of correction {fid} must keep the corrected "
                 "filing", "REG-094")
        if destroyed_by.get(fid) != t["destroyedByFiling"]:
            fail("examples/pleasure-craft/chain.json", f"tombstone {fid} must name the destruction filing that "
                 "lists it", "REG-094")

    # The log series of the register (REG-031, REG-032).
    log_path = os.path.join(ex, "log.json")
    log_doc = load(log_path)
    model.check(log_doc, "RegistryContainer", rel(log_path))
    where = rel(log_path)
    shards = log_doc.get("logShards") or []
    all_leaves = [(sh["origin"], i, leaf) for sh in shards for i, leaf in enumerate(sh["leaves"])]
    chain_commits = [entries[q]["commitment"] for q in sorted(entries)]
    leaf_values = [leaf for _, _, leaf in all_leaves]
    for q in sorted(entries):
        if entries[q]["commitment"] not in leaf_values:
            fail(where, f"chain entry {q} has no leaf in the log series of the register", "REG-032")
    for origin, i, leaf in all_leaves:
        if leaf not in chain_commits:
            fail(where, f"leaf {i} of shard {origin} matches no chain entry or tombstone", "REG-032")
    if sorted(leaf_values) == sorted(chain_commits) and leaf_values != chain_commits:
        fail(where, "the log indexes must increase with the sequence", "REG-032")
    for sh in shards:
        sizes = [c["treeSize"] for c in sh["checkpoints"]]
        if sizes != sorted(sizes) or sizes[-1] > len(sh["leaves"]):
            fail(where, f"the checkpoints of shard {sh['origin']} must grow and cover only its leaves", "REG-032, LOG-061")
        for c in sh["checkpoints"]:
            if c["treeSize"] <= len(sh["leaves"]) and mth(sh["leaves"][:c["treeSize"]]).hex() != c["rootHash"]:
                fail(where, f"checkpoint {c['treeSize']} of shard {sh['origin']} does not match the leaves",
                     "REG-032, OBS-115")
        if sizes[-1] != len(sh["leaves"]):
            fail(where, f"the newest checkpoint of shard {sh['origin']} must cover every leaf", "REG-032")
    if shards and chain_commits and shards[-1]["leaves"][-1] != chain_commits[-1]:
        fail(where, "the head of the chain must be the last leaf of the newest checkpoint", "REG-032")

    # Replay against the expected snapshots (REG-040, REG-042, REG-053, REG-095).
    snaps_path = os.path.join(ex, "snapshots.json")
    snaps_doc = load(snaps_path)
    model.check(snaps_doc, "RegistryContainer", rel(snaps_path))

    def ordered(s):
        out = dict(s)
        for k in ("assets", "ownerGroups", "entitlements", "encumbrances", "destroyedRows"):
            if k in out:
                out[k] = sorted(out[k], key=lambda r: json.dumps(r, sort_keys=True))
        return json.loads(json.dumps(out, sort_keys=True))

    for i, s in enumerate(snaps_doc.get("snapshots") or []):
        got = replay(filings, tombstones, s["validAt"], s["recordedAt"], pack, tz)
        if ordered(got) != ordered(s):
            fail(rel(snaps_path), f"snapshot {i} as of {s['validAt']} recorded at {s['recordedAt']} does not match "
                 "the replay of the filings", "REG-040, REG-042")
        shares = {}
        for g in got.get("ownerGroups") or []:
            n, d = g["interest"]["numerator"], g["interest"]["denominator"]
            shares.setdefault(g["assetId"], []).append((n, d))
        for asset, parts in shares.items():
            total = sum(Fraction(n, d) for n, d in parts)
            if total != 1:
                fail(rel(snaps_path), f"snapshot {i}: the owner groups of asset {asset} hold {total}, not the whole",
                     "REG-053")

    # Views (REG-012, REG-070 to REG-076, REG-082, REG-084).
    views_path = os.path.join(ex, "views.json")
    views = load(views_path)
    model.check(views, "RegistryContainer", rel(views_path))
    extracts = {x["id"]: x for x in views.get("extracts") or []}
    policies = {a["code"]: a for a in register.get("accessPolicies") or []}
    for x in extracts.values():
        where = f"{rel(views_path)} extract {x['id']}"
        snap = replay(filings, tombstones, x["validAt"], x["recordedAt"], pack, tz)
        if x.get("subjects") and (x["lastFilingSequence"] != snap["lastFilingSequence"] or
                                  x.get("lastFilingId") != seq_of.get(snap["lastFilingSequence"])):
            fail(where, "the extract must state the last filing that it reflects", "REG-084")
        rank = VISIBILITY.index(x["view"])
        if rank > 0:
            pol = policies.get(x.get("accessPolicy"))
            if pol is None or VISIBILITY.index(pol["grants"]) < rank:
                fail(where, f"a {x['view']} view needs an access policy of the profile that grants it", "REG-074")
        if register["publicityRegime"] == "closed" and x["view"] == "public" and \
                (x.get("fields") or x.get("subjects") or x.get("lastFilingId")):
            fail(where, "a public view of a closed register shows no field and neither confirms nor denies a "
                 "record", "REG-012")
        elif not x.get("subjects") and not (register["publicityRegime"] == "closed" and x["view"] == "public"):
            fail(where, "the extract must state its subjects", "REG-084")
        for fld in x.get("fields") or []:
            vis, _, _ = effective_policy(fld["path"], register, pack, core, find_row(snap, fld["entityId"]))
            if VISIBILITY.index(vis) > rank:
                fail(where, f"field {fld['path']} is {vis} under the profile, so a {x['view']} view cannot show it",
                     "REG-070")
            vals = field_value(snap, fld["path"], fld["entityId"])
            if vals is None or fld["value"] not in vals:
                fail(where, f"field {fld['path']} does not hold the replayed value", "REG-084")
        for o in x.get("omissions") or []:
            vis, _, reason = effective_policy(o["path"], register, pack, core)
            if VISIBILITY.index(vis) <= rank:
                fail(where, f"field {o['path']} is visible to a {x['view']} view and cannot be omitted", "REG-073")
            if o["reason"] != reason and o["reason"] not in ("destroyed", "unknown-to-register"):
                fail(where, f"the omission of {o['path']} must give the reason {reason}", "REG-073")
    # A view of a register whose pack is planned, with the record it shows (REG-071).
    qc_path = os.path.join(root, "examples", "ca-qc", "beneficiary-views.json")
    qc_doc = load(qc_path)
    qc_records = {r["id"]: r for r in qc_doc.get("records") or []}
    model.check({"extracts": qc_doc.get("extracts") or []}, "RegistryContainer", rel(qc_path))
    for x in qc_doc.get("extracts") or []:
        qwhere = f"{rel(qc_path)} extract {x['id']}"
        _, _, qreg = registers.get(x["registerCode"], (None, None, None))
        if qreg is None:
            fail(qwhere, f"register {x['registerCode']} is not declared", "REG-010")
            continue
        rank = VISIBILITY.index(x["view"])
        for fld in x.get("fields") or []:
            rec = qc_records.get(fld["entityId"])
            vis, _, _ = effective_policy(fld["path"], qreg, {}, core, rec)
            if VISIBILITY.index(vis) > rank:
                fail(qwhere, f"field {fld['path']} is {vis} for this record, so a {x['view']} view cannot show it",
                     "REG-070, REG-071")
            if rec is None or rec.get(fld["path"].split(".")[-1]) != fld["value"]:
                fail(qwhere, f"field {fld['path']} does not hold the value of the record", "REG-084")
        for o in x.get("omissions") or []:
            recs = [qc_records.get(f["entityId"]) for f in x.get("fields") or []]
            vis, _, reason = effective_policy(o["path"], qreg, {}, core, recs[0] if recs else None)
            if o["reason"] != reason:
                fail(qwhere, f"the omission of {o['path']} must give the reason {reason}", "REG-073")

    modes = {m["code"]: m for m in register.get("searchModes") or []}
    for s in views.get("searchRecords") or []:
        where = f"{rel(views_path)} search {s['id']}"
        m = modes.get(s["mode"])
        if m is None:
            fail(where, f"search mode {s['mode']} is not in the profile", "REG-080")
            continue
        for k in s["keys"]:
            if k["scheme"] not in m["keys"]:
                fail(where, f"key {k['scheme']} is not a key of the mode", "REG-080")
            elif k["scheme"] in schemes:
                check_identifier(k, where, "$.keys")
        snap = replay(filings, tombstones, s["executedAt"], s["executedAt"], pack, tz)
        if s["lastFilingSequence"] != snap["lastFilingSequence"]:
            fail(where, "the search record must state the last filing that its result reflects", "REG-082")
        if s["certified"] and s.get("extractId") not in extracts:
            fail(where, "a certified result names its sealed extract", "REG-082")

    # Event schemas (API-103) and events (REG-102, REG-103).
    ev_schemas = {}
    for p in sorted(glob.glob(os.path.join(root, "registry", "events", "*.schema.json"))):
        s = load(p)
        t = os.path.basename(p)[:-len(".schema.json")]
        if s.get("title") != t or not s.get("$id", "").endswith("/" + os.path.basename(p)):
            fail(rel(p), "the title and the $id must name the event type of the file", "API-103")
        if not re.match(r"^org\.fpsot\.registry\.[a-z]+(-[a-z]+)*\.[a-z]+$", t):
            fail(rel(p), f"{t} is not of the form org.fpsot.registry.<resource>.<event>", "NAM-050")
        ev_schemas[t] = s
    personal = set(parties)
    for f in filings.values():
        for lst in KIND_LIST.values():
            for row in ((f.get("changes") or {}).get("opens") or {}).get(lst) or []:
                for ident in (row.get("identifiers") or []) + ([row["number"]] if "number" in row else []):
                    personal |= {ident["value"], ident["searchKey"]}
    for p in sorted(glob.glob(os.path.join(ex, "events", "*.json"))):
        e, where = load(p), rel(p)
        for attr, want in (("specversion", "1.0"), ("datacontenttype", "application/json")):
            if e.get(attr) != want:
                fail(where, f"{attr} must be {want}", "API-101")
        for attr in ("id", "source", "type", "time"):
            if not e.get(attr):
                fail(where, f"the attribute {attr} is required", "API-101")
        if e.get("type") not in ev_schemas:
            fail(where, f"event type {e.get('type')} has no schema in registry/events/", "API-103")
            continue
        json_schema(e.get("data"), ev_schemas[e["type"]], where, "$.data")
        for path, v in leaves(e):
            if isinstance(v, str) and v in personal:
                fail(where, f"{path} holds a party id or an identifier value: events hold no personal value", "REG-103")
        data = e.get("data") or {}
        f = filings.get(data.get("filingId"))
        if f is None:
            fail(where, "the event names a filing that the register holds", "REG-102")
            continue
        if e["type"].endswith(".filing.recorded"):
            for k in ("filingType", "category", "sequence", "processingStatus", "effectiveAt", "completedAt"):
                if data.get(k) != f.get(k):
                    fail(where, f"data.{k} must match the filing", "REG-102")
        if e["type"].endswith(".state.changed"):
            changes = f.get("changes") or {}
            want = {("ended", r["kind"], r["entityId"]) for r in changes.get("ends") or []}
            for kind, lst in KIND_LIST.items():
                want |= {("opened", kind, r["id"]) for r in (changes.get("opens") or {}).get(lst) or []}
            got = {(r["change"], r["kind"], r["entityId"]) for r in data.get("rows") or []}
            if got != want:
                fail(where, "data.rows must list the rows that the filing opened and ended", "REG-102")

    # Features (REG-105, TST-030 to TST-032).
    en_files = sorted(glob.glob(os.path.join(root, "examples", "features", "en", "*.feature")))
    if not en_files:
        fail("examples/features", "no feature file", "REG-105")
    for en in en_files:
        fr = en.replace(os.sep + "en" + os.sep, os.sep + "fr" + os.sep)
        if not os.path.exists(fr):
            fail(rel(en), "the French feature file is missing", "TST-030")
            continue
        (en_head, en_sc), (fr_head, fr_sc) = gherkin(en), gherkin(fr)
        if en_head != "# language: en" or fr_head != "# language: fr":
            fail(rel(en), "the first lines must be # language: en and # language: fr", "TST-031")
        if [s["tags"] for s in en_sc] != [s["tags"] for s in fr_sc] or \
                [len(s["steps"]) for s in en_sc] != [len(s["steps"]) for s in fr_sc]:
            fail(rel(en), "the English and French scenarios must have the same tags and steps", "TST-032")
        for path, sc_list in ((en, en_sc), (fr, fr_sc)):
            for s in sc_list:
                text = "\n".join(s["steps"])
                tag = s["tags"][0] if s["tags"] else "(no tag)"
                if not s["tags"]:
                    fail(rel(path), "each scenario needs a tag", "TST-027")
                if not re.search(r'"\d{4}-\d{2}-\d{2}', text):
                    fail(rel(path), f"scenario {tag} states no date", "REG-105")
                named = re.findall(r'(?:filing|déclaration) "([a-z0-9-]+)"', text)
                if not named:
                    fail(rel(path), f"scenario {tag} names no filing type", "REG-105")
                for code in named:
                    if code not in types:
                        fail(rel(path), f"scenario {tag} names filing type {code}, which the pack does not declare",
                             "REG-021")

    for f in failures:
        print(f)
    if failures:
        sys.exit(1)
    print(f"PASS: filings {len(filings)}, tombstones {len(tombstones)}, chain entries {len(entries)}, "
          f"snapshots {len(snaps_doc.get('snapshots') or [])}, extracts {len(extracts)}, "
          f"profiles {len(profiles)}, packs {len(packs)}, feature pairs {len(en_files)}")


def leaves(v, path="$"):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from leaves(x, f"{path}.{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from leaves(x, f"{path}[{i}]")
    else:
        yield path, v


def json_schema(v, s, where, path="$"):
    """The parts of JSON Schema 2020-12 that the event schemas use."""
    t = s.get("type")
    kinds = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int}
    if t in kinds and (not isinstance(v, kinds[t]) or (t != "boolean" and isinstance(v, bool))):
        fail(where, f"{path} must be of type {t}", "API-103")
        return
    if "enum" in s and v not in s["enum"]:
        fail(where, f"{path} has {v!r}, which is not in the schema enumeration", "API-103")
    if isinstance(v, str) and "pattern" in s and not re.search(s["pattern"], v):
        fail(where, f"{path} has {v!r}, which does not match its schema pattern", "API-103")
    if isinstance(v, int) and not isinstance(v, bool) and v < s.get("minimum", v):
        fail(where, f"{path} is below its schema minimum", "API-103")
    if isinstance(v, list):
        if len(v) < s.get("minItems", 0):
            fail(where, f"{path} has too few items", "API-103")
        for i, x in enumerate(v):
            json_schema(x, s.get("items", {}), where, f"{path}[{i}]")
    if isinstance(v, dict):
        for k in s.get("required", []):
            if k not in v:
                fail(where, f"{path}.{k} is required by the event schema", "API-103")
        props = s.get("properties", {})
        for k, x in v.items():
            if k in props:
                json_schema(x, props[k], where, f"{path}.{k}")
            elif s.get("additionalProperties") is False:
                fail(where, f"{path}.{k} is not allowed by the event schema", "API-103")


if __name__ == "__main__":
    main()
