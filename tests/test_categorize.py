"""Tests de la logique de catégorisation par mots-clés."""
import csv
from pathlib import Path

from src.categorize import DEFAULT_RULES, categorize, normalize

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def test_categorize_basic_match_is_case_insensitive():
    assert categorize("iga montreal", DEFAULT_RULES) == "Épicerie"
    assert categorize("IGA MONTREAL", DEFAULT_RULES) == "Épicerie"


def test_categorize_handles_accents():
    assert normalize("Intérêt") == "interet"


def test_categorize_no_match_returns_none():
    assert categorize("TRANSACTION INCONNUE 12345", DEFAULT_RULES) is None


def test_categorize_empty_description_returns_none():
    assert categorize("", DEFAULT_RULES) is None


def test_categorize_credit_card_payment_is_not_confused_with_salary():
    # Régression : "paiement" contient "paie" comme sous-chaîne. Un paiement
    # de carte de crédit ne doit jamais être catégorisé comme un revenu.
    assert categorize("PAIEMENT RECU - MERCI", DEFAULT_RULES) == "Virement"
    assert categorize("DEPOT PAIE EMPLOYEUR XYZ", DEFAULT_RULES) == "Revenu"


def test_categorize_first_matching_rule_wins_on_ambiguity():
    # Description fictive contenant volontairement deux mots-clés : l'ordre
    # des règles doit trancher, pas un hasard d'itération sur un dict.
    rules = [("iga", "Épicerie"), ("station service", "Transport")]
    assert categorize("IGA STATION SERVICE", rules) == "Épicerie"


def test_default_rules_cover_every_demo_transaction():
    """Garde-fou : si une transaction de démo n'a pas de règle correspondante,
    ce test casse plutôt que de la laisser silencieusement non catégorisée
    dans le tableau de bord final.

    Trois exceptions attendues, correspondant aux défauts de données
    injectés volontairement (voir scripts/generate_demo_data.py) : une
    description vide et deux lignes de transaction avortée, toutes trois
    exclues du chargement par src/ingest.py avant même d'atteindre la
    catégorisation — les voir ici confirme juste qu'elles existent bien
    dans les données brutes."""
    exceptions_attendues = {"", "TRANSACTION INCOMPLETE", "TRANSACTION EN ATTENTE"}
    sources = [
        (RAW_DIR / "banque_boreale_compte_cheque.csv", ",", "Description"),
        (RAW_DIR / "caisse_aurore_epargne.csv", ",", "Description"),
        (RAW_DIR / "carte_nordik_credit_2026_h1.csv", ";", "DESCRIPTION"),
        (RAW_DIR / "carte_nordik_credit_2026_h2.csv", ",", "Merchant"),
    ]
    uncovered = []
    for csv_file, delimiter, colonne in sources:
        with csv_file.open(encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=delimiter):
                description = row[colonne]
                if description not in exceptions_attendues and categorize(description, DEFAULT_RULES) is None:
                    uncovered.append(description)
    assert not uncovered, f"Descriptions non catégorisées : {uncovered}"
