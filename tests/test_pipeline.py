"""Test bout-en-bout : construit la base à partir des vrais relevés de
data/raw/ et vérifie que l'ensemble tient debout (pas de transaction perdue,
pas de non-catégorisée, solde cohérent)."""
import sqlite3

from src.pipeline import build_database, print_summary


def test_build_database_categorizes_every_transaction(tmp_path):
    db_path = tmp_path / "test_finance.db"
    build_database(db_path)

    conn = sqlite3.connect(db_path)
    try:
        total, non_categorisees = conn.execute(
            "SELECT COUNT(*), SUM(CASE WHEN category_id IS NULL THEN 1 ELSE 0 END) FROM transactions"
        ).fetchone()
        assert total == 24  # 10 + 4 + 10 transactions dans data/raw/
        assert non_categorisees == 0
    finally:
        conn.close()


def test_build_database_computes_expected_balance_for_epargne(tmp_path):
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
        assert solde == 500.00 + 4.12 - 200.00 + 300.00
    finally:
        conn.close()


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
