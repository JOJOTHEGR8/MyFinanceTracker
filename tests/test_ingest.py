"""Tests des parseurs par institution — en particulier la conversion de
signe de la carte de crédit, le point le plus piégeux de l'ingestion
(voir le docstring de src/ingest.py pour le raisonnement complet)."""
from pathlib import Path

from src.ingest import parse_banque_boreale, parse_caisse_aurore, parse_carte_nordik

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def test_parse_banque_boreale_debit_becomes_negative():
    transactions = parse_banque_boreale(RAW_DIR / "banque_boreale_compte_cheque.csv")
    iga = next(t for t in transactions if t.description == "IGA MONTREAL" and t.date == "2026-09-01")
    assert iga.amount == -45.20


def test_parse_banque_boreale_credit_stays_positive_and_date_is_iso():
    transactions = parse_banque_boreale(RAW_DIR / "banque_boreale_compte_cheque.csv")
    paie = next(t for t in transactions if "PAIE" in t.description)
    assert paie.amount == 1850.00
    assert paie.date == "2026-09-02"


def test_parse_caisse_aurore_keeps_source_sign():
    transactions = parse_caisse_aurore(RAW_DIR / "caisse_aurore_epargne.csv")
    retrait = next(t for t in transactions if "Retrait" in t.description)
    assert retrait.amount == -200.00


def test_parse_carte_nordik_inverts_purchase_to_expense():
    transactions = parse_carte_nordik(RAW_DIR / "carte_nordik_credit.csv")
    achat = next(t for t in transactions if "UBER EATS" in t.description)
    assert achat.amount == -28.50


def test_parse_carte_nordik_inverts_payment_to_positive():
    transactions = parse_carte_nordik(RAW_DIR / "carte_nordik_credit.csv")
    paiement = next(t for t in transactions if "PAIEMENT RECU" in t.description)
    assert paiement.amount == 200.00


def test_parse_carte_nordik_handles_comma_decimal_and_iso_date():
    transactions = parse_carte_nordik(RAW_DIR / "carte_nordik_credit.csv")
    amazon = next(t for t in transactions if "AMAZON" in t.description)
    assert amazon.amount == -89.99
    assert amazon.date == "2026-09-06"
