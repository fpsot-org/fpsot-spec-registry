# language: fr
# SPDX-License-Identifier: Community-Spec-1.0
# Fonctionnalité d’exemple de la spécification FPSOT sur les registres (REG-105), selon TST-020 à TST-036.
# Elle rejoue les dépôts de examples/pleasure-craft/ selon le profil ca-federal.
# Chaque personne, numéro et ordonnance est fictif. Toutes les données sont synthétiques (TST-050 à TST-056).
@pleasure-craft-license
Fonctionnalité: Rejeu d’un registre des permis d’embarcation de plaisance
  Chaque scénario indique les dépôts, leurs dates et l’état dérivé que le rejeu doit donner.

  Règle: Un permis vaut cinq ans à compter de sa délivrance, de son transfert ou de son renouvellement

    @pleasure-craft-license-001
    Scénario: Un transfert ouvre un nouveau groupe de propriétaires et une nouvelle période
      Étant donné le registre "pleasure-craft-licenses" selon le profil "ca-federal" à la version "0.1.0"
      Et le dépôt "ownership-transfer" pour la cause "sale" avec effet le "2026-06-10T16:00:00Z", reçu le "2026-06-25T15:00:00Z"
      Quand le registre achève le dépôt le "2026-06-26T15:00:00Z"
      Alors l’état du délai du dépôt est "met"
      Et au "2026-06-20T12:00:00Z", tel qu’enregistré au "2026-08-10T12:00:00Z", le groupe de propriétaires "019a1b2c-3d4e-7f03-8a03-000000000302" détient toute l’embarcation
      Et le permis "EX 000001" est valide du "2026-06-10" au "2031-06-10"

    @pleasure-craft-license-002
    Scénario: Un renouvellement ouvre une nouvelle période à compter de sa propre date
      Étant donné le registre "pleasure-craft-licenses" selon le profil "ca-federal" à la version "0.1.0"
      Et le dépôt "license-renewal" avec effet le "2031-05-20T16:00:00Z"
      Quand le registre achève le dépôt le "2031-05-20T16:00:00Z"
      Alors au "2031-06-01T12:00:00Z", tel qu’enregistré au "2031-06-01T12:00:00Z", le permis "EX 000001" est valide du "2031-05-20" au "2036-05-20"
      Et l’état du permis est "active"

    @pleasure-craft-license-003
    Scénario: Un permis expiré n’exige aucun dépôt
      Étant donné le registre "pleasure-craft-licenses" selon le profil "ca-federal" à la version "0.1.0"
      Et le dernier dépôt "license-renewal" du permis fixe la fin de sa validité au "2036-05-20"
      Quand le registre rejoue ses dépôts au "2036-06-01T12:00:00Z", tel qu’enregistré au "2036-06-01T12:00:00Z"
      Alors l’état du permis est "expired"
      Et le dernier numéro d’ordre de l’instantané est 5

  Règle: Une correction remplace un dépôt pour chaque moment d’inscription ultérieur

    @pleasure-craft-license-004
    Scénario: Le numéro de série de la coque suit la correction dès son inscription
      Étant donné le registre "pleasure-craft-licenses" selon le profil "ca-federal" à la version "0.1.0"
      Et le dépôt "filing-correction" qui corrige le numéro d’ordre 1, achevé le "2026-07-15T15:00:00Z"
      Quand le registre rejoue ses dépôts au "2026-06-01T12:00:00Z", tel qu’enregistré au "2026-07-31T12:00:00Z"
      Alors le numéro de série de la coque de l’embarcation est "EXA 12354 B626"
      Et le groupe de propriétaires "019a1b2c-3d4e-7f03-8a03-000000000301" vient de la correction et le numéro d’ordre 2 y met fin

  Règle: Une destruction légale garde la chaîne vérifiable

    @pleasure-craft-license-005
    Scénario: Un dépôt détruit laisse un témoin de destruction et la chaîne se vérifie encore
      Étant donné le registre "pleasure-craft-licenses" selon le profil "ca-federal" à la version "0.1.0"
      Et le dépôt "destruction-order" qui détruit le numéro d’ordre 1, achevé le "2026-08-04T15:00:00Z"
      Quand une personne qui vérifie contrôle la chaîne légère du numéro d’ordre 1 au numéro d’ordre 5
      Alors le contenu et le sel du numéro d’ordre 1 ont disparu et son témoin de destruction garde son condensé salé
      Et le condensé salé précédent du numéro d’ordre 2 égale le condensé salé du témoin de destruction
      Et au "2026-06-20T12:00:00Z", tel qu’enregistré au "2026-06-30T12:00:00Z", l’embarcation figure comme ligne détruite
