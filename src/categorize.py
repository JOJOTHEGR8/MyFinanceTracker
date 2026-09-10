"""Catégorisation de transactions par règles de mots-clés.

Priorité : la première règle de la liste dont le mot-clé apparaît dans la
description (normalisée : minuscules, sans accents) l'emporte. L'ordre de
DEFAULT_RULES est donc significatif — pas de conflit dans les données de
démo, mais un mot-clé plus spécifique doit être placé avant un générique
s'il y a chevauchement.
"""
from __future__ import annotations

import unicodedata

Rule = tuple[str, str]  # (mot-clé, catégorie)

DEFAULT_RULES: list[Rule] = [
    ("uber eats", "Restaurant"),
    ("banquise", "Restaurant"),
    ("st-hubert", "Restaurant"),
    ("tim hortons", "Restaurant"),
    ("station service", "Transport"),
    ("essence", "Transport"),
    ("ultramar", "Transport"),
    ("iga", "Épicerie"),
    ("metro", "Épicerie"),
    ("netflix", "Abonnements"),
    ("spotify", "Abonnements"),
    ("loyer", "Logement"),
    # "paiement recu" doit être vérifié avant "paie" : "paiement" contient
    # "paie" comme sous-chaîne, donc l'ordre inverse ferait passer un
    # paiement de carte de crédit pour un revenu.
    ("paiement recu", "Virement"),
    ("interac", "Virement"),
    ("virement", "Virement"),
    ("retrait guichet", "Virement"),
    ("paie", "Revenu"),
    ("interet", "Revenu"),
    ("pharmaprix", "Santé"),
    ("pharmacie", "Santé"),
    ("saq", "Loisirs"),
    ("cineplex", "Loisirs"),
    ("amazon", "Achats"),
    ("la baie", "Achats"),
]


def normalize(text: str) -> str:
    """Minuscules, sans accents — pour un matching robuste aux variations
    d'encodage entre relevés (ex. "Intérêt" vs "INTERET")."""
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return ascii_only.lower()


def categorize(description: str, rules: list[Rule] = DEFAULT_RULES) -> str | None:
    """Retourne le nom de la première catégorie dont un mot-clé apparaît
    dans la description, ou None si aucune règle ne correspond."""
    normalized_description = normalize(description)
    for keyword, category in rules:
        if normalize(keyword) in normalized_description:
            return category
    return None
