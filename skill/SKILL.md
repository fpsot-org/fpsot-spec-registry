---
name: fpsot-registry
description: Registry rules for FPSOT software. Use when writing or reviewing code that keeps a register of assets, ownership and entitlements under a law, such as licenses, vehicle or vessel registrations, permits or business registers; that stores or replays filings, corrects or destroys them, derives bitemporal state, writes jurisdiction profiles or domain packs, serves register views, searches or extracts, or emits register events.
---

# FPSOT registry

Summary of the FPSOT registry specification. It adds no rules of its own.
The spec text in `spec/` wins on any difference. Each line cites its requirement ID.
It standardizes the filing and what can be derived from it; everything that varies by law lives in jurisdiction profiles.
The model is `model/registry.yaml` with pack schemas such as `model/pleasure-craft.yaml`; profiles are in `profiles/`, packs in `packs/`; `examples/check-examples.py` checks the examples and replays the filings.

Each line keeps the strength of its rule: "must" and "must not" are MUST and MUST NOT, "should" and "should not" are SHOULD and SHOULD NOT, "may" is MAY.

Other specs own the party (DMO), representation and authorization (IAM), data types (DAT), eligibility and fees as decisions (DEC), code lists (VOC), seals and the transparency log (LOG), audit events and their retention (OBS), APIs and events (API), scenarios and synthetic data (TST). Cite them; never redefine them (REG-004).

## Scope, roles and legal status

- Applies to software that keeps a register under a law, any domain, any storage; intake, fees and case work are out of scope (REG-001).
- State your conformance classes: `core`, `pack`, `profile`, `publication` (REG-002).
- Never claim that a register meets a law or that an extract carries a legal presumption; legal points go to profiles, comparison data and Questions for counsel (REG-003).
- Follow the pinned versions (REG-005); suites check output only, under TST-044 (REG-006).

## Profiles

- Declare each register in a profile: legal instruments, legal effect, publicity regime, pack, seal profile, time zone; no declaration, no filing (REG-010).
- Legal effect is `administrative-identification`, `notice-opposability` or `title`, with a source; this release declares no `title` (REG-011).
- Publicity regime is `public`, `public-with-exceptions`, `gated` or `closed`; a closed register makes no field public, opens no search to the public, and its public view shows no field (REG-012).
- Profiles are `Profile` files with sources marked `read` or `to-be-verified`; every parameter cites a source (REG-013).
- Profiles have their own SemVer; terms and deadlines carry effective dates; a filing uses the value in force on its effective date (REG-014).
- No law in the core or the pack: never hard-code a term, deadline, visibility, opposability, retention period or search mode (REG-015).
- Follow `core` defaults (`restricted`, not opposable, `seal-log`); refuse to complete a filing when a needed parameter is missing, never assume one (REG-016).

## Filings

- Every state change comes from exactly one completed filing, staff, migration, correction, order and destruction included (REG-020).
- Filings are `Filing` records; type from the pack catalog; category `change`, `correction` or `destruction` (REG-021).
- Never change a filing's content; until a final status only the three statuses, `completedAt`, `sequence` and `previousCommitment` may change; after it, nothing (REG-022).
- Three instants: `submittedAt`, `effectiveAt`, `completedAt`; future-effective changes nothing before `effectiveAt`; `effectiveAt` before `submittedAt` only for retroactive types (REG-023).
- Three separate statuses: payment and review from pack lists; processing `received`, `in-progress`, `completed`, `rejected`, `withdrawn`; only `completed` changes state (REG-024).
- Record the actor (opaque id), the represented `Party`, and the authority: `own-behalf`, `representation` (IAM-061 id), `statutory-power` or `order`; check it under IAM-050 and IAM-064 (REG-025).
- Eligibility, fees, exemptions and penalties are DEC decisions; the filing names the decision record ids (REG-026).
- A correction names an earlier filing, carries the full corrected changes and effective instant, and replaces it for later record times; the original stays retrievable (REG-027).
- Court and registrar orders are filings with authority `order` or `statutory-power` (REG-028).
- A completed filing states each row it opens (full values) and ends (kind and id); the catalog lists allowed kinds; replay applies them and never reruns rules (REG-029).
- Light chain: contiguous `sequence` per register from 1; `previousCommitment` holds the commitment of the filing before; complete one at a time (REG-030).
- Seal and log each final filing under LOG; its commitment is its LOG-031 salted hash; at least `seal-log`, `seal-log-preserve` when kept forever; no own signature, checkpoint or witness (REG-031).
- A verifier checks contiguity, links, recomputed commitments, tombstones and log inclusion, and reports each result apart (REG-032).
- Deadlines are dated profile data; record `deadlineStatus`; never reject a late filing unless the profile cites a provision that bars it (REG-033).

## Derived state

- Every view equals a replay of completed filings, by effective instant then sequence, with corrections in place of what they correct (REG-040).
- Each row is a version with `createdByFiling`, `validFrom`, and `endedByFiling`, `validTo` once ended; filings never hold these slots (REG-041).
- Answer "as of V, as recorded at T" from filings completed at or before T, as a `StateSnapshot` with the highest sequence (REG-042).
- Stored views are rebuildable projections; on a difference, the replay wins and it is an incident (REG-043).
- No deletion except through a destruction filing; never delete because a period ended (REG-044).
- Lifecycles are pack data; each transition names its filing type or scheduled event; time-driven states (`expired`, `lapsed`) come from dates, act-driven ones only from filings (REG-045).
- Legacy records enter through migration filings that name their source; law-set end dates are profile data and the migration filing opens each entitlement with that end (REG-046).

## Assets, ownership, entitlements, encumbrances

- Assets are `Asset` or a pack subclass in the pack's LinkML schema, which imports `model/registry.yaml`; name the kind in `assetKind` (REG-050).
- Identifier schemes are VOC concepts declared by the pack with issuer, check digit, uniqueness scope, normalization and format when read; keep the issuer form plus a normalized `searchKey` (REG-051).
- Links between assets are typed, never free text (REG-052).
- Ownership is the set of current `OwnerGroup` rows: `sole`, `joint` or `in-common` with a fraction; interests add up to exactly one (REG-053).
- A transfer ends groups and opens new ones, never edits members in place (REG-054).
- Transfer types list their causes (`sale`, `death`, `court-order`, `operation-of-law`); each transfer states one; its evidence is `restricted` by default (REG-055).
- Ownership and entitlement never imply each other (REG-056).
- `Entitlement`: class, number, validity as dates in the register's time zone, party roles, covered assets, coded conditions (REG-057).
- Terms are profile data counted from the date of the effective instant; lifecycles are pack data (REG-058).
- Liens, seizures, stop orders and flags should be `Encumbrance` rows with their own filings and term (REG-059).
- Rights kept in another register are declared in the profile with their search keys and never copied (REG-060).
- Every party is a DMO `Party` by id; no local person or organization records; roles are pack codes (REG-061).

## Visibility, opposability and access

- Each field has a class: `public`, `parties`, `agency`, `restricted`; pack default, profile override; never show a field narrower than the view (REG-070).
- A class may depend on another field of the same record, with a class for each case (REG-071).
- Opposability is a separate per-field flag set by the profile; never derive one from the other (REG-072).
- Each omission carries `not-public-by-law`, `withheld-on-application`, `unknown-to-register` or `destroyed` (REG-073).
- A view wider than public rests on a role in the record or an access policy with basis, recipients, purpose, widest class, expiry and logging duty; per-request grants should be entitlements (REG-074).
- Ask the authorization engine on every view request and deny by default; profile policies feed the engine (REG-075).
- Each personal-data read, search, extract or export is an OBS-042 audit event with the policy code as purpose (REG-076).
- Should let a data subject list the reads of their data (REG-077).

## Search, extracts and credentials

- Search modes are profile data with keys, matching and allowed views, dated when the law dates them; offer no other search (REG-080).
- Matching is `exact`, `normalized` (scheme steps) or `similar` with a stated algorithm and threshold (REG-081).
- Keep a `SearchRecord` with mode, keys, instant and highest sequence; certified results are sealed extracts named in the record (REG-082).
- Searches on personal data use `POST` on `searches` (API-049) and respect visibility (REG-083).
- Extracts are `Extract` records with register, subject, both instants, last filing, view, policy and omissions; values equal the replay; seal and log them (REG-084).
- Extract layout should be profile data; legal weight never appears in a rule (REG-085).
- Should also issue entitlements as VC 2.0 with Bitstring Status List driven by lifecycle filings; may do so for extracts; no wallet protocol (REG-086).
- Business packs should export BODS 0.4 and map to CBV 2.2.0 (REG-087).

## Retention and destruction

- Each filing type and evidence type has a profile retention class naming its schedule rule; legal holds stop destruction (REG-090).
- Never cut a filing's life to that of its events (REG-091).
- Filings hold evidence references with SHA-256 and a retention class; evidence may go on schedule with an OBS-104 event (REG-092).
- Destroy a filing only through a destruction filing with basis, targets, authority, legal hold check and prior copies; destroy content and salt together in every copy (LOG-081); emit OBS-104 (REG-093).
- Leave a `Tombstone` with sequence, type, category, instants, commitment, previous commitment and row ids only (REG-094).
- After destruction the chain still verifies and replay still works; rows that only destroyed content supports show as destroyed rows, never guessed (REG-095).
- Copies made before a destruction are recorded in the destruction filing and are disclosures (REG-096).

## Packs, events and conformance

- A pack holds its LinkML schema, `DomainPack` data (asset kinds, schemes, filing catalog), lifecycles, statuses, roles, evidence types, field defaults and replay fixtures (REG-100).
- Packs have their own SemVer, never redefine core or Party classes, hold no law (REG-101).
- Emit business events and CloudEvents `org.fpsot.registry.filing.recorded` and `org.fpsot.registry.state.changed`, schemas in `registry/events/` (REG-102).
- Events hold no party id, name, address, amount or identifier value; only ids of filings and rows, codes and instants (REG-103).
- Create filings with `POST` and `Idempotency-Key`; no operation edits or deletes a filing; withdrawal is a status change before completion (REG-104).
- Pack suites hold replay fixtures (ordered filings, chain, expected snapshots) and EN/FR scenarios that state dates and name filing types (REG-105).
- Synthetic data only, fictional parties, documentation domains, no real identifiers (REG-106).
- May offer a GovStack Digital Registries adapter mapped requirement by requirement (REG-107).
- A replacement engine passes the same replay fixtures (REG-108).
