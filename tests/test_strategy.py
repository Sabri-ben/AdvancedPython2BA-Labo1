"""
Tests pour la stratégie IA du jeu Kamisado.
Lancer avec : pytest tests/ --cov=strategy --cov-report=term-missing
"""

import copy
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strategy import (
    obtenir_jeton, obtenir_couleur_case, trouver_jeton, est_bloque,
    obtenir_coups_valides, appliquer_coup, evaluer, choisir_coup,
    COULEURS, DIRECTION, LIGNE_FIN,
)

# ─────────────────────────────────────────────
# Fonctions utilitaires pour les tests
# ─────────────────────────────────────────────

def creer_plateau_vide():
    """Plateau 8x8 avec les couleurs correctes mais sans aucun jeton."""
    COULEURS_PLATEAU = [
        ["orange", "blue",   "purple", "pink",   "yellow", "red",    "green",  "brown"],
        ["red",    "orange", "pink",   "green",  "blue",   "yellow", "brown",  "purple"],
        ["green",  "pink",   "orange", "red",    "purple", "brown",  "yellow", "blue"],
        ["pink",   "purple", "blue",   "orange", "brown",  "green",  "red",    "yellow"],
        ["yellow", "red",    "green",  "brown",  "orange", "blue",   "purple", "pink"],
        ["blue",   "yellow", "brown",  "purple", "red",    "orange", "pink",   "green"],
        ["purple", "brown",  "yellow", "blue",   "green",  "pink",   "orange", "red"],
        ["brown",  "green",  "red",    "yellow", "pink",   "purple", "blue",   "orange"],
    ]
    return [[[couleur, None] for couleur in ligne] for ligne in COULEURS_PLATEAU]


def creer_etat_initial():
    """État initial complet du jeu avec les jetons en place."""
    plateau = creer_plateau_vide()
    couleurs_light = ["pink", "orange", "green", "red", "purple", "blue", "brown", "yellow"]
    for c, couleur in enumerate(couleurs_light):
        plateau[0][c][1] = [couleur, "light"]
    couleurs_dark = ["yellow", "green", "orange", "purple", "red", "brown", "blue", "pink"]
    for c, couleur in enumerate(couleurs_dark):
        plateau[7][c][1] = [couleur, "dark"]
    return {
        "board": plateau,
        "color": None,
        "current": 0,
        "players": ["IA", "ADV"],
    }


# ─────────────────────────────────────────────
# Tests – obtenir_jeton
# ─────────────────────────────────────────────

class TestObtenirJeton:
    def test_retourne_none_si_case_vide(self):
        plateau = creer_plateau_vide()
        assert obtenir_jeton(plateau, 3, 3) is None

    def test_retourne_jeton_si_present(self):
        plateau = creer_plateau_vide()
        plateau[0][0][1] = ["orange", "light"]
        assert obtenir_jeton(plateau, 0, 0) == ["orange", "light"]


class TestObtenirCouleurCase:
    def test_coin_haut_gauche(self):
        plateau = creer_plateau_vide()
        assert obtenir_couleur_case(plateau, 0, 0) == "orange"

    def test_coin_bas_droite(self):
        plateau = creer_plateau_vide()
        assert obtenir_couleur_case(plateau, 7, 7) == "orange"


class TestTrouverJeton:
    def test_trouve_jeton_existant(self):
        plateau = creer_plateau_vide()
        plateau[3][5][1] = ["red", "dark"]
        assert trouver_jeton(plateau, "red", "dark") == (3, 5)

    def test_retourne_none_si_absent(self):
        plateau = creer_plateau_vide()
        assert trouver_jeton(plateau, "red", "dark") is None

    def test_trouve_jeton_light(self):
        plateau = creer_plateau_vide()
        plateau[0][2][1] = ["green", "light"]
        assert trouver_jeton(plateau, "green", "light") == (0, 2)


class TestEstBloque:
    def test_jeton_dark_bloque_par_ligne_pleine(self):
        plateau = creer_plateau_vide()
        plateau[7][3][1] = ["yellow", "dark"]
        for c in range(8):
            plateau[6][c][1] = ["orange", "light"]
        assert est_bloque(plateau, 7, 3) is True

    def test_jeton_dark_pas_bloque(self):
        plateau = creer_plateau_vide()
        plateau[7][3][1] = ["yellow", "dark"]
        assert est_bloque(plateau, 7, 3) is False

    def test_jeton_light_pas_bloque(self):
        plateau = creer_plateau_vide()
        plateau[0][4][1] = ["purple", "light"]
        assert est_bloque(plateau, 0, 4) is False

    def test_jeton_en_colonne_bord_pas_bloque(self):
        plateau = creer_plateau_vide()
        plateau[7][0][1] = ["brown", "dark"]
        assert est_bloque(plateau, 7, 0) is False


class TestObtenirCoupsValides:
    def test_jeton_dark_a_des_coups(self):
        plateau = creer_plateau_vide()
        plateau[7][4][1] = ["red", "dark"]
        coups = obtenir_coups_valides(plateau, "red", "dark")
        assert len(coups) > 0
        for coup in coups:
            assert coup[1][0] < 7

    def test_jeton_light_a_des_coups(self):
        plateau = creer_plateau_vide()
        plateau[0][2][1] = ["green", "light"]
        coups = obtenir_coups_valides(plateau, "green", "light")
        assert len(coups) > 0
        for coup in coups:
            assert coup[1][0] > 0

    def test_jeton_bloque_retourne_coup_passe(self):
        plateau = creer_plateau_vide()
        plateau[7][3][1] = ["yellow", "dark"]
        for c in range(8):
            plateau[6][c][1] = ["orange", "light"]
        coups = obtenir_coups_valides(plateau, "yellow", "dark")
        assert len(coups) == 1
        assert coups[0][0] == coups[0][1]

    def test_jeton_bloque_par_autre_jeton(self):
        plateau = creer_plateau_vide()
        plateau[7][4][1] = ["red", "dark"]
        plateau[6][4][1] = ["blue", "light"]
        coups = obtenir_coups_valides(plateau, "red", "dark")
        destinations = [c[1] for c in coups]
        assert [6, 4] not in destinations

    def test_retourne_vide_si_jeton_introuvable(self):
        plateau = creer_plateau_vide()
        coups = obtenir_coups_valides(plateau, "orange", "dark")
        assert coups == []

    def test_coups_diagonaux_inclus(self):
        plateau = creer_plateau_vide()
        plateau[5][4][1] = ["red", "dark"]
        coups = obtenir_coups_valides(plateau, "red", "dark")
        colonnes = [c[1][1] for c in coups]
        assert len(set(colonnes)) > 1


class TestAppliquerCoup:
    def test_jeton_se_deplace_vers_destination(self):
        plateau = creer_plateau_vide()
        plateau[7][4][1] = ["red", "dark"]
        nouveau_plateau, _, _ = appliquer_coup(plateau, [[7, 4], [5, 4]], "dark")
        assert obtenir_jeton(nouveau_plateau, 5, 4) == ["red", "dark"]
        assert obtenir_jeton(nouveau_plateau, 7, 4) is None

    def test_plateau_original_non_modifie(self):
        plateau = creer_plateau_vide()
        plateau[7][4][1] = ["red", "dark"]
        jeton_original = copy.deepcopy(obtenir_jeton(plateau, 7, 4))
        appliquer_coup(plateau, [[7, 4], [5, 4]], "dark")
        assert obtenir_jeton(plateau, 7, 4) == jeton_original

    def test_victoire_dark_atteint_ligne_0(self):
        plateau = creer_plateau_vide()
        plateau[1][3][1] = ["yellow", "dark"]
        _, _, victoire = appliquer_coup(plateau, [[1, 3], [0, 3]], "dark")
        assert victoire is True

    def test_victoire_light_atteint_ligne_7(self):
        plateau = creer_plateau_vide()
        plateau[6][2][1] = ["orange", "light"]
        _, _, victoire = appliquer_coup(plateau, [[6, 2], [7, 2]], "light")
        assert victoire is True

    def test_pas_de_victoire_coup_normal(self):
        plateau = creer_plateau_vide()
        plateau[7][4][1] = ["red", "dark"]
        _, _, victoire = appliquer_coup(plateau, [[7, 4], [5, 4]], "dark")
        assert victoire is False

    def test_couleur_suivante_correspond_a_case_arrivee(self):
        plateau = creer_plateau_vide()
        plateau[7][4][1] = ["red", "dark"]
        _, couleur_suivante, _ = appliquer_coup(plateau, [[7, 4], [5, 4]], "dark")
        assert couleur_suivante == obtenir_couleur_case(plateau, 5, 4)


class TestEvaluer:
    def test_jeton_avance_score_plus_eleve(self):
        plateau1 = creer_plateau_vide()
        plateau1[7][4][1] = ["red", "dark"]
        plateau2 = creer_plateau_vide()
        plateau2[3][4][1] = ["red", "dark"]
        assert evaluer(plateau2, "dark") > evaluer(plateau1, "dark")

    def test_avancement_adversaire_baisse_score(self):
        plateau1 = creer_plateau_vide()
        plateau1[0][4][1] = ["purple", "light"]
        plateau2 = creer_plateau_vide()
        plateau2[4][4][1] = ["purple", "light"]
        assert evaluer(plateau1, "dark") > evaluer(plateau2, "dark")

    def test_colonne_centrale_preferee(self):
        plateau1 = creer_plateau_vide()
        plateau1[5][0][1] = ["blue", "dark"]
        plateau2 = creer_plateau_vide()
        plateau2[5][3][1] = ["blue", "dark"]
        assert evaluer(plateau2, "dark") > evaluer(plateau1, "dark")

    def test_plateau_vide_score_zero(self):
        plateau = creer_plateau_vide()
        assert evaluer(plateau, "dark") == 0


class TestChoisirCoup:
    def test_retourne_un_coup(self):
        etat = creer_etat_initial()
        coup = choisir_coup(etat, mon_index=0)
        assert coup is not None
        assert len(coup) == 2
        assert len(coup[0]) == 2
        assert len(coup[1]) == 2

    def test_coordonnees_dans_les_limites(self):
        etat = creer_etat_initial()
        coup = choisir_coup(etat, mon_index=0)
        for pos in coup:
            assert 0 <= pos[0] <= 7
            assert 0 <= pos[1] <= 7

    def test_source_appartient_au_joueur_courant(self):
        etat = creer_etat_initial()
        coup = choisir_coup(etat, mon_index=0)
        plateau = etat["board"]
        sr, sc = coup[0]
        jeton = obtenir_jeton(plateau, sr, sc)
        assert jeton is not None
        assert jeton[1] == "dark"

    def test_choisir_coup_joueur_1(self):
        etat = creer_etat_initial()
        etat["current"] = 1
        etat["color"] = "orange"
        coup = choisir_coup(etat, mon_index=1)
        assert coup is not None

    def test_coup_gagnant_choisi(self):
        plateau = creer_plateau_vide()
        plateau[1][4][1] = ["yellow", "dark"]
        etat = {
            "board": plateau,
            "color": "yellow",
            "current": 0,
            "players": ["IA", "ADV"],
        }
        coup = choisir_coup(etat, mon_index=0)
        assert coup[1][0] == 0

    def test_pas_de_coup_illegal_etat_initial(self):
        etat = creer_etat_initial()
        coup = choisir_coup(etat, mon_index=0)
        sr, sc = coup[0]
        er, ec = coup[1]
        assert [sr, sc] != [er, ec]

