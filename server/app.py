from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, db
import uuid, os, json
from typing import Any, Dict, List, Optional
from datetime import datetime

# -------------------------------
# AI Utilities (Fallback Safe)
# -------------------------------
try:
    from ai.minimax import find_best_move, check_winner
except Exception:
    def check_winner(board):
        combos = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in combos:
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
# Firebase Initialization
# -------------------------------
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")
FIREBASE_DB_URL = os.getenv(
    "FIREBASE_DB_URL",
    "https://tictactoe-multiplayer-581b6-default-rtdb.asia-southeast1.firebasedatabase.app"
)

if FIREBASE_CREDENTIALS_JSON:
    cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
    cred = credentials.Certificate(cred_dict)
else:
    service_key = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
    if not os.path.exists(service_key):
        raise RuntimeError("Missing Firebase service account key")
    cred = credentials.Certificate(service_key)

initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})

# -------------------------------
# FastAPI Setup
# -------------------------------
app = FastAPI(title="Tic Tac Toe Backend")

# ✅ Allow both local dev and deployed frontend origins
origins = [
    "http://localhost:3000",
    "https://tic-tac-toe-ten-topaz.vercel.app",
    "https://tic-tac-toe-ten-topaz.vercel.app/",  # optional trailing slash version
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Preflight handler (fixes browser CORS pre-check)
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str = None):
    return {"message": "CORS preflight OK"}


# -------------------------------
# Helper Functions
# -------------------------------
def firebase_board_to_internal(raw) -> List[Optional[str]]:
    internal = [None] * 9
    if raw is None:
        return internal
    if isinstance(raw, dict):
        for k, v in raw.items():
            try:
                idx = int(k)
                if 0 <= idx < 9:
                    internal[idx] = v if v not in (None, "") else None
            except Exception:
                continue
    elif isinstance(raw, list):
        for i, v in enumerate(raw[:9]):
            internal[i] = v if v not in (None, "") else None
    return internal


def internal_board_to_firebase(board: List[Optional[str]]):
    return [v if v is not None else "" for v in board[:9]]


def make_default_room_dict() -> Dict[str, Any]:
    return {
        "board": internal_board_to_firebase([None] * 9),
        "players": {},
        "turn": "X",
        "winner": ""
    }


def ensure_room_structure(room: Dict[str, Any]) -> Dict[str, Any]:
    board = firebase_board_to_internal(room.get("board"))
    room["board"] = internal_board_to_firebase(board)
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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/create")
def create_room():
    room_id = str(uuid.uuid4())[:8]
    db.reference(f"rooms/{room_id}").set(make_default_room_dict())
    print(f"[CREATE] Room {room_id} created.")
    return {"room_id": room_id}


@app.post("/join/{room_id}")
def join_room(room_id: str, payload: Optional[Dict] = None):
    ref = db.reference(f"rooms/{room_id}")
    room = ref.get()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room = ensure_room_structure(room)
    players = room.get("players", {}) or {}

    username = payload.get("username") if payload else None

    if not players.get("X"):
        players["X"] = username or f"player-{uuid.uuid4().hex[:6]}"
        assigned = "X"
    elif not players.get("O"):
        players["O"] = username or f"player-{uuid.uuid4().hex[:6]}"
        assigned = "O"
    else:
        raise HTTPException(status_code=400, detail="Room is full")

    ref.child("players").set(players)
    print(f"[JOIN] Room {room_id}: {assigned} joined as {players[assigned]}")
    return {"player": assigned, "room_id": room_id, "username": players[assigned]}


@app.get("/room/{room_id}")
def get_room(room_id: str):
    ref = db.reference(f"rooms/{room_id}")
    room = ref.get()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room = ensure_room_structure(room)
    internal_board = firebase_board_to_internal(room.get("board"))
    return {
        "board": internal_board,
        "players": room.get("players", {}),
        "turn": room.get("turn", "X"),
        "winner": room.get("winner", "")
    }


@app.post("/move/{room_id}")
def make_move(room_id: str, move: Dict):
    player = move.get("player")
    index = move.get("index")

    if player not in ("X", "O"):
        raise HTTPException(status_code=400, detail="Invalid player")
    if index is None or not isinstance(index, int) or not 0 <= index <= 8:
        raise HTTPException(status_code=400, detail="Invalid index")

    ref = db.reference(f"rooms/{room_id}")
    room = ref.get()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    board = firebase_board_to_internal(room.get("board"))
    turn = room.get("turn", "X")
    winner = room.get("winner", "")

    if winner:
        raise HTTPException(status_code=400, detail=f"Game already finished with winner {winner}")
    if board[index] not in (None, ""):
        raise HTTPException(status_code=400, detail="Invalid move: cell already filled")
    if player != turn:
        raise HTTPException(status_code=400, detail=f"Not your turn, it's {turn}'s move")

    board[index] = player
    new_winner = check_winner(board)
    next_turn = turn if new_winner else ("O" if turn == "X" else "X")

    ref.update({
        "board": internal_board_to_firebase(board),
        "turn": next_turn,
        "winner": new_winner or ""
    })

    if new_winner in ("X", "O"):
        players = room.get("players", {})
        winner_name = players.get(new_winner)
        loser_name = players.get("O" if new_winner == "X" else "X")
        if winner_name:
            update_leaderboard_and_history(room_id, winner_name, loser_name, players)

    print(f"[MOVE] Room {room_id} | Player {player} -> {index} | Winner: {new_winner}")
    return {"board": board, "turn": next_turn, "winner": new_winner}


def update_leaderboard_and_history(room_id, winner_name, loser_name, players):
    leaderboard = db.reference("leaderboard")
    history = db.reference("history")

    if winner_name:
        wref = leaderboard.child(winner_name)
        wdata = wref.get() or {"wins": 0, "losses": 0}
        wdata["wins"] = int(wdata["wins"]) + 1
        wref.set(wdata)

    if loser_name:
        lref = leaderboard.child(loser_name)
        ldata = lref.get() or {"wins": 0, "losses": 0}
        ldata["losses"] = int(ldata["losses"]) + 1
        lref.set(ldata)

    history.child(room_id).set({
        "room_id": room_id,
        "winner": winner_name,
        "players": players,
        "finished_at": datetime.utcnow().isoformat()
    })
    print(f"[LEADERBOARD] {winner_name}+1 win, {loser_name}+1 loss")


@app.post("/reset/{room_id}")
def reset_game(room_id: str):
    ref = db.reference(f"rooms/{room_id}")
    if not ref.get():
        raise HTTPException(status_code=404, detail="Room not found")
    ref.update({
        "board": internal_board_to_firebase([None] * 9),
        "turn": "X",
        "winner": ""
    })
    print(f"[RESET] Room {room_id} reset.")
    return {"status": "reset", "room_id": room_id}


@app.post("/ai-move")
def ai_move(data: Dict):
    board = data.get("board")
    player = data.get("player")
    if not isinstance(board, list) or player not in ("X", "O"):
        raise HTTPException(status_code=400, detail="Invalid data")
    best = find_best_move(board, player)
    return {"best_move": best}
