# server/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, db
import uuid, os
from typing import Any, Dict, List, Optional
from datetime import datetime

# AI utilities (kept for AI endpoint)
try:
    from ai.minimax import find_best_move, check_winner
except Exception:
    # fallback functions
    def check_winner(board):
        combos = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        for a,b,c in combos:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        if all(cell is not None and cell != "" for cell in board):
            return "DRAW"
        return None

    def find_best_move(board, player):
        for i, v in enumerate(board):
            if v is None or v == "":
                return i
        return None

# -------------------------------
# Firebase init
# -------------------------------
SERVICE_KEY = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
if not os.path.exists(SERVICE_KEY):
    raise RuntimeError(f"Missing Firebase service account key at: {SERVICE_KEY}")

cred = credentials.Certificate(SERVICE_KEY)
initialize_app(cred, {
    "databaseURL": "https://tictactoe-multiplayer-581b6-default-rtdb.asia-southeast1.firebasedatabase.app"
})

# -------------------------------
# FastAPI
# -------------------------------
app = FastAPI(title="TicTacToe Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Helpers: normalize board representations
# -------------------------------
def firebase_board_to_internal(raw) -> List[Optional[str]]:
    """
    Accept firebase representation (list with "" or dict with numeric keys)
    Return Python list of length 9 with values: "X", "O" or None
    """
    internal = [None] * 9
    if raw is None:
        return internal
    # If Firebase stored as dict { "0":"X", "1":"" ... }
    if isinstance(raw, dict):
        for k, v in raw.items():
            try:
                idx = int(k)
            except Exception:
                continue
            val = v if v not in (None, "") else None
            if 0 <= idx < 9:
                internal[idx] = val
        return internal
    # If list-like
    if isinstance(raw, list):
        for i in range(min(9, len(raw))):
            v = raw[i]
            internal[i] = v if v not in (None, "") else None
        return internal
    # fallback
    return internal

def internal_board_to_firebase(board: List[Optional[str]]):
    """
    Convert internal board (list with None/"X"/"O") to firebase-friendly list
    using empty string "" for empty spots (keeps Firebase array indices intact).
    """
    out = []
    for i in range(9):
        v = board[i] if i < len(board) else None
        out.append(v if v is not None else "")
    return out

def make_default_room_dict() -> Dict[str, Any]:
    return {
        "board": internal_board_to_firebase([None]*9),
        "players": {},
        "turn": "X",
        "winner": ""
    }

def ensure_room_structure(room: Dict[str, Any]) -> Dict[str, Any]:
    # normalize board into internal form and then place firebase form back
    board_raw = room.get("board", None)
    internal = firebase_board_to_internal(board_raw)
    room["board"] = internal_board_to_firebase(internal)
    if "players" not in room or not isinstance(room["players"], dict):
        room["players"] = {}
    if "turn" not in room:
        room["turn"] = "X"
    if "winner" not in room:
        room["winner"] = ""
    return room

# -------------------------------
# Routes
# -------------------------------
@app.get("/")
def root():
    return {"message": "Tic Tac Toe Backend Active!"}

@app.post("/create")
def create_room():
    room_id = str(uuid.uuid4())[:8]
    ref = db.reference(f"rooms/{room_id}")
    ref.set(make_default_room_dict())
    print(f"[CREATE] Room {room_id} created.")
    return {"room_id": room_id}

@app.post("/join/{room_id}")
def join_room(room_id: str, payload: Optional[Dict] = None):
    """
    Join room. Optionally pass {"username": "Alice"} in POST body.
    Server returns assigned role and stores username under players role.
    """
    ref = db.reference(f"rooms/{room_id}")
    room = ref.get()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room = ensure_room_structure(room)
    players = room.get("players", {}) or {}

    username = None
    if payload and isinstance(payload, dict):
        username = payload.get("username")

    # choose empty slot
    if not players.get("X"):
        players["X"] = username if username else f"player-{str(uuid.uuid4())[:6]}"
        assigned = "X"
    elif not players.get("O"):
        players["O"] = username if username else f"player-{str(uuid.uuid4())[:6]}"
        assigned = "O"
    else:
        raise HTTPException(status_code=400, detail="Room is full")

    # persist players map (keep other fields unchanged)
    ref.child("players").set(players)
    print(f"[JOIN] Room {room_id}: {assigned} joined -> {players.get(assigned)}")
    return {"player": assigned, "room_id": room_id, "username": players.get(assigned)}

@app.get("/room/{room_id}")
def get_room(room_id: str):
    ref = db.reference(f"rooms/{room_id}")
    room = ref.get()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    # normalize and return fully normalized structure (board as internal list for frontend)
    room = ensure_room_structure(room)
    # convert board to internal representation for API consumers (optional)
    internal_board = firebase_board_to_internal(room.get("board"))
    return {
        "board": internal_board,        # list of None/"X"/"O"
        "players": room.get("players", {}),
        "turn": room.get("turn", "X"),
        "winner": room.get("winner", "")
    }

# -------------------------------
# Make Move (fixed: normalization + write)
# -------------------------------
@app.post("/move/{room_id}")
def make_move(room_id: str, move: Dict):
    """
    Expected JSON body: { "player": "X" | "O", "index": 0..8 }
    """
    if not isinstance(move, dict):
        raise HTTPException(status_code=400, detail="Invalid payload format (expected JSON object)")

    player = move.get("player")
    index = move.get("index")

    if player not in ("X", "O"):
        raise HTTPException(status_code=400, detail="Invalid or missing 'player' (must be 'X' or 'O')")

    if index is None:
        raise HTTPException(status_code=400, detail="Missing 'index' for move")
    try:
        index = int(index)
    except Exception:
        raise HTTPException(status_code=400, detail="'index' must be an integer between 0 and 8")

    if index < 0 or index > 8:
        raise HTTPException(status_code=400, detail="'index' out of range (0..8)")

    ref = db.reference(f"rooms/{room_id}")
    room_raw = ref.get()
    if not room_raw:
        raise HTTPException(status_code=404, detail="Room not found")

    # Convert DB board into internal list
    board_internal = firebase_board_to_internal(room_raw.get("board"))
    turn = room_raw.get("turn", "X")
    winner = room_raw.get("winner", "")

    # If game already has a winner, reject moves
    if winner and winner != "":
        raise HTTPException(status_code=400, detail=f"Game already finished with winner: {winner}")

    # Validate that index cell is empty
    if board_internal[index] is not None and board_internal[index] != "":
        raise HTTPException(status_code=400, detail="Invalid move: position filled")

    # Validate player's turn
    if player != turn:
        raise HTTPException(status_code=400, detail=f"Not your turn. Current turn: {turn}")

    # Apply move
    board_internal[index] = player

    # Check winner after move
    new_winner = check_winner(board_internal)

    # Calculate next turn
    next_turn = turn if new_winner else ("O" if turn == "X" else "X")

    # Persist: convert internal board -> firebase form ("" for empties)
    try:
        ref.update({
            "board": internal_board_to_firebase(board_internal),
            "turn": next_turn,
            "winner": new_winner if new_winner else ""
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to persist move: {e}")

    # Update leaderboard/history if game ended
    if new_winner in ("X", "O"):
        players = room_raw.get("players", {})
        winner_name = players.get(new_winner)
        loser_name = players.get("O" if new_winner == "X" else "X")
        if winner_name:
            update_leaderboard_and_history(room_id, winner_name, loser_name, players)

    print(f"[MOVE] Room {room_id} | Player {player} -> {index} | Winner: {new_winner} | Next: {next_turn}")
    return {"board": board_internal, "turn": next_turn, "winner": new_winner}

# -------------------------------
# Leaderboard & History Helper
# -------------------------------
def update_leaderboard_and_history(room_id: str, winner_name: str, loser_name: Optional[str], players: Dict):
    leaderboard_ref = db.reference("leaderboard")
    history_ref = db.reference("history")

    # Winner
    if winner_name:
        wref = leaderboard_ref.child(winner_name)
        wdata = wref.get() or {"wins": 0, "losses": 0}
        wdata["wins"] = int(wdata.get("wins", 0)) + 1
        wref.set(wdata)
    # Loser
    if loser_name:
        lref = leaderboard_ref.child(loser_name)
        ldata = lref.get() or {"wins": 0, "losses": 0}
        ldata["losses"] = int(ldata.get("losses", 0)) + 1
        lref.set(ldata)

    # push history
    history_ref.child(room_id).set({
        "room_id": room_id,
        "winner": winner_name,
        "players": players,
        "finished_at": datetime.utcnow().isoformat()
    })
    print(f"[LEADERBOARD] {winner_name} +1 win; {loser_name} +1 loss")

# -------------------------------
# Reset
# -------------------------------
@app.post("/reset/{room_id}")
def reset_game(room_id: str):
    ref = db.reference(f"rooms/{room_id}")
    if not ref.get():
        raise HTTPException(status_code=404, detail="Room not found")
    ref.update({
        "board": internal_board_to_firebase([None]*9),
        "turn": "X",
        "winner": ""
    })
    print(f"[RESET] Room {room_id} reset.")
    return {"status":"reset","room_id":room_id}

# -------------------------------
# AI Move
# -------------------------------
@app.post("/ai-move")
def ai_move(data: Dict):
    board = data.get("board")
    player = data.get("player")
    if not isinstance(board, list) or player not in ("X","O"):
        raise HTTPException(status_code=400, detail="Invalid data")
    best = find_best_move(board, player)
    return {"best_move": best}
