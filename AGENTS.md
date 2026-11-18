# Instructions for agents

This repository holds the FPSOT registry specification: registers of assets, ownership and entitlements under a law. It covers the immutable filing with its three dates, three statuses, authority and light chain; state derived by replaying filings, with bitemporal history; assets, owner groups, entitlements and encumbrances; field visibility, opposability and access policies; search modes, search records, sealed extracts and verifiable credentials; retention classes and lawful destruction with tombstones; domain packs, jurisdiction profiles, events and replay fixtures. It standardizes the filing and what can be derived from it, and leaves the law to profiles.

- The normative text is in `spec/en/` and `spec/fr/`. Every rule has an ID such as `REG-001`.
- Follow `skill/SKILL.md` when you write or review code that keeps a register, stores or replays filings, corrects or destroys them, writes a profile or a pack, serves register views, searches or extracts, or emits register events. The spec text wins on any difference.
- Every page exists in English and in French, with the same file name and the same IDs.
- Terms and abbreviations come from the term base of `fpsot-spec-writing`. Add a missing term there first; `TERMS-NEEDED.md` lists the ones this spec waits for.
- This is a layer 2 specification. It may cite every published layer 0 and layer 1 specification by rule ID. It cites the code specification only by topic until it is published, and the capability specification only by topic.
- Other specifications own the party (data models), representation and authorization (identity), data types, decisions and their reason codes (decisions, vocabularies), seals and the transparency log (log), audit events and their retention (observability), APIs and events (api-restful) and scenarios (testing). Cite their rules; never redefine them.
- No integrity mechanism of its own: the light chain is a sequence and the previous commitment, and seals, time stamps, witnesses and proofs come from the signed records specification. No blockchain.
- `model/registry.yaml` is the source of the record forms, and each pack adds one schema that imports it, such as `model/pleasure-craft.yaml`. `model/imports/` holds unchanged copies of the data types and party models. When you change a model, a pack, a profile or a fixture, run `bash examples/test-examples.sh`.
- Jurisdiction values live in `profiles/`, never in the model, a pack or the check script. Domain mechanics live in `packs/`.
- Examples hold synthetic data only: fictional people, numbers starting with `EX`, domains reserved for documentation, and no personal value in an event.
- Do not copy text from statutes, regulations or standards. Summarize in your own words and cite the exact version, with an archived copy.
- Do not state a legal point as a rule. Points that need a lawyer go in an informative note or in `questions-for-counsel.adoc`, and a text that nobody read at the source is marked "to be verified". France has comparison data only, no profile.
- Commits follow Conventional Commits and are signed. Pull requests are squash-merged.
