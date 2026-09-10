"""Orchestration : construit finance.db à partir des relevés de data/raw/.

Usage : python -m src.pipeline
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from src.categorize import DEFAULT_RULES, categorize
from src.ingest import (
    RawTransaction,
    parse_banque_boreale,
    parse_caisse_aurore,
    parse_carte_nordik_h1,
    parse_carte_nordik_h2,
)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "finance.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
RAW_DIR = ROOT / "data" / "raw"

# (institution, nom du compte, type de compte, [(fichier source, parseur), ...])
# Carte Nordik a deux fichiers : son export a changé de format le 1er juillet
# 2026 (voir docstring de src/ingest.py). Les deux alimentent le même compte.
SOURCES = [
    ("Banque Boréale", "Compte chèque", "cheque", [
        ("banque_boreale_compte_cheque.csv", parse_banque_boreale),
    ]),
    ("Caisse Aurore", "Épargne", "epargne", [
        ("caisse_aurore_epargne.csv", parse_caisse_aurore),
    ]),
    ("Carte Nordik", "Carte de crédit", "carte_credit", [
        ("carte_nordik_credit_2026_h1.csv", parse_carte_nordik_h1),
        ("carte_nordik_credit_2026_h2.csv", parse_carte_nordik_h2),
    ]),
]


def _dedupliquer(transactions: list[RawTransaction]) -> tuple[list[RawTransaction], int]:
    """Retire les doublons exacts (même date, description et montant) —
    ça arrive en vrai quand un export bancaire chevauche deux téléchargements.
    Garde la première occurrence, compte le reste."""
    vues: set[tuple[str, str, float]] = set()
    uniques = []
    doublons = 0
    for tx in transactions:
        cle = (tx.date, tx.description, tx.amount)
        if cle in vues:
            doublons += 1
            continue
        vues.add(cle)
        uniques.append(tx)
    return uniques, doublons


def build_database(db_path: Path = DB_PATH) -> None:
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        category_ids = _seed_categories(conn)
        _seed_category_rules(conn, category_ids)

        for institution_name, account_name, account_type, sources in SOURCES:
            institution_id = _insert_institution(conn, institution_name)
            account_id = _insert_account(conn, institution_id, account_name, account_type)

            transactions: list[RawTransaction] = []
            for filename, parser in sources:
                transactions.extend(parser(RAW_DIR / filename))

            transactions, doublons = _dedupliquer(transactions)
            if doublons:
                print(f"⚠️  {doublons} transaction(s) dupliquée(s) ignorée(s) pour {account_name}")

            for tx in transactions:
                category_name = categorize(tx.description, DEFAULT_RULES)
                category_id = category_ids.get(category_name) if category_name else None
                conn.execute(
                    "INSERT INTO transactions (account_id, date, description, amount, category_id) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (account_id, tx.date, tx.description, tx.amount, category_id),
                )
        conn.commit()
    finally:
        conn.close()


def _seed_categories(conn: sqlite3.Connection) -> dict[str, int]:
    names = sorted({category for _, category in DEFAULT_RULES})
    return {name: conn.execute("INSERT INTO categories (name) VALUES (?)", (name,)).lastrowid for name in names}


def _seed_category_rules(conn: sqlite3.Connection, category_ids: dict[str, int]) -> None:
    for keyword, category in DEFAULT_RULES:
        conn.execute(
            "INSERT INTO category_rules (keyword, category_id) VALUES (?, ?)",
            (keyword, category_ids[category]),
        )


def _insert_institution(conn: sqlite3.Connection, name: str) -> int:
    return conn.execute("INSERT INTO institutions (name) VALUES (?)", (name,)).lastrowid


def _insert_account(conn: sqlite3.Connection, institution_id: int, account_name: str, account_type: str) -> int:
    cur = conn.execute(
        "INSERT INTO accounts (institution_id, account_name, account_type) VALUES (?, ?, ?)",
        (institution_id, account_name, account_type),
    )
    return cur.lastrowid


def print_summary(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        print("=== Solde par compte ===")
        for institution, account, solde in conn.execute(
            """
            SELECT i.name, a.account_name, SUM(t.amount)
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            JOIN institutions i ON i.id = a.institution_id
            GROUP BY a.id
            ORDER BY i.name
            """
        ):
            print(f"  {institution} — {account} : {solde:,.2f} $")

        print("\n=== Dépenses par catégorie (hors Virement) ===")
        for category, total in conn.execute(
            """
            SELECT c.name, SUM(-t.amount) AS total
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.amount < 0 AND c.name != 'Virement'
            GROUP BY c.name
            ORDER BY total DESC
            """
        ):
            print(f"  {category} : {total:,.2f} $")

        non_categorisees = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE category_id IS NULL"
        ).fetchone()[0]
        if non_categorisees:
            print(f"\n⚠️  {non_categorisees} transaction(s) non catégorisée(s)")
    finally:
        conn.close()


if __name__ == "__main__":
    build_database()
    print(f"Base construite : {DB_PATH}\n")
    print_summary()
