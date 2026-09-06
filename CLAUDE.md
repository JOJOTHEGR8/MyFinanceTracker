# Contexte du projet

## Qui je suis

Jojo (Georges Elias Khalil). Basé à Montréal, bosse et pense principalement en
français (code/commits/doc peuvent être en anglais quand c'est la norme du
milieu). B.B.A. bilingue HEC Montréal (Business Analysis TI + Finance).
Parcours finance/données, démarre comme Conseiller Bancaire chez RBC. Stack
actuelle : SQL, Excel avancé, Power BI, MS Access, Python (pandas), notions
SAP/Odoo. Solide en analyse de données et logique métier, moins rodé en
ingénierie logicielle (archi, tests, CI/CD, déploiement) — c'est ce qu'il
muscle via ces projets. Priorités du portfolio : **finance** et **bases de
données**.

## Ce dépôt : MyFinanceTracker

Agrégateur de finances personnelles multi-institutions inspiré du
**Consumer-Driven Banking** (open banking canadien, Phase 1 en déploiement en
2026). Simule 3 institutions fictives aux formats de relevés incompatibles
(`data/raw/`), les normalise vers un schéma SQLite commun (`src/schema.sql`),
catégorise les transactions par règles, et expose le résultat via un
tableau de bord Power BI connecté directement à la base.

Toutes les données sont synthétiques — jamais de vraies données bancaires.

Statut : pipeline d'ingestion (`src/ingest.py`, pandas), catégorisation par
règles (`src/categorize.py`) et orchestration (`src/pipeline.py`) fonctionnels
et testés (21 tests, `python -m pytest`, CI GitHub Actions sur chaque push).
Tableau de bord Power BI construit et connecté à `finance.db` (généré par le
pipeline, non versionné). Données étendues à une année complète (2026, 262
transactions) avec un changement de format à mi-année pour Carte Nordik et
des défauts réalistes injectés (doublons, description manquante, montants
illisibles) — voir `docs/decisions.md` et `docs/analyse.md`.

Décisions déjà prises (ne pas rouvrir sans raison) :
- SQLite plutôt que Postgres : zéro serveur à monter, fichier versionnable,
  vrai SQL. Le fichier `.db` généré n'est **pas** commité (`.gitignore`) —
  il se régénère par le pipeline, pas stocké comme état.
- Power BI plutôt que Streamlit : Jojo maîtrise déjà l'outil. Démo publique
  via "Publier sur le web" (acceptable car données 100 % synthétiques —
  ne jamais faire ça avec de vraies données).
- Pas de ML de catégorisation : règles par mot-clé seulement. Voir
  `docs/decisions.md` section 2 pour le raisonnement complet.
- Portée volontairement limitée à la profondeur (données réalistes, tests,
  CI, documentation des décisions) plutôt qu'à la largeur (plus
  d'institutions, plus de types de graphiques, une UI custom en plus de
  Power BI) — décision explicite après discussion sur ce qui prouve
  réellement du jugement à un recruteur vs ce qui gonfle artificiellement
  le scope. Un futur "dashboard live" (API boursière + rafraîchissement
  programmé Power BI Service) est noté comme projet SÉPARÉ, pas une
  extension de celui-ci — architecture différente (API cloud vs pipeline
  batch local), ne pas mélanger les deux.

## Comment on travaille ensemble

Voir le CLAUDE.md du repo `Micro-Informa` de Jojo pour le style complet
(brut, honnête, pédagogue, opinions tranchées). En résumé : on avance une
étape à la fois (cadrage → archi → structure → code en petits incréments →
qualité/tests → doc → publication), on valide ensemble avant de passer à la
suivante, et "fini > parfait".
