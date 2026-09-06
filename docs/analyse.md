# Ce qu'un conseiller financier remarquerait dans ces données

Analyse basée sur les 262 transactions réelles générées pour l'année 2026
(données synthétiques — voir l'avertissement du README). Les chiffres
ci-dessous sont ceux produits par `python -m src.pipeline`, pas des
estimations.

## Portrait global

| | Montant |
|---|---|
| Revenu annuel | 22 320,06 $ |
| Dépenses annuelles (hors virements internes) | 19 055,84 $ |
| Épargne nette | 3 264,22 $ |
| Taux d'épargne | ~14,6 % du revenu |

Un taux d'épargne de 14,6 % est correct, mais deux signaux dans le détail
méritent d'être creusés avant de le prendre pour argent comptant.

## Signal n°1 : le logement mange la moitié du revenu

Le loyer représente **11 373,81 $ sur l'année, soit ~51 % du revenu brut**.
La règle de base la plus citée en planification financière personnelle
plafonne le logement à 30 % du revenu — ce ménage est 70 % au-dessus de ce
repère. C'est le genre de chiffre qu'un conseiller identifierait en
premier, avant même de regarder les dépenses discrétionnaires : peu importe
à quel point le reste du budget est discipliné, une charge de logement à ce
niveau limite structurellement la marge de manœuvre (épargne, coussin
d'urgence, capacité d'emprunt pour un projet futur).

## Signal n°2 : la carte de crédit ne se referme pas à zéro

Le solde de Carte Nordik termine l'année à **-921,88 $**, en territoire
négatif — les paiements mensuels ("PAIEMENT RECU") ne couvrent pas
entièrement les dépenses portées à la carte. Ce n'est pas dramatique à ce
niveau, mais c'est le genre de dérive qui, laissée telle quelle,
composerait des intérêts d'un mois à l'autre. Un conseiller demanderait
si ce solde est stable, croissant, ou saisonnier — la réponse ici (voir
signal n°3) est qu'il est concentré sur une période précise.

## Signal n°3 : décembre sort clairement du lot

La catégorie "Achats" passe de 35-80 $/mois le reste de l'année à
**538,90 $ en décembre** — un pic net de dépenses des Fêtes, pas du bruit
statistique. Les dépenses totales de décembre (1 914,37 $) dépassent de
~23 % la moyenne des 11 autres mois (1 558,32 $). C'est exactement le genre
de pic prévisible qu'un budget devrait anticiper (mettre de côté un peu
chaque mois plutôt que d'absorber le choc en décembre) plutôt que découvrir
après coup.

## Ce que ça donnerait comme recommandations

1. **Revoir le logement en priorité** — c'est le levier avec le plus
   d'impact structurel, largement avant d'optimiser l'épicerie ou les
   abonnements.
2. **Provisionner les Fêtes à l'avance** — un virement automatique de
   ~45 $/mois vers l'épargne (538,90 $ ÷ 12) lisserait le pic de décembre
   au lieu de le subir.
3. **Surveiller la tendance du solde de carte de crédit** sur plusieurs
   années plutôt qu'un seul instantané — un solde négatif stable n'est pas
   le même problème qu'un solde qui grossit mois après mois.

C'est précisément le type d'angle mort qu'un agrégateur multi-institutions
révèle et qu'aucun relevé bancaire pris isolément ne montre — le loyer vit
dans le compte chèque, les achats des Fêtes sur la carte de crédit, et
personne ne les met côte à côte sans un outil comme celui-ci.
