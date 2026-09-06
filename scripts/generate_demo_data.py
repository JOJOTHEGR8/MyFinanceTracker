"""Génère les relevés synthétiques de data/raw/ pour une année complète (2026).

Ce script n'est PAS exécuté par le pipeline (src/pipeline.py) — c'est un
utilitaire à usage unique pour produire des données de démo réalistes, avec
seed fixe pour la reproductibilité. Les fichiers générés sont commités tels
quels dans data/raw/, comme s'ils étaient de vrais exports bancaires reçus.

Inclut volontairement :
- une saisonnalité modeste (achats/cadeaux en hausse en décembre)
- un changement de format à mi-année pour Carte Nordik (simule une
  institution qui modernise son export bancaire en juillet)
- des défauts de données réels : doublons exacts, description vide,
  montant illisible — documentés ligne par ligne ci-dessous

Usage : python scripts/generate_demo_data.py
"""
from __future__ import annotations

import random
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
random.seed(42)

MOIS = range(1, 13)


def jour(mois: int, jour_du_mois: int) -> str:
    return f"{jour_du_mois:02d}/{mois:02d}/2026"


def jour_iso(mois: int, jour_du_mois: int) -> str:
    return f"2026-{mois:02d}-{jour_du_mois:02d}"


def montant(base: float, variation: float) -> float:
    return round(base + random.uniform(-variation, variation), 2)


# --------------------------------------------------------------------------
# Banque Boréale — compte chèque (format inchangé toute l'année)
# --------------------------------------------------------------------------

NOMS_MOIS = [
    "JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN",
    "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE",
]


def generer_banque_boreale() -> list[str]:
    lignes = ["Date,Description,Debit,Credit"]
    epiceries = ["IGA MONTREAL", "METRO"]
    for m in MOIS:
        lignes.append(f"{jour(m, 2)},DEPOT PAIE EMPLOYEUR XYZ,,{montant(1850, 40):.2f}")
        lignes.append(f"{jour(m, 7)},LOYER {NOMS_MOIS[m - 1]},{montant(950, 15):.2f},")
        for _ in range(random.randint(3, 5)):
            j = random.randint(3, 27)
            lignes.append(f"{jour(m, j)},{random.choice(epiceries)},{montant(55, 25):.2f},")
        lignes.append(f"{jour(m, random.randint(4, 10))},ESSO STATION SERVICE,{montant(55, 12):.2f},")
        if random.random() < 0.5:
            lignes.append(f"{jour(m, random.randint(10, 20))},ULTRAMAR,{montant(48, 10):.2f},")
        lignes.append(f"{jour(m, random.randint(1, 28))},NETFLIX.COM,16.99,")
        if random.random() < 0.6:
            lignes.append(f"{jour(m, random.randint(1, 28))},PHARMACIE JEAN COUTU,{montant(25, 12):.2f},")
        if random.random() < 0.4:
            lignes.append(f"{jour(m, random.randint(1, 28))},RESTAURANT LA BANQUISE,{montant(40, 15):.2f},")
        if random.random() < 0.5:
            lignes.append(f"{jour(m, random.randint(1, 28))},VIREMENT INTERAC RECU,,{montant(60, 30):.2f}")
        if random.random() < 0.5:
            lignes.append(f"{jour(m, random.randint(1, 28))},VIREMENT INTERAC ENVOYE,{montant(30, 15):.2f},")

    # --- Défauts de données injectés volontairement ---
    # 1) Doublon exact (même ligne répétée deux fois) : une transaction IGA de mars.
    ligne_dupliquee = f"{jour(3, 14)},IGA MONTREAL,61.40,"
    lignes.append(ligne_dupliquee)
    lignes.append(ligne_dupliquee)
    # 2) Description vide (ex. un paiement terminal sans nom de marchand transmis).
    lignes.append(f"{jour(6, 18)},,12.34,")
    # 3) Montant illisible (ni Debit ni Credit rempli — ligne d'export incomplète).
    lignes.append(f"{jour(8, 22)},TRANSACTION INCOMPLETE,,")

    return lignes


# --------------------------------------------------------------------------
# Caisse Aurore — épargne (format inchangé toute l'année)
# --------------------------------------------------------------------------

def generer_caisse_aurore() -> list[str]:
    lignes = ["Transaction Date,Description,Amount"]
    for m in MOIS:
        lignes.append(f"{jour_iso(m, 1)},Virement depuis compte cheque,{montant(400, 100):.2f}")
        lignes.append(f"{jour_iso(m, 3)},Interet mensuel,{montant(4, 1.5):.2f}")
        if random.random() < 0.3:
            lignes.append(f"{jour_iso(m, random.randint(10, 25))},Retrait guichet,-{montant(150, 60):.2f}")
    return lignes


# --------------------------------------------------------------------------
# Carte Nordik — carte de crédit
# H1 (janvier-juin) : ancien format (point-virgule, virgule décimale)
# H2 (juillet-décembre) : nouveau format après modernisation de l'export
# --------------------------------------------------------------------------

def generer_carte_nordik_h1() -> list[str]:
    lignes = ["DATE_TRANSACTION;DESCRIPTION;MONTANT"]
    for m in range(1, 7):
        for _ in range(random.randint(3, 5)):
            j = random.randint(1, 27)
            marchand = random.choice(["UBER EATS", "RESTAURANT ST-HUBERT", "TIM HORTONS"])
            lignes.append(f"{jour(m, j)};{marchand};{montant(30, 15):.2f}".replace(".", ","))
        lignes.append(f"{jour(m, random.randint(1, 27))};ESSO STATION SERVICE;{montant(58, 10):.2f}".replace(".", ","))
        lignes.append(f"{jour(m, random.randint(1, 27))};ABONNEMENT SPOTIFY;10,99")
        if random.random() < 0.5:
            lignes.append(f"{jour(m, random.randint(1, 27))};SAQ SUCCURSALE 1234;{montant(45, 15):.2f}".replace(".", ","))
        lignes.append(f"{jour(m, random.randint(1, 27))};PAIEMENT RECU - MERCI;-{montant(200, 50):.2f}".replace(".", ","))

    # Défaut : montant illisible (le système d'export a buté sur une transaction en attente).
    lignes.append(f"{jour(4, 19)};TRANSACTION EN ATTENTE;N/D")

    return lignes


def generer_carte_nordik_h2() -> list[str]:
    lignes = ["Date,Merchant,Amount"]
    for m in range(7, 13):
        for _ in range(random.randint(3, 5)):
            j = random.randint(1, 27)
            marchand = random.choice(["UBER EATS", "RESTAURANT ST-HUBERT", "TIM HORTONS"])
            lignes.append(f"{jour_iso(m, j)},{marchand},{montant(30, 15):.2f}")
        lignes.append(f"{jour_iso(m, random.randint(1, 27))},ESSO STATION SERVICE,{montant(58, 10):.2f}")
        lignes.append(f"{jour_iso(m, random.randint(1, 27))},ABONNEMENT SPOTIFY,10.99")
        if random.random() < 0.5:
            lignes.append(f"{jour_iso(m, random.randint(1, 27))},SAQ SUCCURSALE 1234,{montant(45, 15):.2f}")
        # Saisonnalité : achats des Fêtes en décembre.
        nb_achats = 4 if m == 12 else 1
        for _ in range(nb_achats):
            lignes.append(f"{jour_iso(m, random.randint(1, 27))},AMAZON.CA,{montant(90 if m == 12 else 60, 30):.2f}")
        if m == 12:
            lignes.append(f"{jour_iso(m, random.randint(1, 27))},LA BAIE,{montant(120, 40):.2f}")
        lignes.append(f"{jour_iso(m, random.randint(1, 27))},PAIEMENT RECU - MERCI,-{montant(220, 60):.2f}")

    # Défaut : doublon exact (même ligne répétée deux fois).
    ligne_dupliquee = f"{jour_iso(9, 12)},UBER EATS,27.85"
    lignes.append(ligne_dupliquee)
    lignes.append(ligne_dupliquee)

    return lignes


def main() -> None:
    fichiers = {
        "banque_boreale_compte_cheque.csv": generer_banque_boreale(),
        "caisse_aurore_epargne.csv": generer_caisse_aurore(),
        "carte_nordik_credit_2026_h1.csv": generer_carte_nordik_h1(),
        "carte_nordik_credit_2026_h2.csv": generer_carte_nordik_h2(),
    }
    ancien_fichier = RAW_DIR / "carte_nordik_credit.csv"
    if ancien_fichier.exists():
        ancien_fichier.unlink()

    for nom, lignes in fichiers.items():
        chemin = RAW_DIR / nom
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
        print(f"{nom} : {len(lignes) - 1} transactions")


if __name__ == "__main__":
    main()
