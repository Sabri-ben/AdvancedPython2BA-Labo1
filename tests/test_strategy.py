"""
Tests for the Kamisado AI strategy.
Run with:  pytest tests/ --cov=strategy --cov-report=term-missing
"""

import copy
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strategy import (
    get_tile, get_cell_color, find_tile, is_blocked,
    get_valid_moves, apply_move, evaluate, choose_move,
    COLORS, DIRECTION, END_ROW,
)

# ─────────────────────────────────────────────
# Fixtures – sample boards
# ─────────────────────────────────────────────

def make_empty_board():
    """8x8 board with correct square colors but no tiles."""
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
    return [[[color, None] for color in row] for row in BOARD_COLORS]


def make_initial_state():
    """Full initial game state (same token arrangement as game.py example)."""
    board = make_empty_board()
    # Place light tiles on row 0
    light_colors = ["pink", "orange", "green", "red", "purple", "blue", "brown", "yellow"]
    for c, color in enumerate(light_colors):
        board[0][c][1] = [color, "light"]
    # Place dark tiles on row 7
    dark_colors = ["yellow", "green", "orange", "purple", "red", "brown", "blue", "pink"]
    for c, color in enumerate(dark_colors):
        board[7][c][1] = [color, "dark"]
    return {
        "board": board,
        "color": None,
        "current": 0,
        "players": ["AI", "OPP"],
    }


# ─────────────────────────────────────────────
# Tests – board helpers
# ─────────────────────────────────────────────

class TestGetTile:
    def test_returns_none_on_empty_cell(self):
        board = make_empty_board()
        assert get_tile(board, 3, 3) is None

    def test_returns_tile_when_present(self):
        board = make_empty_board()
        board[0][0][1] = ["orange", "light"]
        assert get_tile(board, 0, 0) == ["orange", "light"]


class TestGetCellColor:
    def test_corner_top_left(self):
        board = make_empty_board()
        assert get_cell_color(board, 0, 0) == "orange"

    def test_corner_bottom_right(self):
        board = make_empty_board()
        assert get_cell_color(board, 7, 7) == "orange"


class TestFindTile:
    def test_finds_existing_tile(self):
        board = make_empty_board()
        board[3][5][1] = ["red", "dark"]
        assert find_tile(board, "red", "dark") == (3, 5)

    def test_returns_none_when_not_found(self):
        board = make_empty_board()
        assert find_tile(board, "red", "dark") is None

    def test_finds_light_tile(self):
        board = make_empty_board()
        board[0][2][1] = ["green", "light"]
        assert find_tile(board, "green", "light") == (0, 2)


# ─────────────────────────────────────────────
# Tests – is_blocked
# ─────────────────────────────────────────────

class TestIsBlocked:
    def test_dark_tile_blocked_by_full_row(self):
        """Dark tile at row 7 with row 6 fully occupied → blocked."""
        board = make_empty_board()
        board[7][3][1] = ["yellow", "dark"]
        for c in range(8):
            board[6][c][1] = ["orange", "light"]
        assert is_blocked(board, 7, 3) is True

    def test_dark_tile_not_blocked(self):
        """Dark tile at row 7 with empty row 6 → not blocked."""
        board = make_empty_board()
        board[7][3][1] = ["yellow", "dark"]
        assert is_blocked(board, 7, 3) is False

    def test_light_tile_not_blocked(self):
        board = make_empty_board()
        board[0][4][1] = ["purple", "light"]
        assert is_blocked(board, 0, 4) is False

    def test_tile_at_edge_column_not_blocked(self):
        """Tile in column 0 – only two directions to check."""
        board = make_empty_board()
        board[7][0][1] = ["brown", "dark"]
        assert is_blocked(board, 7, 0) is False


# ─────────────────────────────────────────────
# Tests – get_valid_moves
# ─────────────────────────────────────────────

class TestGetValidMoves:
    def test_dark_tile_has_moves_on_open_board(self):
        board = make_empty_board()
        board[7][4][1] = ["red", "dark"]
        moves = get_valid_moves(board, "red", "dark")
        assert len(moves) > 0
        # All destinations must have row < 7 (dark goes up)
        for move in moves:
            assert move[1][0] < 7

    def test_light_tile_has_moves_on_open_board(self):
        board = make_empty_board()
        board[0][2][1] = ["green", "light"]
        moves = get_valid_moves(board, "green", "light")
        assert len(moves) > 0
        for move in moves:
            assert move[1][0] > 0

    def test_blocked_tile_returns_pass_move(self):
        board = make_empty_board()
        board[7][3][1] = ["yellow", "dark"]
        for c in range(8):
            board[6][c][1] = ["orange", "light"]
        moves = get_valid_moves(board, "yellow", "dark")
        assert len(moves) == 1
        assert moves[0][0] == moves[0][1]   # pass move: src == dst

    def test_tile_blocked_by_other_tiles_in_path(self):
        board = make_empty_board()
        board[7][4][1] = ["red", "dark"]
        board[6][4][1] = ["blue", "light"]   # blocks straight ahead
        moves = get_valid_moves(board, "red", "dark")
        destinations = [m[1] for m in moves]
        assert [6, 4] not in destinations

    def test_returns_empty_when_tile_not_found(self):
        board = make_empty_board()
        moves = get_valid_moves(board, "orange", "dark")
        assert moves == []

    def test_diagonal_moves_included(self):
        board = make_empty_board()
        board[5][4][1] = ["red", "dark"]
        moves = get_valid_moves(board, "red", "dark")
        cols = [m[1][1] for m in moves]
        # Should include moves to the left and right diagonals
        assert len(set(cols)) > 1


# ─────────────────────────────────────────────
# Tests – apply_move
# ─────────────────────────────────────────────

class TestApplyMove:
    def test_tile_moves_to_destination(self):
        board = make_empty_board()
        board[7][4][1] = ["red", "dark"]
        new_board, next_color, won = apply_move(board, [[7, 4], [5, 4]], "dark")
        assert get_tile(new_board, 5, 4) == ["red", "dark"]
        assert get_tile(new_board, 7, 4) is None

    def test_original_board_not_mutated(self):
        board = make_empty_board()
        board[7][4][1] = ["red", "dark"]
        original_tile = copy.deepcopy(get_tile(board, 7, 4))
        apply_move(board, [[7, 4], [5, 4]], "dark")
        assert get_tile(board, 7, 4) == original_tile

    def test_won_when_dark_reaches_row_0(self):
        board = make_empty_board()
        board[1][3][1] = ["yellow", "dark"]
        _, _, won = apply_move(board, [[1, 3], [0, 3]], "dark")
        assert won is True

    def test_won_when_light_reaches_row_7(self):
        board = make_empty_board()
        board[6][2][1] = ["orange", "light"]
        _, _, won = apply_move(board, [[6, 2], [7, 2]], "light")
        assert won is True

    def test_not_won_on_normal_move(self):
        board = make_empty_board()
        board[7][4][1] = ["red", "dark"]
        _, _, won = apply_move(board, [[7, 4], [5, 4]], "dark")
        assert won is False

    def test_next_color_matches_destination_square(self):
        board = make_empty_board()
        board[7][4][1] = ["red", "dark"]
        _, next_color, _ = apply_move(board, [[7, 4], [5, 4]], "dark")
        assert next_color == get_cell_color(board, 5, 4)


# ─────────────────────────────────────────────
# Tests – evaluate
# ─────────────────────────────────────────────

class TestEvaluate:
    def test_advanced_dark_tile_scores_higher(self):
        board1 = make_empty_board()
        board1[7][4][1] = ["red", "dark"]   # start position
        board2 = make_empty_board()
        board2[3][4][1] = ["red", "dark"]   # advanced position
        assert evaluate(board2, "dark") > evaluate(board1, "dark")

    def test_opponent_advancement_lowers_score(self):
        board1 = make_empty_board()
        board1[0][4][1] = ["purple", "light"]   # opponent at start
        board2 = make_empty_board()
        board2[4][4][1] = ["purple", "light"]   # opponent advanced
        assert evaluate(board1, "dark") > evaluate(board2, "dark")

    def test_central_column_preferred(self):
        board1 = make_empty_board()
        board1[5][0][1] = ["blue", "dark"]   # edge column
        board2 = make_empty_board()
        board2[5][3][1] = ["blue", "dark"]   # central column
        assert evaluate(board2, "dark") > evaluate(board1, "dark")

    def test_symmetric_empty_board_scores_zero(self):
        board = make_empty_board()
        assert evaluate(board, "dark") == 0


# ─────────────────────────────────────────────
# Tests – choose_move (integration)
# ─────────────────────────────────────────────

class TestChooseMove:
    def test_returns_a_move(self):
        state = make_initial_state()
        move = choose_move(state, my_index=0)
        assert move is not None
        assert len(move) == 2
        assert len(move[0]) == 2
        assert len(move[1]) == 2

    def test_move_coordinates_in_range(self):
        state = make_initial_state()
        move = choose_move(state, my_index=0)
        for pos in move:
            assert 0 <= pos[0] <= 7
            assert 0 <= pos[1] <= 7

    def test_move_source_has_correct_kind(self):
        """The source tile must belong to the current player."""
        state = make_initial_state()
        move = choose_move(state, my_index=0)
        board = state["board"]
        sr, sc = move[0]
        tile = get_tile(board, sr, sc)
        assert tile is not None
        assert tile[1] == "dark"   # player 0 is dark

    def test_choose_move_player_1(self):
        """Player 1 (light) should also return a valid move."""
        state = make_initial_state()
        state["current"] = 1
        state["color"] = "orange"   # simulate a color constraint
        move = choose_move(state, my_index=1)
        assert move is not None

    def test_winning_move_chosen(self):
        """AI should pick the winning move when available."""
        board = make_empty_board()
        # Dark tile one step from winning
        board[1][4][1] = ["yellow", "dark"]
        state = {
            "board": board,
            "color": "yellow",
            "current": 0,
            "players": ["AI", "OPP"],
        }
        move = choose_move(state, my_index=0)
        assert move[1][0] == 0   # should move to row 0 (win)

    def test_no_bad_move_on_initial_state(self):
        """Source and destination must differ (no illegal same-square move unless blocked)."""
        state = make_initial_state()
        move = choose_move(state, my_index=0)
        board = state["board"]
        sr, sc = move[0]
        er, ec = move[1]
        # On initial state nothing is blocked so source != destination
        assert [sr, sc] != [er, ec]
