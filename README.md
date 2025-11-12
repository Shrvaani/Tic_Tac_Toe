# Tic Tac Toe (AI + Multiplayer)

A full-stack Tic Tac Toe experience with a React front end and a FastAPI backend. Play solo against an adaptive AI, challenge friends online in real time, and track wins through a Firebase-backed leaderboard and game history.

## Features

- **Single-player vs AI**: Select from easy, medium, or hard. AI moves are calculated server-side; easier levels mix optimal play with random moves.
- **Online multiplayer**: Create or join rooms, take turns in real time, and reset matches without leaving the lobby.
- **Leaderboard & history**: Player wins/losses and finished games persist in Firebase Realtime Database.
- **FastAPI backend**: REST endpoints manage rooms, moves, AI decisions, and persistence layers.
- **React + Tailwind UI**: Responsive layout with routing for home, gameplay modes, leaderboard, and history views.

## Project Structure

```
frontend/
  src/
    App.js / App.jsx         # SPA routing and legacy single-player prototype
    components/              # Board, Leaderboard, DifficultySelector
    pages/                   # Home, Multiplayer, History
    utils/api.js             # Fetch helpers to backend + Firebase
server/
  app.py                     # FastAPI application
  requirements.txt           # Backend deps
Procfile                     # Uvicorn entry for deployment
requirements.txt             # Convenience mirror of backend deps
```

## Prerequisites

- Node.js 18+ (for `npm` scripts)
- Python 3.10+ with `pip`
- Firebase project with Realtime Database enabled
- Service account credentials (JSON)

## Backend Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Provide Firebase credentials either by:

   - Copying your service account JSON to `server/serviceAccountKey.json`, **or**
   - Setting an environment variable with the JSON contents:

     ```bash
     export FIREBASE_CREDENTIALS_JSON='{"type": "..."}'
     ```

   Optional override for the DB endpoint:

   ```bash
   export FIREBASE_DB_URL="https://your-project-id-default-rtdb.region.firebasedatabase.app"
   ```

4. Run the API:

   ```bash
   uvicorn app:app --reload --app-dir server --host 127.0.0.1 --port 8000
   ```

   Key endpoints live under `http://127.0.0.1:8000`:

   - `POST /create` -> `{ room_id }`
   - `POST /join/{room_id}` body `{ username }`
   - `GET /room/{room_id}`
   - `POST /move/{room_id}` body `{ index, player }`
   - `POST /reset/{room_id}`
   - `POST /ai-move` body `{ board, player }`

   The backend auto-initializes Firebase and updates leaderboard/history when games finish.

## Frontend Setup

1. Install packages:

   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:

   ```bash
   npm start
   ```

   The app expects the FastAPI server on `http://127.0.0.1:8000`. Adjust `API_BASE` in `src/utils/api.js` if needed.

3. Tailwind CSS is preconfigured via `postcss.config.js` and `tailwind.config.js`. Editing `src/styles/index.css` updates global styles.

## Deployment Notes

- The provided `Procfile` runs `uvicorn` with the backend app; adapt for hosting platforms like Heroku or Render.
- Ensure Firebase credentials are injected as environment variables in production rather than bundled files.
- If you need advanced AI, add a real `ai/minimax.py` module; `server/app.py` includes a fallback stub.

## Testing & Troubleshooting

- Use `npm test` for React tests (default CRA suite).
- For backend checks, leverage FastAPI’s built-in docs at `http://127.0.0.1:8000/docs`.
- Multiplayer polling relies on Firebase and backend endpoints; confirm both are reachable and CORS is configured appropriately (`app.py` currently allows all origins).

Enjoy building and extending the game!