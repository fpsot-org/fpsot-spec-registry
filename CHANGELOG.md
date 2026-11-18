# Changelog

All notable changes to this specification are listed here.
The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-18

### Added

- Scope, conformance classes, legal status, owners of the parts and conformance REG-001 to REG-006: any register under a law, any domain and storage; the classes `core`, `pack`, `profile` and `publication`; no claim of legal compliance or presumption; each part taken from the specification that owns it; pinned versions; suites that check output only.
- Jurisdiction profiles REG-010 to REG-016: a declaration for each register with its legal instruments, legal effect, publicity regime, pack, seal profile and time zone; three legal effects, with `title` unused in this release; four publicity regimes; profile files whose parameters cite sources marked read or to be verified; dated parameters and profile versions; no law in the core or a pack; core defaults and a refusal when a parameter is missing. Profiles `core`, `ca-federal` (pleasure craft licenses under SOR/2025-272) and `ca-qc` in `profiles/`.
- Filings REG-020 to REG-034: one completed filing for each change; a type catalog with three categories; immutability, with the list of fields that the register sets before a final status; `submittedAt`, `effectiveAt` and `completedAt`; separate payment, review and processing statuses; the actor, the represented party and the authority, from a representation of the identity specification or an order; fees and eligibility as decisions; corrections as whole replacements; orders as filings; stated changes that the replay applies; the light chain of sequence numbers and previous commitments, sealed and logged in a log series of the register's own under the signed records specification; separate verification results, including the match between the chain and the log; deadlines as profile data, counted from the date that `countFrom` names, that never reject a late filing on their own; restatement of the later versions that a retroactive filing affects.
- Derived state REG-040 to REG-046: replay, with corrections at the sequence of the filing they correct and restated versions; history rows with the filings that opened and ended them; bitemporal queries; rebuildable stored views; no deletion outside a destruction filing; time-driven and act-driven states; migration filings and scheduled expiries.
- Assets and rights REG-050 to REG-061: asset classes per pack; identifier schemes with uniqueness scope and normalized search keys; typed links; owner groups with tenancy codes from the profile, sole, joint and in-common by default, that add up to one; transfers that end and open groups, with causes; ownership apart from entitlement; entitlements with class, number, validity, roles, assets and conditions; terms as profile data with `countFrom`; optional encumbrances; rights in another register declared, not copied; parties from the data models specification.
- Visibility REG-070 to REG-077: four visibility classes; conditional visibility; opposability as its own flag; omission reason codes; access policies; authorization on every request; an audit event for each read; a list of reads for the data subject.
- Search and extracts REG-080 to REG-087: declared search modes and matching rules; search records; searches on personal data by `POST`; extracts that state their instants and last filing, sealed and logged; extract layout as profile data; verifiable credentials for entitlements; BODS and CBV for business packs.
- Retention REG-090 to REG-096: retention classes per filing and evidence type; filings apart from event retention; evidence by reference with a salted hash; destruction filings that name their targets and destroy every filing that holds one, deleting content and salt together; tombstones that keep the corrected filing of a correction; chain and replay after destruction; copies made before a destruction.
- Packs and conformance REG-100 to REG-108: domain packs; pack versions; two CloudEvents types with schemas in `registry/events/`; no personal value in events; no interface that edits or deletes a filing, with API tests under TST-040; replay fixtures and event tests under TST-043; synthetic data; an optional GovStack adapter; replacement of a core engine.
- Informative pages on the alignment with LADM, BODS 0.4, SEMIC CBV 2.2.0, GovStack Digital Registries 3.0-alpha, VC 2.0 and the Once-Only Technical System, and on questions for counsel.
- The LinkML model `model/registry.yaml`, which imports the Party model of the data models specification, and the pleasure craft pack schema `model/pleasure-craft.yaml`, with the pack data in `packs/pleasure-craft.yaml`.
- A synthetic pleasure craft license register in `examples/pleasure-craft/`: six filings, of which a lawful order destroyed the issue and its first correction, with a second correction that restates them; the light chain; a stand-in log series in two yearly shards; seven bitemporal snapshots; extracts, a search record and events. A public view of a Québec beneficiary record in `examples/ca-qc/` shows conditional visibility. A replay check, its test of 52 broken copies and scenarios in English and French run in the `examples` job of the continuous integration.
- Comparison data with international rows and rows for Canada, Québec and France.
- How-to guide that puts a register under the specification.

### Known gaps

- The generated forms of the model under DMO-014 and DMO-015 are deferred to the conformance suite.
- The `model/examples/` folder of DMO-017 is deferred to the conformance suite; the examples sit in `examples/` for now.
- The formats of the Canadian pleasure craft license number and hull serial number were not read, so the pack declares no format.
- The business and road vehicle packs of the `ca-qc` profile are planned, not published.

[Unreleased]: https://github.com/fpsot-org/fpsot-spec-registry/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fpsot-org/fpsot-spec-registry/releases/tag/v0.1.0
