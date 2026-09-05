"""Parseurs par institution : chaque relevé source, dans son propre format,
est normalisé vers le même schéma de transaction interne.

Convention de signe interne : amount > 0 = argent qui entre (revenu, dépôt,
virement reçu) ; amount < 0 = argent qui sort (dépense, retrait, achat).

Pour un compte chèque ou épargne, cette convention correspond directement
à la sémantique "débit/crédit" du relevé. Pour une carte de crédit, c'est
l'inverse sur le relevé brut : un achat y est positif (il augmente ce que
tu dois), un paiement y est négatif (il réduit ce que tu dois). Comme ici
on mesure des *dépenses*, pas un solde de carte, le signe est inversé à
l'ingestion : un achat devient une sortie d'argent (négatif), un paiement
devient positif. Ce paiement n'est pas un revenu — c'est un virement interne
(argent déjà compté comme dépense ailleurs, ex. dans le compte chèque) —
il est donc catégorisé "Virement" et exclu des totaux de dépenses par le
rapport (src/pipeline.py), pas par une manipulation supplémentaire du signe.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class RawTransaction:
    date: str  # ISO 8601 (YYYY-MM-DD)
    description: str
    amount: float


def _to_transactions(dates: pd.Series, descriptions: pd.Series, amounts: pd.Series) -> list[RawTransaction]:
    return [
        RawTransaction(date, description.strip(), float(amount))
        for date, description, amount in zip(dates, descriptions, amounts)
    ]


def parse_banque_boreale(path: Path) -> list[RawTransaction]:
    """Format : virgule, JJ/MM/AAAA, colonnes Debit/Credit séparées."""
    df = pd.read_csv(path)
    dates = pd.to_datetime(df["Date"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
    amounts = df["Credit"].fillna(0.0) - df["Debit"].fillna(0.0)
    return _to_transactions(dates, df["Description"], amounts)


def parse_caisse_aurore(path: Path) -> list[RawTransaction]:
    """Format : virgule, AAAA-MM-JJ, colonne Amount déjà signée (convention
    déjà alignée sur la nôtre — aucune inversion nécessaire)."""
    df = pd.read_csv(path)
    dates = pd.to_datetime(df["Transaction Date"], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")
    return _to_transactions(dates, df["Description"], df["Amount"])


def parse_carte_nordik(path: Path) -> list[RawTransaction]:
    """Format : point-virgule, JJ/MM/AAAA, virgule décimale, colonne MONTANT
    signée avec une convention inversée (voir docstring du module).

    `decimal=","` fait gérer la virgule décimale par pandas directement,
    plutôt que de bricoler un `.replace(",", ".")` sur des chaînes.
    """
    df = pd.read_csv(path, sep=";", decimal=",")
    dates = pd.to_datetime(df["DATE_TRANSACTION"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
    return _to_transactions(dates, df["DESCRIPTION"], -df["MONTANT"])
