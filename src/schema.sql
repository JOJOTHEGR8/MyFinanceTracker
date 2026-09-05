-- Schéma normalisé : une institution a plusieurs comptes, un compte a plusieurs
-- transactions, une transaction est rattachée à au plus une catégorie via une
-- règle de mot-clé. C'est la cible commune vers laquelle convergent des
-- relevés d'institutions aux formats tous différents (voir data/raw/).

CREATE TABLE IF NOT EXISTS institutions (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS accounts (
    id              INTEGER PRIMARY KEY,
    institution_id  INTEGER NOT NULL REFERENCES institutions(id),
    account_name    TEXT NOT NULL,
    account_type    TEXT NOT NULL CHECK (account_type IN ('cheque', 'epargne', 'carte_credit')),
    UNIQUE (institution_id, account_name)
);

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Une catégorie peut avoir plusieurs mots-clés déclencheurs (ex. "essence" et
-- "petro-canada" -> Transport).
CREATE TABLE IF NOT EXISTS category_rules (
    id          INTEGER PRIMARY KEY,
    keyword     TEXT NOT NULL UNIQUE,
    category_id INTEGER NOT NULL REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id            INTEGER PRIMARY KEY,
    account_id    INTEGER NOT NULL REFERENCES accounts(id),
    date          TEXT NOT NULL,  -- ISO 8601 (YYYY-MM-DD), normalisée à l'ingestion
    description   TEXT NOT NULL,
    amount        REAL NOT NULL,  -- positif = crédit, négatif = débit
    category_id   INTEGER REFERENCES categories(id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
