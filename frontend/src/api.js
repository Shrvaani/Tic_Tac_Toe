// src/api.js

// Dynamically pick backend URL based on environment
const BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://tictactoe-production-85ab.up.railway.app" // Railway backend
    : "http://127.0.0.1:8000"; // Local backend for dev

// Generic fetch handler with error handling
async function safeFetch(url, options = {}) {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return await res.json();
  } catch (err) {
    console.error("❌ API Error:", err.message);
    throw err;
  }
}

// ---------------------- Multiplayer Endpoints ----------------------

export async function createRoom() {
  return await safeFetch(`${BASE_URL}/create`, { method: "POST" });
}

export async function joinRoom(roomId, username) {
  return await safeFetch(`${BASE_URL}/join/${roomId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
}

export async function getRoom(roomId) {
  return await safeFetch(`${BASE_URL}/room/${roomId}`);
}

export async function makeMove(roomId, player, index) {
  return await safeFetch(`${BASE_URL}/move/${roomId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player, index }),
  });
}

export async function resetRoom(roomId) {
  return await safeFetch(`${BASE_URL}/reset/${roomId}`, { method: "POST" });
}

// ---------------------- AI (Single Player) ----------------------

export async function aiMove(board, player) {
  return await safeFetch(`${BASE_URL}/ai-move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ board, player }),
  });
}

// ---------------------- Firebase Leaderboard & History ----------------------

export async function getLeaderboard() {
  return await safeFetch(
    "https://tictactoe-multiplayer-581b6-default-rtdb.asia-southeast1.firebasedatabase.app/leaderboard.json"
  );
}

export async function getHistory() {
  return await safeFetch(
    "https://tictactoe-multiplayer-581b6-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"
  );
}
