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

Carte Nordik a changé de format le 1er juillet 2026 (modernisation de son
export bancaire) : parse_carte_nordik_h1 lit l'ancien format (point-virgule,
JJ/MM/AAAA, virgule décimale), parse_carte_nordik_h2 le nouveau (virgule,
AAAA-MM-JJ, point décimal, en-têtes renommés). Les deux alimentent le même
compte dans src/pipeline.py — c'est le pipeline, pas le schéma, qui absorbe
ce genre de changement du monde réel.

Défense contre les lignes mal formées : une ligne dont le montant est
illisible (ex. "N/D") ou dont ni débit ni crédit n'est renseigné est
ignorée et comptée, plutôt que de faire planter tout le chargement ou de
la traiter silencieusement comme un montant de 0 $. Une description
manquante n'empêche pas la transaction d'être chargée — elle reste
simplement non catégorisable.
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


DESCRIPTION_MANQUANTE = "(description manquante)"


def _to_transactions(dates: pd.Series, descriptions: pd.Series, amounts: pd.Series) -> list[RawTransaction]:
    return [
        RawTransaction(date, description.strip(), float(amount))
        for date, description, amount in zip(dates, descriptions, amounts)
    ]


def _signaler_lignes_ignorees(path: Path, nb_ignorees: int, raison: str) -> None:
    if nb_ignorees:
        print(f"⚠️  {nb_ignorees} ligne(s) ignorée(s) dans {path.name} : {raison}")


def parse_banque_boreale(path: Path) -> list[RawTransaction]:
    """Format : virgule, JJ/MM/AAAA, colonnes Debit/Credit séparées."""
    df = pd.read_csv(path)

    valide = ~(df["Debit"].isna() & df["Credit"].isna())
    _signaler_lignes_ignorees(path, (~valide).sum(), "ni débit ni crédit renseigné")
    df = df[valide]

    dates = pd.to_datetime(df["Date"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
    amounts = df["Credit"].fillna(0.0) - df["Debit"].fillna(0.0)
    descriptions = df["Description"].fillna(DESCRIPTION_MANQUANTE)
    return _to_transactions(dates, descriptions, amounts)


def parse_caisse_aurore(path: Path) -> list[RawTransaction]:
    """Format : virgule, AAAA-MM-JJ, colonne Amount déjà signée (convention
    déjà alignée sur la nôtre — aucune inversion nécessaire)."""
    df = pd.read_csv(path)
    dates = pd.to_datetime(df["Transaction Date"], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")
    return _to_transactions(dates, df["Description"], df["Amount"])


def parse_carte_nordik_h1(path: Path) -> list[RawTransaction]:
    """Ancien format (jusqu'au 30 juin 2026) : point-virgule, JJ/MM/AAAA,
    virgule décimale, colonne MONTANT signée avec convention inversée
    (voir docstring du module)."""
    df = pd.read_csv(path, sep=";", dtype={"MONTANT": str})
    dates = pd.to_datetime(df["DATE_TRANSACTION"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
    montants = pd.to_numeric(df["MONTANT"].str.replace(",", "."), errors="coerce")

    valide = montants.notna()
    _signaler_lignes_ignorees(path, (~valide).sum(), "montant illisible")

    return _to_transactions(dates[valide], df["DESCRIPTION"][valide], -montants[valide])


def parse_carte_nordik_h2(path: Path) -> list[RawTransaction]:
    """Nouveau format (à partir du 1er juillet 2026, après modernisation de
    l'export) : virgule, AAAA-MM-JJ, point décimal, en-têtes Date/Merchant/
    Amount. Même convention de signe inversée que l'ancien format."""
    df = pd.read_csv(path)
    dates = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")
    return _to_transactions(dates, df["Merchant"], -df["Amount"])
