# server/ai/minimax.py
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

Board = Sequence[Optional[str]]
Triplet = Tuple[int, int, int]


_WIN_LINES: Tuple[Triplet, ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def check_winner(board: Board) -> Optional[str]:
    """Return 'X', 'O', 'DRAW', or None for an unfinished game."""
    normalized = [cell if cell not in ("", None) else None for cell in board]

    for a, b, c in _WIN_LINES:
        line = (normalized[a], normalized[b], normalized[c])
        if line[0] is not None and line[0] == line[1] == line[2]:
            return line[0]

    if all(cell is not None for cell in normalized):
        return "DRAW"

    return None


def _minimax(
    board: List[Optional[str]],
    depth: int,
    maximizing: bool,
    ai_player: str,
    human_player: str,
) -> int:
    result = check_winner(board)

    if result == ai_player:
        return 10 - depth
    if result == human_player:
        return depth - 10
    if result == "DRAW":
        return 0

    if maximizing:
        best_score = -float("inf")
        for idx, cell in enumerate(board):
            if cell is None:
                board[idx] = ai_player
                score = _minimax(board, depth + 1, False, ai_player, human_player)
                board[idx] = None
                best_score = max(best_score, score)
        return best_score

    best_score = float("inf")
    for idx, cell in enumerate(board):
        if cell is None:
            board[idx] = human_player
            score = _minimax(board, depth + 1, True, ai_player, human_player)
            board[idx] = None
            best_score = min(best_score, score)
    return best_score


def find_best_move(board: Board, player: str) -> Optional[int]:
    """Return the strongest move index for `player` given the current board."""
    ai_player = player
    human_player = "O" if player == "X" else "X"

    normalized = [cell if cell not in ("", None) else None for cell in board]
    best_score = -float("inf")
    best_move: Optional[int] = None

    for idx, cell in enumerate(normalized):
        if cell is None:
            normalized[idx] = ai_player
            score = _minimax(normalized, depth=0, maximizing=False,
                             ai_player=ai_player, human_player=human_player)
            normalized[idx] = None
            if score > best_score:
                best_score = score
                best_move = idx

    return best_move