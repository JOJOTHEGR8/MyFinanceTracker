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

Statut : squelette en place (structure, schéma, données d'exemple). Pipeline
d'ingestion/catégorisation et tableau de bord Power BI à construire.

Décisions déjà prises (ne pas rouvrir sans raison) :
- SQLite plutôt que Postgres : zéro serveur à monter, fichier versionnable,
  vrai SQL. Le fichier `.db` généré n'est **pas** commité (`.gitignore`) —
  il se régénère par le pipeline, pas stocké comme état.
- Power BI plutôt que Streamlit : Jojo maîtrise déjà l'outil. Pour garder une
  démo publique cliquable malgré ça, utiliser "Publier sur le web" une fois
  le tableau de bord fait (acceptable car données 100 % synthétiques —
  ne jamais faire ça avec de vraies données).
- Pas de ML de catégorisation en V1 : règles par mot-clé seulement. Le ML
  serait de la sur-ingénierie pour un projet weekend.

## Comment on travaille ensemble

Voir le CLAUDE.md du repo `Micro-Informa` de Jojo pour le style complet
(brut, honnête, pédagogue, opinions tranchées). En résumé : on avance une
étape à la fois (cadrage → archi → structure → code en petits incréments →
qualité/tests → doc → publication), on valide ensemble avant de passer à la
suivante, et "fini > parfait".
