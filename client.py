"""
Client IA Kamisado
Se connecte au serveur de parties et joue en utilisant la stratégie Minimax.

Utilisation :
    python client.py <url_serveur> <nom_joueur>

Exemple :
    python client.py http://192.168.1.42:5000 MonIA
"""

import sys
import time
import requests
from strategy import choisir_coup

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

SERVEUR_DEFAUT     = "http://localhost:5000"
NOM_DEFAUT         = "MinimaxIA"
INTERVALLE_ATTENTE = 0.5  # secondes entre chaque vérification de l'état


# ─────────────────────────────────────────────
# Communication avec le serveur
# ─────────────────────────────────────────────

def s_inscrire(url_serveur: str, nom_joueur: str) -> dict:
    """
    Inscrit l'IA auprès du serveur de parties.
    Retourne les informations d'inscription (game_id, index du joueur, ...).
    """
    url = f"{url_serveur}/register"
    reponse = requests.post(url, json={"name": nom_joueur})
    reponse.raise_for_status()
    donnees = reponse.json()
    print(f"[inscription] Inscrit en tant que '{nom_joueur}' → {donnees}")
    return donnees


def obtenir_etat(url_serveur: str, game_id: str) -> dict:
    """Récupère l'état actuel de la partie depuis le serveur."""
    url = f"{url_serveur}/state/{game_id}"
    reponse = requests.get(url)
    reponse.raise_for_status()
    return reponse.json()


def envoyer_coup(url_serveur: str, game_id: str, coup: list) -> dict:
    """Envoie le coup choisi au serveur."""
    url = f"{url_serveur}/move/{game_id}"
    reponse = requests.post(url, json=coup)
    reponse.raise_for_status()
    return reponse.json()


# ─────────────────────────────────────────────
# Boucle de jeu principale
# ─────────────────────────────────────────────

def jouer(url_serveur: str, nom_joueur: str) -> None:
    """
    Boucle de jeu complète :
      1. S'inscrire auprès du serveur.
      2. Vérifier l'état jusqu'à ce que ce soit notre tour.
      3. Choisir le meilleur coup avec Minimax.
      4. Envoyer le coup et recommencer.
    """
    # ── Inscription ───────────────────────────
    info = s_inscrire(url_serveur, nom_joueur)

    game_id   = info.get("game_id") or info.get("id")
    mon_index = info.get("index")   or info.get("player_index", 0)

    print(f"[jeu] game_id={game_id}  mon_index={mon_index}")

    # ── Boucle de jeu ─────────────────────────
    while True:
        etat = obtenir_etat(url_serveur, game_id)

        # Vérifier si la partie est terminée
        gagnant = etat.get("winner")
        if gagnant is not None:
            joueurs = etat.get("players", [])
            if gagnant == mon_index:
                print(f"[jeu] 🏆  On GAGNE !  ({joueurs[mon_index] if joueurs else mon_index})")
            else:
                print(f"[jeu] ❌  On perd. ({joueurs[gagnant] if joueurs else gagnant} gagne)")
            break

        courant = etat.get("current")
        if courant != mon_index:
            # Ce n'est pas notre tour → on attend et on revérifie
            time.sleep(INTERVALLE_ATTENTE)
            continue

        # ── Notre tour ────────────────────────
        print(f"[jeu] Notre tour  couleur={etat.get('color')}")
        coup = choisir_coup(etat, mon_index)

        if coup is None:
            print("[jeu] ⚠️  Aucun coup trouvé – quelque chose s'est mal passé.")
            break

        print(f"[jeu] Envoi du coup : {coup}")
        resultat = envoyer_coup(url_serveur, game_id, coup)
        print(f"[jeu] Réponse du serveur : {resultat}")


# ─────────────────────────────────────────────
# Point d'entrée
# ─────────────────────────────────────────────

if __name__ == "__main__":
    serveur = sys.argv[1] if len(sys.argv) > 1 else SERVEUR_DEFAUT
    nom     = sys.argv[2] if len(sys.argv) > 2 else NOM_DEFAUT
    jouer(serveur, nom)

