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

🚧 En construction — squelette de repo en place, pipeline d'ingestion à venir.

## Le problème concret

Chaque institution exporte ses relevés à sa façon. Ce repo simule 3
institutions fictives avec 3 formats incompatibles (voir `data/raw/`) :

| Fichier | Délimiteur | Dates | Montant | Particularité |
|---|---|---|---|---|
| `banque_boreale_compte_cheque.csv` | virgule | JJ/MM/AAAA | colonnes Débit/Crédit séparées | — |
| `caisse_aurore_epargne.csv` | virgule | AAAA-MM-JJ | colonne signée unique | — |
| `carte_nordik_credit.csv` | **point-virgule** | JJ/MM/AAAA | colonne signée, **virgule décimale** | convention de signe inversée (carte de crédit) |

Le pipeline devra normaliser tout ça vers un schéma commun.

## Structure du repo

```
data/raw/       Relevés sources par institution (formats hétérogènes, volontaire)
src/schema.sql  Schéma relationnel cible (institutions, comptes, transactions, catégories)
src/            Pipeline d'ingestion, catégorisation, orchestration (à venir)
tests/          Tests de la logique de catégorisation
powerbi/        Tableau de bord Power BI connecté à la base SQLite générée
```

## Stack

- **Python (pandas)** — ingestion et normalisation des relevés
- **SQLite** — base relationnelle, schéma dans `src/schema.sql`
- **Power BI** — tableau de bord, connecté directement à la base SQLite

## Lancer le projet

À venir avec le pipeline (prochaine étape).

## Contexte réglementaire

- [Consumer-Driven Banking — règlement proposé](https://www.flinks.com/blog/open-banking-canada-2026-launch-fintech-institutions)
- [Open banking : lancement au Canada](https://www.forbes.com/sites/christerholloman/2026/02/09/open-banking-now-launching-in-canada-what-it-means-for-you-and-banks/)
