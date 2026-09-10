"""Tests des parseurs par institution — la conversion de signe de la carte
de crédit, le changement de format à mi-année, et la défense contre les
lignes mal formées (voir le docstring de src/ingest.py).

Les montants sont générés avec une variation aléatoire (scripts/generate_demo_data.py) :
on teste donc des propriétés (signe, présence, comptage) plutôt que des
valeurs exactes, sauf pour les lignes à défaut injectées à des dates fixes.
"""
from pathlib import Path

from src.ingest import (
    parse_banque_boreale,
    parse_caisse_aurore,
    parse_carte_nordik_h1,
    parse_carte_nordik_h2,
)

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def test_parse_banque_boreale_debit_becomes_negative():
    transactions = parse_banque_boreale(RAW_DIR / "banque_boreale_compte_cheque.csv")
    iga = [t for t in transactions if "IGA" in t.description]
    assert iga
    assert all(t.amount < 0 for t in iga)


def test_parse_banque_boreale_credit_stays_positive():
    transactions = parse_banque_boreale(RAW_DIR / "banque_boreale_compte_cheque.csv")
    paie = [t for t in transactions if "PAIE" in t.description]
    assert paie
    assert all(t.amount > 0 for t in paie)


def test_parse_banque_boreale_drops_row_with_no_amount():
    # La ligne "TRANSACTION INCOMPLETE" (ni débit ni crédit renseigné) doit
    # être ignorée, pas traitée comme un montant de 0 $.
    transactions = parse_banque_boreale(RAW_DIR / "banque_boreale_compte_cheque.csv")
    assert not any(t.description == "TRANSACTION INCOMPLETE" for t in transactions)


def test_parse_banque_boreale_fills_missing_description():
    transactions = parse_banque_boreale(RAW_DIR / "banque_boreale_compte_cheque.csv")
    # Sélection par date ET montant : la date seule peut coïncider par hasard
    # avec une autre transaction générée aléatoirement le même jour.
    ligne = next(t for t in transactions if t.date == "2026-06-18" and t.amount == -12.34)
    assert ligne.description == "(description manquante)"


def test_parse_caisse_aurore_keeps_source_sign():
    transactions = parse_caisse_aurore(RAW_DIR / "caisse_aurore_epargne.csv")
    retraits = [t for t in transactions if "Retrait" in t.description]
    assert retraits
    assert all(t.amount < 0 for t in retraits)


def test_parse_carte_nordik_h1_inverts_purchase_to_expense():
    transactions = parse_carte_nordik_h1(RAW_DIR / "carte_nordik_credit_2026_h1.csv")
    achats = [t for t in transactions if "UBER EATS" in t.description]
    assert achats
    assert all(t.amount < 0 for t in achats)


def test_parse_carte_nordik_h1_inverts_payment_to_positive():
    transactions = parse_carte_nordik_h1(RAW_DIR / "carte_nordik_credit_2026_h1.csv")
    paiements = [t for t in transactions if "PAIEMENT RECU" in t.description]
    assert paiements
    assert all(t.amount > 0 for t in paiements)


def test_parse_carte_nordik_h1_drops_unreadable_amount():
    # La ligne "TRANSACTION EN ATTENTE;N/D" doit être ignorée, pas planter
    # tout le chargement.
    transactions = parse_carte_nordik_h1(RAW_DIR / "carte_nordik_credit_2026_h1.csv")
    assert not any(t.description == "TRANSACTION EN ATTENTE" for t in transactions)


def test_parse_carte_nordik_h2_reads_new_format_with_same_sign_convention():
    # Nouveau format (virgule, AAAA-MM-JJ, point décimal, en-têtes
    # Date/Merchant/Amount) — même convention de signe que l'ancien format.
    transactions = parse_carte_nordik_h2(RAW_DIR / "carte_nordik_credit_2026_h2.csv")
    achats = [t for t in transactions if "UBER EATS" in t.description]
    paiements = [t for t in transactions if "PAIEMENT RECU" in t.description]
    assert achats and all(t.amount < 0 for t in achats)
    assert paiements and all(t.amount > 0 for t in paiements)
    assert all(t.date.startswith("2026-") for t in transactions)
