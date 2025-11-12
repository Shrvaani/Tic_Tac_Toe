// src/api.js
const BASE_URL = "tictactoe-production-85ab.up.railway.app";

export async function createRoom() {
  const res = await fetch(`${BASE_URL}/create`, { method: "POST" });
  return res.json();
}

export async function joinRoom(roomId, username) {
  const res = await fetch(`${BASE_URL}/join/${roomId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  return res.json();
}

export async function getRoom(roomId) {
  const res = await fetch(`${BASE_URL}/room/${roomId}`);
  return res.json();
}

export async function makeMove(roomId, player, index) {
  const res = await fetch(`${BASE_URL}/move/${roomId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player, index }),
  });
  return res.json();
}

export async function resetRoom(roomId) {
  const res = await fetch(`${BASE_URL}/reset/${roomId}`, { method: "POST" });
  return res.json();
}

export async function getLeaderboard() {
  const res = await fetch(
    "https://tictactoe-multiplayer-581b6-default-rtdb.asia-southeast1.firebasedatabase.app/leaderboard.json"
  );
  return res.json();
}

export async function getHistory() {
  const res = await fetch(
    "https://tictactoe-multiplayer-581b6-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"
  );
  return res.json();
}
