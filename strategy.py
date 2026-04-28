"""
Kamisado AI Strategy - Minimax with Alpha-Beta Pruning
"""

import copy

# ─────────────────────────────────────────────
# Constants (mirror game.py so we stay independent)
# ─────────────────────────────────────────────

COLORS = ["orange", "blue", "purple", "pink", "yellow", "red", "green", "brown"]

BOARD_COLORS = [
    ["orange", "blue",   "purple", "pink",   "yellow", "red",    "green",  "brown"],
    ["red",    "orange", "pink",   "green",  "blue",   "yellow", "brown",  "purple"],
    ["green",  "pink",   "orange", "red",    "purple", "brown",  "yellow", "blue"],
    ["pink",   "purple", "blue",   "orange", "brown",  "green",  "red",    "yellow"],
    ["yellow", "red",    "green",  "brown",  "orange", "blue",   "purple", "pink"],
    ["blue",   "yellow", "brown",  "purple", "red",    "orange", "pink",   "green"],
    ["purple", "brown",  "yellow", "blue",   "green",  "pink",   "orange", "red"],
    ["brown",  "green",  "red",    "yellow", "pink",   "purple", "blue",   "orange"],
]

# dark moves toward row 0, light moves toward row 7
DIRECTION = {"dark": -1, "light": 1}
END_ROW   = {"dark": 0,  "light": 7}
START_ROW = {"dark": 7,  "light": 0}

TILE_IDX  = 1
COLOR_IDX = 0
KIND_IDX  = 1

MINIMAX_DEPTH = 3   # increase for stronger play (slower)


# ─────────────────────────────────────────────
# Board helpers
# ─────────────────────────────────────────────

def get_tile(board, r, c):
    """Return the tile at (r, c) or None."""
    return board[r][c][TILE_IDX]


def get_cell_color(board, r, c):
    """Return the board-square color at (r, c)."""
    return board[r][c][COLOR_IDX]


def find_tile(board, color, kind):
    """Find the position (r, c) of a tile by color and kind."""
    for r in range(8):
        for c in range(8):
            tile = get_tile(board, r, c)
            if tile is not None and tile[COLOR_IDX] == color and tile[KIND_IDX] == kind:
                return r, c
    return None


def is_blocked(board, r, c):
    """
    Return True if the tile at (r, c) cannot move anywhere.
    A tile is blocked when every cell in the row ahead (and diagonals) is occupied.
    """
    kind = get_tile(board, r, c)[KIND_IDX]
    dr = DIRECTION[kind]
    next_row = r + dr
    if next_row < 0 or next_row > 7:
        return True   # already on winning row – handled elsewhere
    for dc in (-1, 0, 1):
        nc = c + dc
        if 0 <= nc <= 7 and get_tile(board, next_row, nc) is None:
            return False
    return True


def get_valid_moves(board, color, kind):
    """
    Return all legal moves for the tile of the given (color, kind).
    Each move is [[src_r, src_c], [dst_r, dst_c]].
    Returns [[[r,c],[r,c]]] with src==dst if the tile is blocked.
    """
    pos = find_tile(board, color, kind)
    if pos is None:
        return []

    r, c = pos
    dr = DIRECTION[kind]
    moves = []

    # three possible directions: straight ahead, diagonal-left, diagonal-right
    for dc in (0, -1, 1):
        nr, nc = r + dr, c + dc
        while 0 <= nr <= 7 and 0 <= nc <= 7:
            if get_tile(board, nr, nc) is not None:
                break   # path blocked
            moves.append([[r, c], [nr, nc]])
            nr += dr
            nc += dc

    if not moves:
        # tile is blocked: pass move
        moves.append([[r, c], [r, c]])

    return moves


def apply_move(board, move, kind):
    """
    Apply a move on a deep copy of the board and return
    (new_board, next_color, won).
    next_color is the board-square color of the destination cell.
    won is True if the moving tile has reached the end row.
    """
    new_board = copy.deepcopy(board)
    (sr, sc), (er, ec) = move

    tile = new_board[sr][sc][TILE_IDX]
    new_board[er][ec][TILE_IDX] = tile
    new_board[sr][sc][TILE_IDX] = None

    next_color = get_cell_color(new_board, er, ec)
    won = (er == END_ROW[kind])
    return new_board, next_color, won


# ─────────────────────────────────────────────
# Evaluation heuristic
# ─────────────────────────────────────────────

def evaluate(board, my_kind):
    """
    Static evaluation of the board from the perspective of my_kind.
    Higher is better for my_kind.

    Heuristic components:
      1. Row advancement  – reward being closer to the opponent's end row.
      2. Centrality       – central columns are more flexible.
      3. Opponent penalty – penalise the opponent's advancement.
    """
    opp_kind = "light" if my_kind == "dark" else "dark"
    score = 0

    for r in range(8):
        for c in range(8):
            tile = get_tile(board, r, c)
            if tile is None:
                continue
            t_color, t_kind = tile

            # advancement: dark goes toward row 0, light toward row 7
            if t_kind == "dark":
                advancement = 7 - r   # 0 (start) → 7 (end)
            else:
                advancement = r       # 0 (start) → 7 (end)

            centrality = 3.5 - abs(c - 3.5)   # 0..3.5

            tile_score = advancement * 10 + centrality * 2

            if t_kind == my_kind:
                score += tile_score
            else:
                score -= tile_score

    return score


# ─────────────────────────────────────────────
# Minimax with Alpha-Beta pruning
# ─────────────────────────────────────────────

def minimax(board, depth, alpha, beta, is_maximising, my_kind, current_color, current_kind):
    """
    Minimax with alpha-beta pruning.

    Parameters
    ----------
    board            : current board state
    depth            : remaining search depth
    alpha, beta      : pruning bounds
    is_maximising    : True when it is our turn
    my_kind          : the kind ("dark"/"light") of our AI
    current_color    : color of the tile that must be played (None = any)
    current_kind     : kind of the player whose turn it is

    Returns
    -------
    (score, best_move)
    """
    opp_kind = "light" if current_kind == "dark" else "dark"

    # Determine which tile must be moved
    if current_color is None:
        # First move: any tile of current_kind can be chosen
        # We try all tiles of current_kind
        all_moves = []
        for color in COLORS:
            pos = find_tile(board, color, current_kind)
            if pos is not None:
                all_moves.extend(get_valid_moves(board, color, current_kind))
    else:
        all_moves = get_valid_moves(board, current_color, current_kind)

    # Terminal: no moves available
    if not all_moves or depth == 0:
        return evaluate(board, my_kind), None

    best_move = None

    if is_maximising:
        best_score = float("-inf")
        for move in all_moves:
            new_board, next_color, won = apply_move(board, move, current_kind)
            if won:
                return 10000 + depth * 100, move   # winning move
            score, _ = minimax(
                new_board, depth - 1, alpha, beta,
                False, my_kind, next_color, opp_kind
            )
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break   # β-cutoff
        return best_score, best_move

    else:
        best_score = float("inf")
        for move in all_moves:
            new_board, next_color, won = apply_move(board, move, current_kind)
            if won:
                return -10000 - depth * 100, move   # opponent wins
            score, _ = minimax(
                new_board, depth - 1, alpha, beta,
                True, my_kind, next_color, opp_kind
            )
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break   # α-cutoff
        return best_score, best_move


# ─────────────────────────────────────────────
# Public API – called by client.py
# ─────────────────────────────────────────────

def choose_move(state, my_index):
    """
    Choose the best move given the current game state.

    Parameters
    ----------
    state    : dict – the game state received from the server
    my_index : int  – our player index (0 or 1)

    Returns
    -------
    move : [[src_r, src_c], [dst_r, dst_c]]
    """
    board         = state["board"]
    current_color = state["color"]       # None on first move
    current       = state["current"]     # index of player to move

    # Determine kinds: player 0 is always "dark", player 1 is "light"
    # (first player uses dark tiles as per game rules)
    my_kind      = "dark"  if my_index == 0 else "light"
    current_kind = "dark"  if current  == 0 else "light"

    is_my_turn = (current == my_index)

    _, move = minimax(
        board,
        depth        = MINIMAX_DEPTH,
        alpha        = float("-inf"),
        beta         = float("inf"),
        is_maximising= is_my_turn,
        my_kind      = my_kind,
        current_color= current_color,
        current_kind = current_kind,
    )

    # Fallback safety: if minimax returns None, play first valid move
    if move is None:
        if current_color is None:
            for color in COLORS:
                moves = get_valid_moves(board, color, current_kind)
                if moves:
                    move = moves[0]
                    break
        else:
            moves = get_valid_moves(board, current_color, current_kind)
            move = moves[0] if moves else None

    return move
