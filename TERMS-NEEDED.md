# Terms needed

Entries in the format of `termbase/terms.yaml` of fpsot-spec-writing, for a pull request to the term base.
The pages of this specification write these terms in plain text for now, and will use the term attributes once the term base has them.
The French forms marked "to confirm" have no record that the writer could check in the Grand dictionnaire terminologique or TERMIUM Plus during this work.

## Decisions for the lead (provisional French forms)

1. **filing → « déclaration »** (provisional, used on every French page). The term base already gives « dépôt » for *repository*, so the French pages now keep « dépôt » for repositories. The Québec enterprise registrar calls its filings « déclarations ». Alternatives: « dépôt » (TERMIUM, for the filing of a document, but it collides with *repository*), « acte déposé », or « réquisition d’inscription » (RDPRM usage, which covers only applications to register a right). Side effects: a BODS *statement* becomes « énoncé », and a *register declaration* (REG-010) becomes « fiche de registre », so that « déclaration » keeps one meaning.
2. **tombstone → « trace de destruction »** (provisional, used on every French page). « Témoin » is the word of the signed records specification for a log *witness*, so the earlier « témoin de destruction » would mislead. Alternatives: « marqueur de destruction », « vestige ».
3. **entitlement → « droit »** is ambiguous in French: the same word means *law*, *right* and *fee* (« droits » in « droits exigibles »). The pages write « droit » where context is clear. Alternatives: « droit accordé », « autorisation ».
4. **status → « statut »** for the payment, review and processing status of a filing; « état » stays for the state of a register and the lifecycle state of an entitlement.
5. **jurisdiction profile.** The existing definition speaks of notices, human review and impact levels, which fit the decisions specification only. The entry below proposes a broader definition, and the pages write the term in plain text until then.
6. **asset and entitlement.** The existing definitions say that an asset is "a thing or right that can be owned" and that an entitlement is a right "over an asset". In this specification, an asset is a thing that the register identifies, and an entitlement may cover no asset at all, such as a business registration. The entries below propose matching definitions.

```yaml
  - id: filing
    kind: term
    en: {full: "filing", definition: "One legal event in a register, such as an application, an act of the registrar, a correction, an order or a destruction, which never changes once received."}
    fr: {full: "déclaration", definition: "Événement juridique dans un registre, comme une demande, un acte du registraire, une correction, une ordonnance ou une destruction, qui ne change jamais une fois reçu."}
    source: {name: "FPSOT registry specification, REG-020 and REG-021; French form provisional, see decision 1 (the Québec enterprise registrar uses déclaration)", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: register
    kind: term
    en: {full: "register", definition: "One registry that a law establishes, with its legal effect, its publicity regime and its filings."}
    fr: {full: "registre", definition: "Registre établi par une loi, avec son effet juridique, son régime de publicité et ses déclarations."}
    source: {name: "FPSOT registry specification, REG-010; same French form as registry", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: registration
    kind: term
    en: {full: "registration", definition: "The entry of a fact or a right in a register."}
    fr: {full: "inscription", definition: "Entrée d’un fait ou d’un droit dans un registre."}
    source: {name: "Civil Code of Québec, book on the publication of rights, for the French form, to be verified", url: "https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991", checked: "2026-11-18"}
  - id: derived-state
    kind: term
    en: {full: "derived state", definition: "The state of a register that a replay of its completed filings gives, as of one instant and as recorded at another."}
    fr: {full: "état dérivé", definition: "État d’un registre que donne le rejeu de ses déclarations achevées, à un instant donné, tel qu’enregistré à un autre."}
    source: {name: "FPSOT registry specification, REG-040; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: replay
    kind: term
    en: {full: "replay", definition: "Applying the stated changes of completed filings in order, to rebuild the state of a register."}
    fr: {full: "rejeu", definition: "Application, dans l’ordre, des changements déclarés des déclarations achevées, pour reconstruire l’état d’un registre."}
    source: {name: "FPSOT registry specification, REG-040; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: valid-time
    kind: term
    en: {full: "valid time", definition: "The time during which a fact holds in the world, as opposed to the time at which a system recorded it."}
    fr: {full: "temps de validité", definition: "Temps pendant lequel un fait vaut dans le monde, par opposition au moment où un système l’a enregistré."}
    source: {name: "FPSOT registry specification, REG-042; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: light-chain
    kind: term
    en: {full: "light chain", definition: "The link between the filings of one register, made of a sequence number and the commitment of the filing before, with no key of its own."}
    fr: {full: "chaîne légère", definition: "Lien entre les déclarations d’un registre, fait d’un numéro d’ordre et du condensé salé de la déclaration précédente, sans clé propre."}
    source: {name: "FPSOT registry specification, REG-030; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: commitment
    kind: term
    en: {full: "commitment", definition: "The salted hash of a sealed filing, which is its entry in the transparency log."}
    fr: {full: "condensé salé", definition: "Condensé salé d’une déclaration cachetée, qui est son entrée dans le journal de transparence."}
    source: {name: "FPSOT registry specification, REG-031, after LOG-031; French form as in the signed records specification, to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: sequence-number
    kind: term
    en: {full: "sequence number", definition: "The number of a filing in its register, from 1 with no gap."}
    fr: {full: "numéro d’ordre", definition: "Numéro d’une déclaration dans son registre, à partir de 1 et sans trou."}
    source: {name: "FPSOT registry specification, REG-030; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: tombstone
    kind: term
    en: {full: "tombstone", definition: "What remains of a lawfully destroyed filing: its place in the chain, its dates, its type and the ids of its rows, with no other value."}
    fr: {full: "trace de destruction", definition: "Ce qui reste d’une déclaration détruite légalement : sa place dans la chaîne, ses dates, son type et les identifiants de ses lignes, sans autre valeur."}
    source: {name: "FPSOT registry specification, REG-094; French form provisional, see decision 2", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: destruction-filing
    kind: term
    en: {full: "destruction filing", definition: "A filing that destroys the content and the salt of every earlier filing that holds a value that a law or an order targets, and leaves tombstones."}
    fr: {full: "déclaration de destruction", definition: "Déclaration qui détruit le contenu et le sel de déclarations antérieures en vertu d’une loi ou d’une ordonnance, et laisse des traces de destruction."}
    source: {name: "FPSOT registry specification, REG-093; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: owner-group
    kind: term
    en: {full: "owner group", definition: "A group of parties that holds an interest in an asset, alone, jointly or in common with other groups."}
    fr: {full: "groupe de propriétaires", definition: "Groupe de parties qui détient un intérêt dans un bien, seul, conjointement ou en commun avec d’autres groupes."}
    source: {name: "FPSOT registry specification, REG-053, after the manufactured home register of British Columbia; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: tenancy
    kind: term
    en: {full: "tenancy", definition: "How an owner group holds its interest: sole, joint or in common."}
    fr: {full: "mode de détention", definition: "Façon dont un groupe de propriétaires détient son intérêt : seul, conjointement ou en commun."}
    source: {name: "FPSOT registry specification, REG-053; French form to confirm. Common law French uses tenance conjointe and tenance commune; Québec civil law speaks of indivision, which is not the same concept", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: encumbrance
    kind: term
    en: {full: "encumbrance", definition: "A lien, a seizure, a stop order or a flag that weighs on an asset or on an entitlement."}
    fr: {full: "charge", definition: "Sûreté, saisie, interdiction ou signalement qui grève un bien ou un droit."}
    source: {name: "TERMIUM Plus, encumbrance, for the French form, to confirm. A sûreté is only one kind of charge, and a Québec hypothèque only one kind of sûreté", url: "https://www.btb.termiumplus.gc.ca/", checked: "2026-11-18"}
  - id: opposability
    kind: term
    en: {full: "opposability", definition: "The quality of a registered fact that a party can rely on against third parties."}
    fr: {full: "opposabilité", definition: "Qualité d’un fait inscrit qu’une partie peut faire valoir contre les tiers."}
    source: {name: "Civil Code of Québec, opposable aux tiers, for the French form, to be verified", url: "https://www.legisquebec.gouv.qc.ca/fr/document/lc/CCQ-1991", checked: "2026-11-18"}
  - id: legal-effect
    kind: term
    en: {full: "legal effect", definition: "What registration does in law: identify an asset for the administration, give notice or opposability, or create or prove title."}
    fr: {full: "effet juridique", definition: "Ce que produit l’inscription en droit : identifier un bien pour l’administration, donner avis ou opposabilité, ou créer ou prouver le titre."}
    source: {name: "FPSOT registry specification, REG-011; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: publicity-regime
    kind: term
    en: {full: "publicity regime", definition: "Who may see a register: everyone, everyone with exceptions, people who meet a condition, or no one outside the body."}
    fr: {full: "régime de publicité", definition: "Qui peut voir un registre : tout le monde, tout le monde avec des exceptions, les personnes qui remplissent une condition, ou personne hors de l’organisme."}
    source: {name: "FPSOT registry specification, REG-012; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: visibility-class
    kind: term
    en: {full: "visibility class", definition: "Who may see a field of a register: the public, the parties, the agency or only named roles."}
    fr: {full: "catégorie de visibilité", definition: "Qui peut voir un champ d’un registre : le public, les parties, l’organisme ou seulement des rôles nommés."}
    source: {name: "FPSOT registry specification, REG-070; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: access-policy
    kind: term
    en: {full: "access policy", definition: "A grant in a profile that lets a category of recipients see more than the public, with its legal basis, purpose, expiry and duty to log."}
    fr: {full: "politique d’accès", definition: "Autorisation d’un profil qui permet à une catégorie de destinataires de voir plus que le public, avec sa base juridique, sa fin, son échéance et son obligation de journaliser."}
    source: {name: "FPSOT registry specification, REG-074; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: omission-reason
    kind: term
    en: {full: "omission reason", definition: "The code that tells why a view leaves a field out, such as a law, an application, a missing value or a destruction."}
    fr: {full: "motif d’omission", definition: "Code qui dit pourquoi une vue omet un champ, comme une loi, une demande, une valeur absente ou une destruction."}
    source: {name: "FPSOT registry specification, REG-073, after BODS 0.4; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: domain-pack
    kind: term
    en: {full: "domain pack", definition: "The released data and schema of one domain of registers, such as pleasure craft: asset classes, identifier schemes, filing types and lifecycles."}
    fr: {full: "module de domaine", definition: "Données et schéma publiés d’un domaine de registres, comme les embarcations de plaisance : classes de biens, schémas d’identifiants, types de déclarations et cycles de vie."}
    source: {name: "FPSOT registry specification, REG-100; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: jurisdiction-profile
    kind: term
    en: {full: "jurisdiction profile", definition: "A released set of the legal parameters that the law of one jurisdiction sets for a kind of software, each with its source."}
    fr: {full: "profil juridictionnel", definition: "Ensemble publié des paramètres juridiques que le droit d’une collectivité publique fixe pour un genre de logiciel, chacun avec sa source."}
    source: {name: "Broader definition proposed by the FPSOT registry specification, REG-013, to replace the one of DEC-011; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: register-operator
    kind: term
    en: {full: "register operator", definition: "The body or the supplier that runs a register and serves its views, searches and extracts."}
    fr: {full: "exploitant de registre", definition: "Organisme ou fournisseur qui fait fonctionner un registre et en sert les vues, les recherches et les extraits."}
    source: {name: "FPSOT registry specification, REG-002; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: core-engine
    kind: term
    en: {full: "core engine", definition: "Software that keeps filings and derives the state of registers of any domain, under the rules of this specification."}
    fr: {full: "moteur de base", definition: "Logiciel qui tient les déclarations et dérive l’état de registres de tout domaine, selon les règles de cette spécification."}
    source: {name: "FPSOT registry specification, REG-002; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: search-mode
    kind: term
    en: {full: "search mode", definition: "A declared way to search a register, with its keys, its matching rule and the views that may use it."}
    fr: {full: "mode de recherche", definition: "Façon déclarée de chercher dans un registre, avec ses clés, sa règle de correspondance et les vues qui peuvent l’employer."}
    source: {name: "FPSOT registry specification, REG-080; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: extract
    kind: term
    en: {full: "extract", definition: "A sealed record of what a register shows about a subject, as of one instant and as recorded at another."}
    fr: {full: "extrait", definition: "Document cacheté de ce qu’un registre montre sur un sujet, à un instant donné, tel qu’enregistré à un autre."}
    source: {name: "FPSOT registry specification, REG-084; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: retention-class
    kind: term
    en: {full: "retention class", definition: "How long one kind of filing or evidence stays in a register, and the rule of the retention schedule that says so."}
    fr: {full: "catégorie de conservation", definition: "Durée pendant laquelle un genre de déclaration ou de pièce reste dans un registre, et règle du calendrier de conservation qui la fixe."}
    source: {name: "FPSOT registry specification, REG-090; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: verifiable-credential
    kind: term
    en: {full: "verifiable credential", definition: "A set of claims by an issuer, in the W3C data model, whose origin and integrity anyone can check."}
    fr: {full: "attestation vérifiable", definition: "Ensemble d’affirmations d’un émetteur, selon le modèle de données du W3C, dont chacun peut vérifier l’origine et l’intégrité."}
    source: {name: "W3C Verifiable Credentials Data Model v2.0 for the English form; French form to confirm", url: "https://www.w3.org/TR/2025/REC-vc-data-model-2.0-20250515/", checked: "2026-11-18"}
  - id: beneficial-owner
    kind: term
    en: {full: "beneficial owner", definition: "A person who in the end owns or controls a business, as a register of beneficial owners records them."}
    fr: {full: "bénéficiaire effectif", definition: "Personne qui, au bout du compte, possède ou contrôle une entreprise, telle qu’un registre des bénéficiaires l’inscrit."}
    source: {name: "French law uses bénéficiaire effectif; Québec uses bénéficiaire ultime. Both to confirm", url: "https://www.quebec.ca/entreprises-et-travailleurs-autonomes/demarrer-entreprise/immatriculer-constituer-entreprise/nouvelles-obligations-transparence", checked: "2026-11-18"}
  - id: pleasure-craft-license
    kind: term
    en: {full: "pleasure craft license", definition: "The license that a pleasure craft in scope of the Small Vessel Regulations of Canada must carry."}
    fr: {full: "permis d’embarcation de plaisance", definition: "Permis que doit porter une embarcation de plaisance visée par le Règlement sur les petits bâtiments du Canada."}
    source: {name: "SOR/2025-272 and DORS/2025-272, Canada Gazette, Part II (official forms in both languages)", url: "https://gazette.gc.ca/rp-pr/p2/2025/2025-12-31/html/sor-dors272-fra.html", checked: "2026-11-18"}
  - id: bods
    kind: abbreviation
    en: {short: "BODS", full: "Beneficial Ownership Data Standard", definition: "An open standard of Open Ownership for publishing data on the beneficial owners of companies."}
    fr: {short: "BODS", full: "Beneficial Ownership Data Standard", definition: "Norme ouverte d’Open Ownership pour publier les données sur les bénéficiaires effectifs des sociétés."}
    source: {name: "Open Ownership, BODS 0.4 (proper name, kept in English)", url: "https://standard.openownership.org/en/0.4.0/standard/reference.html", checked: "2026-11-18"}
  - id: ladm
    kind: abbreviation
    en: {short: "LADM", full: "Land Administration Domain Model", definition: "The model of ISO 19152 for parties, administrative units, rights, restrictions and responsibilities in land administration."}
    fr: {short: "LADM", full: "Land Administration Domain Model", definition: "Modèle de la norme ISO 19152 pour les parties, les unités administratives, les droits, les restrictions et les responsabilités en administration foncière."}
    source: {name: "ISO 19152-1:2024 (proper name, kept in English; French title to confirm)", url: "https://www.iso.org/standard/81263.html", checked: "2026-11-18"}
  - id: cbv
    kind: abbreviation
    en: {short: "CBV", full: "Core Business Vocabulary", definition: "A SEMIC vocabulary of the European Commission for the basic data of a registered business."}
    fr: {short: "CBV", full: "Core Business Vocabulary", definition: "Vocabulaire SEMIC de la Commission européenne pour les données de base d’une entreprise immatriculée."}
    source: {name: "SEMIC, Core Business Vocabulary 2.2.0 (proper name, kept in English)", url: "https://semiceu.github.io/Core-Business-Vocabulary/releases/2.2.0/", checked: "2026-11-18"}
  - id: semic
    kind: abbreviation
    en: {short: "SEMIC", full: "Semantic Interoperability Community", definition: "The community of the European Commission that publishes core vocabularies for public sector data."}
    fr: {short: "SEMIC", full: "Semantic Interoperability Community", definition: "Communauté de la Commission européenne qui publie des vocabulaires de base pour les données du secteur public."}
    source: {name: "European Commission, SEMIC (proper name, kept in English; to confirm)", url: "https://semiceu.github.io/Core-Business-Vocabulary/releases/2.2.0/", checked: "2026-11-18"}
  - id: rdprm
    kind: abbreviation
    en: {short: "RDPRM", full: "Register of personal and movable real rights", definition: "The Québec register of rights over movable property, such as hypothecs on vehicles."}
    fr: {short: "RDPRM", full: "Registre des droits personnels et réels mobiliers", definition: "Registre québécois des droits sur les biens meubles, comme les hypothèques sur les véhicules."}
    source: {name: "Registre des droits personnels et réels mobiliers (official French name; English form to confirm)", url: "https://www.rdprm.gouv.qc.ca/", checked: "2026-11-18"}
  - id: saaq
    kind: abbreviation
    en: {short: "SAAQ", full: "Société de l’assurance automobile du Québec", definition: "The Québec body that registers road vehicles and licenses drivers."}
    fr: {short: "SAAQ", full: "Société de l’assurance automobile du Québec", definition: "Organisme québécois qui immatricule les véhicules routiers et délivre les permis de conduire."}
    source: {name: "SAAQ (proper name in both languages)", url: "https://saaq.gouv.qc.ca/blob/saaq/documents/publications/acces-information/registre-communications-saaq.pdf", checked: "2026-11-18"}
  - id: cnil
    kind: abbreviation
    en: {short: "CNIL", full: "Commission nationale de l’informatique et des libertés", definition: "The French data protection authority."}
    fr: {short: "CNIL", full: "Commission nationale de l’informatique et des libertés", definition: "Autorité française de protection des données."}
    source: {name: "CNIL (proper name in both languages)", url: "https://www.cnil.fr/fr/siv-systeme-dimmatriculation-des-vehicules", checked: "2026-11-18"}
  - id: sor
    kind: abbreviation
    en: {short: "SOR", full: "Statutory Orders and Regulations", definition: "The series in which Canada registers and numbers its federal regulations, such as SOR/2025-272."}
    fr: {short: "DORS", full: "Décrets, ordonnances et règlements statutaires", definition: "Série dans laquelle le Canada enregistre et numérote ses règlements fédéraux, comme le DORS/2025-272."}
    source: {name: "Canada Gazette, Part II (official forms in both languages; full French form to confirm)", url: "https://gazette.gc.ca/rp-pr/p2/2025/2025-12-31/html/sor-dors272-eng.html", checked: "2026-11-18"}
  - id: asset
    kind: term
    en: {full: "asset", definition: "A thing that a register identifies, such as a vessel, a vehicle, a drone or a firearm."}
    fr: {full: "bien", definition: "Chose qu’un registre identifie, comme un bateau, un véhicule, un drone ou une arme."}
    source: {name: "Changed definition proposed by the FPSOT registry specification, REG-050; same French form", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: entitlement
    kind: term
    en: {full: "entitlement", definition: "A right that a register grants to parties, such as a license, a permit or a registration, which may cover assets or none."}
    fr: {full: "droit", definition: "Droit qu’un registre accorde à des parties, comme un permis, une autorisation ou une immatriculation, qui peut viser des biens ou aucun."}
    source: {name: "Changed definition proposed by the FPSOT registry specification, REG-056 and REG-057; French form ambiguous, see decision 3", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: status
    kind: term
    en: {full: "status", definition: "Where one track of the processing of a filing stands, such as its payment, its review or its processing."}
    fr: {full: "statut", definition: "Point où en est un volet du traitement d’une déclaration, comme son paiement, son examen ou son traitement."}
    source: {name: "FPSOT registry specification, REG-024; French form to confirm, see decision 4", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: restatement
    kind: term
    en: {full: "restatement", definition: "A later version of an entity that a retroactive filing repeats in full, so that the replay never runs the rules again."}
    fr: {full: "réénoncé", definition: "Version ultérieure d’une entité qu’une déclaration rétroactive répète au complet, pour que le rejeu n’exécute jamais de nouveau les règles."}
    source: {name: "FPSOT registry specification, REG-034; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
  - id: log-series
    kind: term
    en: {full: "log series", definition: "The log that holds the commitments of the filings of one register and nothing else, cut into yearly shards."}
    fr: {full: "série de journal", definition: "Journal qui contient les condensés salés des déclarations d’un seul registre et rien d’autre, divisé en tranches annuelles."}
    source: {name: "FPSOT registry specification, REG-031, after LOG-032 and LOG-035; French form to confirm", url: "https://github.com/fpsot-org/fpsot-spec-registry", checked: "2026-11-18"}
```
