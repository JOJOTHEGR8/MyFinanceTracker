# MyFinanceTracker

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

🚧 En construction — pipeline d'ingestion, catégorisation et base SQLite
fonctionnels et testés. Tableau de bord Power BI à venir.

## Le problème concret

Chaque institution exporte ses relevés à sa façon. Ce repo simule 3
institutions fictives avec 3 formats incompatibles (voir `data/raw/`) :

| Fichier | Délimiteur | Dates | Montant | Particularité |
|---|---|---|---|---|
| `banque_boreale_compte_cheque.csv` | virgule | JJ/MM/AAAA | colonnes Débit/Crédit séparées | — |
| `caisse_aurore_epargne.csv` | virgule | AAAA-MM-JJ | colonne signée unique | — |
| `carte_nordik_credit.csv` | **point-virgule** | JJ/MM/AAAA | colonne signée, **virgule décimale** | convention de signe inversée (carte de crédit) |

Le pipeline (`src/ingest.py`) normalise tout ça vers un schéma commun —
y compris une subtilité réelle des cartes de crédit : leur relevé inverse
la convention de signe (un achat y est positif, un paiement négatif), donc
le signe est inversé à l'ingestion pour mesurer des *dépenses* de façon
cohérente entre tous les comptes (raisonnement complet dans le docstring
du module).

## Structure du repo

```
data/raw/            Relevés sources par institution (formats hétérogènes, volontaire)
src/schema.sql       Schéma relationnel cible (institutions, comptes, transactions, catégories)
src/ingest.py        Un parseur par institution -> schéma commun
src/categorize.py    Catégorisation par règles de mots-clés
src/pipeline.py      Orchestration : construit finance.db et affiche un résumé
tests/               Tests (catégorisation, ingestion, bout-en-bout)
powerbi/             Tableau de bord Power BI connecté à la base SQLite générée (à venir)
```

## Stack

- **Python (pandas)** — ingestion et normalisation des relevés
- **SQLite** — base relationnelle, schéma dans `src/schema.sql`
- **Power BI** — tableau de bord, connecté directement à la base SQLite

## Lancer le projet

```bash
pip install -r requirements.txt

# Construire finance.db à partir de data/raw/ et afficher un résumé
python -m src.pipeline

# Lancer les tests
python -m pytest
```

La base `finance.db` générée n'est pas versionnée (voir `.gitignore`) — elle
se reconstruit à chaque exécution du pipeline, elle n'est jamais un état
stocké dans le repo.

## Contexte réglementaire

- [Consumer-Driven Banking — règlement proposé](https://www.flinks.com/blog/open-banking-canada-2026-launch-fintech-institutions)
- [Open banking : lancement au Canada](https://www.forbes.com/sites/christerholloman/2026/02/09/open-banking-now-launching-in-canada-what-it-means-for-you-and-banks/)
