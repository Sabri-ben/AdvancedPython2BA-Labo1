import copy

# Les 8 couleurs possibles des jetons et des cases
COULEURS = ["orange", "blue", "purple", "pink", "yellow", "red", "green", "brown"]

# Couleurs fixes de chaque case du plateau (ne changent jamais)
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

# Direction de déplacement : "dark" va vers la ligne 0, "light" vers la ligne 7
DIRECTION = {"dark": -1, "light": 1}

# Ligne de victoire pour chaque type de jeton
LIGNE_FIN = {"dark": 0, "light": 7}

# Ligne de départ pour chaque type de jeton
LIGNE_DEPART = {"dark": 7, "light": 0}

# Index dans une cellule : board[r][c] = [couleur_case, jeton]
# Index dans un jeton    : jeton = [couleur_jeton, type_jeton]
IDX_JETON   = 1
IDX_COULEUR = 0
IDX_TYPE    = 1

# Profondeur de recherche Minimax (nombre de coups regardés à l'avance)
PROFONDEUR_MINIMAX = 3


def obtenir_jeton(plateau, r, c):
    """Retourne le jeton sur la case (r, c), ou None si vide."""
    return plateau[r][c][IDX_JETON]


def obtenir_couleur_case(plateau, r, c):
    """Retourne la couleur fixe de la case (r, c)."""
    return plateau[r][c][IDX_COULEUR]


def trouver_jeton(plateau, couleur, type_jeton):
    """
    Cherche le jeton de couleur et type donnés sur tout le plateau.
    Retourne (r, c) si trouvé, None sinon.
    """
    for r in range(8):
        for c in range(8):
            jeton = obtenir_jeton(plateau, r, c)
            if jeton is not None and jeton[IDX_COULEUR] == couleur and jeton[IDX_TYPE] == type_jeton:
                return r, c
    return None


def est_bloque(plateau, r, c):
    """
    Vérifie si le jeton sur la case (r, c) est complètement bloqué.
    Un jeton est bloqué quand toutes les cases devant lui sont occupées.
    Si bloqué → le joueur doit jouer un coup passe (rester sur place).
    """
    type_jeton = obtenir_jeton(plateau, r, c)[IDX_TYPE]
    dr = DIRECTION[type_jeton]
    ligne_suivante = r + dr

    if ligne_suivante < 0 or ligne_suivante > 7:
        return True

    for dc in (-1, 0, 1):
        nc = c + dc
        if 0 <= nc <= 7 and obtenir_jeton(plateau, ligne_suivante, nc) is None:
            return False

    return True


def obtenir_coups_valides(plateau, couleur, type_jeton):
    """
    Calcule tous les coups valides pour le jeton (couleur, type_jeton).

    Règles de déplacement :
      - Avance tout droit ou en diagonale (jamais en arrière)
      - Peut avancer de plusieurs cases à la fois
      - Ne peut pas passer par-dessus un autre jeton
      - Si bloqué → coup passe (source == destination)

    Retourne une liste de coups [[ligne_src, col_src], [ligne_dst, col_dst]]
    """
    pos = trouver_jeton(plateau, couleur, type_jeton)
    if pos is None:
        return []

    r, c = pos
    dr = DIRECTION[type_jeton]
    coups = []

    for dc in (0, -1, 1):  # tout droit, diagonale gauche, diagonale droite
        nr, nc = r + dr, c + dc

        while 0 <= nr <= 7 and 0 <= nc <= 7:
            if obtenir_jeton(plateau, nr, nc) is not None:
                break  # chemin bloqué

            coups.append([[r, c], [nr, nc]])
            nr += dr
            nc += dc

    if not coups:
        coups.append([[r, c], [r, c]])  # coup passe

    return coups


def appliquer_coup(plateau, coup, type_jeton):
    """
    Applique un coup sur une copie du plateau (l'original n'est pas modifié).
    Essentiel pour Minimax : on simule sans changer le vrai état.

    Retourne :
        nouveau_plateau  : plateau après le coup
        couleur_suivante : couleur de la case d'arrivée (impose le prochain jeton)
        victoire         : True si le jeton atteint la ligne de victoire
    """
    nouveau_plateau = copy.deepcopy(plateau)
    (sr, sc), (er, ec) = coup

    jeton = nouveau_plateau[sr][sc][IDX_JETON]
    nouveau_plateau[er][ec][IDX_JETON] = jeton
    nouveau_plateau[sr][sc][IDX_JETON] = None

    couleur_suivante = obtenir_couleur_case(nouveau_plateau, er, ec)
    victoire = (er == LIGNE_FIN[type_jeton])

    return nouveau_plateau, couleur_suivante, victoire


def evaluer(plateau, mon_type):
    """
    Donne un score numérique à une position du plateau.
    Score positif = bonne position pour nous.
    Score négatif = mauvaise position pour nous.

    Critères :
      1. Avancement (x10) : plus le jeton est proche de la ligne adverse, mieux c'est
      2. Centralité (x2)  : les colonnes centrales offrent plus de liberté
      3. Adversaire       : le score adverse est soustrait du nôtre
    """
    score = 0

    for r in range(8):
        for c in range(8):
            jeton = obtenir_jeton(plateau, r, c)
            if jeton is None:
                continue

            couleur_jeton, type_jeton = jeton

            if type_jeton == "dark":
                avancement = 7 - r  # dark part de 7, va vers 0
            else:
                avancement = r      # light part de 0, va vers 7

            centralite = 3.5 - abs(c - 3.5)  # 0 en bord, 3.5 au centre

            score_jeton = avancement * 10 + centralite * 2

            if type_jeton == mon_type:
                score += score_jeton
            else:
                score -= score_jeton

    return score


def minimax(plateau, profondeur, alpha, beta, maximisant, mon_type, couleur_courante, type_courant):
    """
    Algorithme Minimax avec élagage Alpha-Beta.

    Notre tour (maximisant)   → on cherche le coup qui MAXIMISE notre score.
    Tour adverse (minimisant) → l'adversaire cherche à MINIMISER notre score.

    Alpha-Beta : évite d'explorer des branches inutiles.
      - alpha : meilleur score garanti pour nous
      - beta  : meilleur score garanti pour l'adversaire
      - Si beta <= alpha → on arrête d'explorer cette branche

    Retourne : (score, meilleur_coup)
    """
    type_adverse = "light" if type_courant == "dark" else "dark"

    if couleur_courante is None:
        # Premier coup : on peut jouer n'importe quel jeton
        tous_les_coups = []
        for couleur in COULEURS:
            pos = trouver_jeton(plateau, couleur, type_courant)
            if pos is not None:
                tous_les_coups.extend(obtenir_coups_valides(plateau, couleur, type_courant))
    else:
        # Coup normal : on joue le jeton de la couleur imposée
        tous_les_coups = obtenir_coups_valides(plateau, couleur_courante, type_courant)

    # Cas de base : profondeur 0 ou aucun coup → on évalue la position
    if not tous_les_coups or profondeur == 0:
        return evaluer(plateau, mon_type), None

    meilleur_coup = None

    if maximisant:
        meilleur_score = float("-inf")

        for coup in tous_les_coups:
            nouveau_plateau, couleur_suivante, victoire = appliquer_coup(plateau, coup, type_courant)

            if victoire:
                return 10000 + profondeur * 100, coup  # coup gagnant

            score, _ = minimax(
                nouveau_plateau, profondeur - 1, alpha, beta,
                False, mon_type, couleur_suivante, type_adverse
            )

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup

            alpha = max(alpha, meilleur_score)
            if beta <= alpha:
                break  # élagage Beta

        return meilleur_score, meilleur_coup

    else:
        meilleur_score = float("inf")

        for coup in tous_les_coups:
            nouveau_plateau, couleur_suivante, victoire = appliquer_coup(plateau, coup, type_courant)

            if victoire:
                return -10000 - profondeur * 100, coup  # l'adversaire gagne

            score, _ = minimax(
                nouveau_plateau, profondeur - 1, alpha, beta,
                True, mon_type, couleur_suivante, type_adverse
            )

            if score < meilleur_score:
                meilleur_score = score
                meilleur_coup = coup

            beta = min(beta, meilleur_score)
            if beta <= alpha:
                break  # élagage Alpha

        return meilleur_score, meilleur_coup


def choisir_coup(etat, mon_index):
    """
    Fonction principale appelée par le client à chaque tour.
    Reçoit l'état du jeu et retourne le meilleur coup à jouer.

    Paramètres :
        etat      : dictionnaire reçu du serveur avec :
                    - "board"   : le plateau actuel
                    - "color"   : couleur du jeton à jouer (None = premier coup)
                    - "current" : index du joueur dont c'est le tour
                    - "players" : liste des noms des joueurs
        mon_index : notre index dans la liste des joueurs (0 ou 1)

    Retourne :
        coup : [[ligne_source, col_source], [ligne_dest, col_dest]]
    """
    plateau          = etat["board"]
    couleur_courante = etat["color"]
    courant          = etat["current"]

    mon_type     = "dark" if mon_index == 0 else "light"
    type_courant = "dark" if courant   == 0 else "light"

    c_est_mon_tour = (courant == mon_index)

    _, coup = minimax(
        plateau,
        profondeur       = PROFONDEUR_MINIMAX,
        alpha            = float("-inf"),
        beta             = float("inf"),
        maximisant       = c_est_mon_tour,
        mon_type         = mon_type,
        couleur_courante = couleur_courante,
        type_courant     = type_courant,
    )

    # Sécurité : si Minimax ne trouve rien, on joue le premier coup valide
    if coup is None:
        if couleur_courante is None:
            for couleur in COULEURS:
                coups = obtenir_coups_valides(plateau, couleur, type_courant)
                if coups:
                    coup = coups[0]
                    break
        else:
            coups = obtenir_coups_valides(plateau, couleur_courante, type_courant)
            coup = coups[0] if coups else None

    return coup
