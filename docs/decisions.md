# Décisions d'architecture

Ce document capture les choix qui comptent et les pièges réellement
rencontrés en construisant ce projet — pas une reconstruction a posteriori,
mais le journal de ce qui a cassé et pourquoi le correctif retenu est le
bon, plutôt qu'un autre.

## 1. SQLite plutôt que PostgreSQL

**Contexte** : un pipeline personnel, pas un service multi-utilisateur.

**Décision** : SQLite — un fichier, zéro serveur à démarrer, mais un vrai
schéma relationnel avec de vraies jointures SQL.

**Écarté** : PostgreSQL, dont la valeur ajoutée (accès concurrent,
utilisateurs multiples, réplication) ne sert à rien ici. L'ajouter aurait
été de la sur-ingénierie pour l'audience réelle de ce projet.

## 2. Catégorisation par règles de mots-clés, pas par ML

**Contexte** : classer une transaction dans une catégorie de dépense à
partir de sa description.

**Décision** : une liste ordonnée de règles `(mot-clé, catégorie)`,
évaluées dans l'ordre — la première qui correspond gagne.

**Écarté** : un modèle de classification (même simple, type régression
logistique sur un encodage du texte). Avec une dizaine de catégories et des
descriptions courtes et répétitives (toujours "IGA MONTREAL", jamais une
formulation libre), les règles couvrent le problème réel sans le risque de
faux négatifs silencieux d'un modèle probabiliste. Un ML mal justifié ici
aurait été un signal *négatif* : sur-ingénierie plutôt que jugement.

**Piège vécu** : `"paiement"` contient `"paie"` comme sous-chaîne. Avec
`"paie"` placé avant `"paiement recu"` dans la liste, un paiement de carte
de crédit ("PAIEMENT RECU - MERCI") se faisait intercepter et compter comme
un revenu — gonflant le total affiché de 200 $. Trouvé en creusant les
chiffres avant de construire le premier visuel, pas par accident. Corrigé
en plaçant les mots-clés multi-mots plus spécifiques avant les génériques,
et documenté comme invariant du module (`src/categorize.py`) avec un test
de non-régression dédié.

## 3. Convention de signe interne, et son exception

**Décision** : `amount > 0` = argent qui entre, `amount < 0` = argent qui
sort — peu importe le type de compte.

**Piège réel** : un relevé de carte de crédit inverse cette logique sur
son format brut — un achat y est positif (il augmente la dette), un
paiement y est négatif (il la réduit). Ingérer ça sans y penser aurait
compté chaque achat comme un revenu. Le signe est donc inversé à
l'ingestion pour les deux formats de Carte Nordik (`src/ingest.py`), avec
le raisonnement complet documenté dans le docstring du module — c'est le
genre de détail qui semble évident une fois vu, et qui casse tout
silencieusement si on ne le voit pas.

## 4. Un changement de format à mi-année, pas un détecteur universel

**Contexte** : en juillet 2026, Carte Nordik change son export (délimiteur,
format de date, décimale, noms de colonnes) — un scénario réaliste de
modernisation d'un système bancaire.

**Décision** : deux fichiers, deux fonctions de parsing
(`parse_carte_nordik_h1`, `parse_carte_nordik_h2`), assemblés dans
`src/pipeline.py` pour alimenter le même compte.

**Écarté** : un détecteur de format unique qui inspecterait chaque ligne
et choisirait dynamiquement comment la parser. Plus "élégant" en apparence,
mais ça cache la vraie nature du problème — deux relevés distincts, reçus
à des moments différents, jamais mélangés dans un seul fichier en
pratique. Le pipeline absorbe le changement, le schéma relationnel n'a pas
à le savoir.

## 5. Rejeter en comptant, ni planter ni ignorer en silence

**Contexte** : des lignes réellement mal formées existent dans les
données (montant illisible, ni débit ni crédit renseigné).

**Décision** : chaque parseur filtre ces lignes, compte combien, et
imprime un avertissement (`⚠️  N ligne(s) ignorée(s) ... : raison`) plutôt
que de les traiter comme un montant de 0 $ (faux et invisible) ou de
laisser planter tout le chargement (fragile — une seule ligne pourrie
bloquerait tout un mois de données).

**Le même principe s'applique aux doublons** : `src/pipeline._dedupliquer`
retire les transactions identiques (même date, description, montant) après
assemblage de tous les fichiers d'un compte, et rapporte combien ont été
retirées.

## 6. Piège Power BI : `RELATED()` dans un filtre `CALCULATE`

**Contexte** : un graphique à barres des dépenses par catégorie, avec
`categories[name]` en axe.

**Piège vécu** : la première version de la mesure utilisait
`RELATED(categories[name]) <> "Virement"` comme argument-filtre de
`CALCULATE`. Résultat : chaque barre affichait le même total global au
lieu du montant propre à sa catégorie — `RELATED()` a besoin d'un contexte
de ligne que cet argument-filtre ne fournit pas de la même façon.

**Correctif** : filtrer directement sur `categories[name]` (pas via
`RELATED`) au niveau du *visuel* plutôt que dans la mesure — `CALCULATE`
propage nativement ce filtre à travers une relation active, sans le piège
de contexte.

## 7. Piège Power Query : le typage silencieux

**Piège vécu** : deux bugs de type distincts ont produit la même erreur
DAX ("comparaison Texte contre Entier") — d'abord `categories.id` importé
en Texte au lieu d'Entier (rompant la relation avec `transactions.category_id`),
puis `transactions.amount` importé en Texte à cause d'un conflit de
paramètres régionaux (données sources en point décimal, Power BI en
français avec virgule décimale). Le correctif du deuxième cas nécessite un
type explicite avec paramètres régionaux forcés en anglais (États-Unis),
pas une simple conversion de type.

**Leçon générale** : dans Power Query, ne jamais assumer qu'une colonne a
le type qu'elle semble avoir — vérifier l'icône de type sur chaque colonne
importée d'une source externe, surtout quand la locale de la machine ne
correspond pas au format des données sources.
