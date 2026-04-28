"""
Kamisado AI Client
Connects to the game server, registers, and plays using the Minimax strategy.

Usage:
    python client.py <server_url> <player_name>

Example:
    python client.py http://192.168.1.42:5000 MyAI
"""

import sys
import time
import requests
from strategy import choose_move

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

DEFAULT_SERVER = "http://localhost:5000"
DEFAULT_NAME   = "MinimaxAI"
POLL_INTERVAL  = 0.5   # seconds between state polls


# ─────────────────────────────────────────────
# Server communication helpers
# ─────────────────────────────────────────────

def register(server_url: str, player_name: str) -> dict:
    """
    Register this AI with the game server.
    Returns the registration info (game_id, player_index, …).
    """
    url = f"{server_url}/register"
    response = requests.post(url, json={"name": player_name})
    response.raise_for_status()
    data = response.json()
    print(f"[register] Registered as '{player_name}' → {data}")
    return data


def get_state(server_url: str, game_id: str) -> dict:
    """Fetch the current game state from the server."""
    url = f"{server_url}/state/{game_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def send_move(server_url: str, game_id: str, move: list) -> dict:
    """Send our chosen move to the server."""
    url = f"{server_url}/move/{game_id}"
    response = requests.post(url, json=move)
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────
# Main game loop
# ─────────────────────────────────────────────

def play(server_url: str, player_name: str) -> None:
    """
    Full game loop:
      1. Register with the server.
      2. Poll the state until it is our turn.
      3. Choose the best move with Minimax.
      4. Send the move and repeat.
    """
    # ── Register ──────────────────────────────
    info = register(server_url, player_name)

    game_id    = info.get("game_id") or info.get("id")
    my_index   = info.get("index")   or info.get("player_index", 0)

    print(f"[play] game_id={game_id}  my_index={my_index}")

    # ── Game loop ─────────────────────────────
    while True:
        state = get_state(server_url, game_id)

        # Check if the game is over
        winner = state.get("winner")
        if winner is not None:
            players = state.get("players", [])
            if winner == my_index:
                print(f"[play] 🏆  We WIN!  ({players[my_index] if players else my_index})")
            else:
                print(f"[play] ❌  We lose. ({players[winner] if players else winner} wins)")
            break

        current = state.get("current")
        if current != my_index:
            # Not our turn – wait and poll again
            time.sleep(POLL_INTERVAL)
            continue

        # ── Our turn ──────────────────────────
        print(f"[play] Our turn  color={state.get('color')}")
        move = choose_move(state, my_index)

        if move is None:
            print("[play] ⚠️  No move found – something went wrong.")
            break

        print(f"[play] Sending move: {move}")
        result = send_move(server_url, game_id, move)
        print(f"[play] Server response: {result}")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    server = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SERVER
    name   = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_NAME
    play(server, name)
