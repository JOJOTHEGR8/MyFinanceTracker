"""Test bout-en-bout : construit la base à partir des vrais relevés de
data/raw/ (une année complète, avec doublons et lignes mal formées injectés
volontairement) et vérifie que le pipeline absorbe correctement ce désordre :
rien de perdu silencieusement, les doublons et lignes invalides sont
comptés, et une seule transaction reste légitimement non catégorisée (celle
à description manquante)."""
import sqlite3

from src.ingest import parse_caisse_aurore, parse_carte_nordik_h2
from src.pipeline import RAW_DIR, _dedupliquer, build_database, print_summary


def test_build_database_drops_duplicates_and_unreadable_rows(tmp_path):
    db_path = tmp_path / "test_finance.db"
    build_database(db_path)

    conn = sqlite3.connect(db_path)
    try:
        total = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        # 264 lignes valides au total dans data/raw/, moins 2 doublons exacts
        # (un dans banque_boreale, un dans carte_nordik h2) retirés par le
        # pipeline. Les 2 lignes à montant illisible sont déjà exclues par
        # les parseurs (voir tests/test_ingest.py), donc pas comptées ici.
        assert total == 262
    finally:
        conn.close()


def test_build_database_has_exactly_one_uncategorized_transaction(tmp_path):
    db_path = tmp_path / "test_finance.db"
    build_database(db_path)

    conn = sqlite3.connect(db_path)
    try:
        non_categorisees = conn.execute(
            "SELECT description FROM transactions WHERE category_id IS NULL"
        ).fetchall()
        # La seule transaction non catégorisée attendue est celle dont la
        # description est manquante à la source (voir test_ingest.py) —
        # toute autre non-catégorisée serait un vrai trou dans les règles.
        assert non_categorisees == [("(description manquante)",)]
    finally:
        conn.close()


def test_build_database_epargne_balance_matches_source_sum(tmp_path):
    # Recalcule le solde indépendamment à partir du parseur, plutôt que de
    # coder en dur un montant — les données étant générées avec une
    # variation aléatoire, un chiffre figé casserait au moindre ajustement
    # du générateur sans que ce soit un vrai bug.
    attendu = sum(t.amount for t in parse_caisse_aurore(RAW_DIR / "caisse_aurore_epargne.csv"))

    db_path = tmp_path / "test_finance.db"
    build_database(db_path)
    conn = sqlite3.connect(db_path)
    try:
        solde = conn.execute(
            """
            SELECT SUM(t.amount)
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            WHERE a.account_name = 'Épargne'
            """
        ).fetchone()[0]
        assert round(solde, 2) == round(attendu, 2)
    finally:
        conn.close()


def test_dedupliquer_removes_exact_duplicates_only():
    transactions = parse_carte_nordik_h2(RAW_DIR / "carte_nordik_credit_2026_h2.csv")
    uniques, doublons = _dedupliquer(transactions)
    assert doublons == 1
    assert len(uniques) == len(transactions) - 1


def test_print_summary_runs_without_error(tmp_path, capsys):
    # Garde-fou contre les requêtes SQL qui ne cassent qu'à l'exécution
    # (ex. un ORDER BY sur un alias absent) — jamais couvertes par un test
    # qui ne regarde que les données, pas le rapport affiché.
    db_path = tmp_path / "test_finance.db"
    build_database(db_path)
    print_summary(db_path)
    output = capsys.readouterr().out
    assert "Épicerie" in output
    assert "Restaurant" in output
