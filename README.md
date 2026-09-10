# MyFinanceTracker

[![Tests](https://github.com/JOJOTHEGR8/MyFinanceTracker/actions/workflows/tests.yml/badge.svg)](https://github.com/JOJOTHEGR8/MyFinanceTracker/actions/workflows/tests.yml)

Agrégateur et tableau de bord de finances personnelles multi-institutions —
inspiré du **Consumer-Driven Banking** (l'open banking canadien), dont la
Phase 1 (accès en lecture aux données de comptes, avec consentement du
client) est en cours de déploiement en 2026 sous supervision de la Banque du
Canada.

L'infrastructure réelle n'est pas encore ouverte aux développeurs
indépendants — ce projet simule ce qu'elle rendra possible : consolider des
relevés de plusieurs institutions, dans des formats tous différents, en une
seule vue budgétaire.

⚠️ **Toutes les données sont synthétiques.** Aucune vraie donnée bancaire
n'est utilisée ni stockée ici.

## Statut

✅ Pipeline d'ingestion, catégorisation et base SQLite fonctionnels et
testés (21 tests, CI GitHub Actions sur chaque push). Tableau de bord
Power BI construit et connecté. Une année complète de données (262
transactions) avec défauts réalistes injectés volontairement.

## Le problème concret

Chaque institution exporte ses relevés à sa façon — et ça change avec le
temps. Ce repo simule 3 institutions fictives sur une année complète
(2026), avec des formats incompatibles **et un changement de format en
cours d'année** (voir `data/raw/`) :

| Fichier | Délimiteur | Dates | Montant | Particularité |
|---|---|---|---|---|
| `banque_boreale_compte_cheque.csv` | virgule | JJ/MM/AAAA | colonnes Débit/Crédit séparées | — |
| `caisse_aurore_epargne.csv` | virgule | AAAA-MM-JJ | colonne signée unique | — |
| `carte_nordik_credit_2026_h1.csv` (jan.-juin) | **point-virgule** | JJ/MM/AAAA | colonne signée, **virgule décimale** | convention de signe inversée (carte de crédit) |
| `carte_nordik_credit_2026_h2.csv` (juil.-déc.) | virgule | AAAA-MM-JJ | colonne signée, point décimal | **nouveau format** — la banque a modernisé son export en juillet |

Le pipeline (`src/ingest.py`) normalise tout ça vers un schéma commun —
y compris la conversion de signe des cartes de crédit (raisonnement complet
dans le docstring du module) et l'absorption du changement de format sans
toucher au schéma relationnel (`docs/decisions.md`, section 4).

**Les données ne sont pas parfaites non plus, volontairement.** Deux
doublons exacts, une description manquante et deux montants illisibles sont
injectés dans les relevés — le pipeline les détecte, les compte et les
rapporte plutôt que de planter ou de les avaler en silence (`docs/decisions.md`,
section 5).

## Structure du repo

```
data/raw/              Relevés sources par institution (formats hétérogènes + 1 changement de format, volontaire)
scripts/                Génération des données de démo (usage unique, non exécuté par le pipeline)
src/schema.sql          Schéma relationnel cible (institutions, comptes, transactions, catégories)
src/ingest.py           Un parseur par institution/format -> schéma commun, défensif contre les lignes invalides
src/categorize.py       Catégorisation par règles de mots-clés
src/pipeline.py         Orchestration : dédoublonnage, construction de finance.db, résumé
tests/                  33 tests (catégorisation, ingestion, bout-en-bout)
.github/workflows/      CI : tests lancés automatiquement à chaque push
docs/decisions.md       Décisions d'architecture et pièges réellement rencontrés
docs/analyse.md         Analyse d'une page des tendances dans les données générées
powerbi/                Tableau de bord Power BI connecté à la base SQLite générée
```

## Stack

- **Python (pandas)** — ingestion et normalisation des relevés
- **SQLite** — base relationnelle, schéma dans `src/schema.sql`
- **Power BI** — tableau de bord, connecté directement à la base SQLite
- **GitHub Actions** — tests exécutés automatiquement à chaque push

## Lancer le projet

```bash
pip install -r requirements.txt

# (Optionnel) régénérer les données de démo à partir de zéro
python scripts/generate_demo_data.py

# Construire finance.db à partir de data/raw/ et afficher un résumé
python -m src.pipeline

# Lancer les tests
python -m pytest
```

La base `finance.db` générée n'est pas versionnée (voir `.gitignore`) — elle
se reconstruit à chaque exécution du pipeline, elle n'est jamais un état
stocké dans le repo.

## Pour aller plus loin

- [`docs/decisions.md`](docs/decisions.md) — les choix d'architecture et les
  pièges réellement rencontrés (SQLite vs Postgres, le bug de catégorisation
  "paie"/"paiement", les deux pièges DAX/Power Query vécus en construisant
  le tableau de bord).
- [`docs/analyse.md`](docs/analyse.md) — ce qu'un conseiller financier
  remarquerait dans les données générées (le loyer à ~51 % du revenu, le
  pic de décembre, la dérive du solde de carte de crédit).

## Contexte réglementaire

- [Consumer-Driven Banking — règlement proposé](https://www.flinks.com/blog/open-banking-canada-2026-launch-fintech-institutions)
- [Open banking : lancement au Canada](https://www.forbes.com/sites/christerholloman/2026/02/09/open-banking-now-launching-in-canada-what-it-means-for-you-and-banks/)
