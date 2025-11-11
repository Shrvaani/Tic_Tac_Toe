// src/utils/api.js

const API_BASE = "http://127.0.0.1:8000";
const FIREBASE_DB =
  "https://tictactoe-multiplayer-581b6-default-rtdb.asia-southeast1.firebasedatabase.app";

// -------------------- Multiplayer APIs --------------------

export const createRoom = async () => {
  const res = await fetch(`${API_BASE}/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Failed to create room");
  return await res.json();
};

export const joinRoom = async (roomId, username) => {
  const res = await fetch(`${API_BASE}/join/${roomId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  if (!res.ok) throw new Error("Failed to join room");
  return await res.json();
};

export const getRoom = async (roomId) => {
  const res = await fetch(`${API_BASE}/room/${roomId}`);
  if (!res.ok) throw new Error("Room not found");
  return await res.json();
};

export const makeMove = async (roomId, move) => {
  const res = await fetch(`${API_BASE}/move/${roomId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(move),
  });
  if (!res.ok) throw new Error("Failed to make move");
  return await res.json();
};

export const resetRoom = async (roomId) => {
  const res = await fetch(`${API_BASE}/reset/${roomId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Failed to reset room");
  return await res.json();
};

// -------------------- AI Mode --------------------

export const aiMove = async (board, player) => {
  const res = await fetch(`${API_BASE}/ai-move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ board, player }),
  });
  if (!res.ok) throw new Error("AI move failed");
  return await res.json();
};

// -------------------- Firebase Leaderboard --------------------

export const getLeaderboard = async () => {
  const res = await fetch(`${FIREBASE_DB}/leaderboard.json`);
  const data = await res.json();
  if (!data) return [];

  // Each key is a username
  return Object.entries(data).map(([username, stats]) => ({
    username,
    wins: stats.wins || 0,
    losses: stats.losses || 0,
  }));
};

// -------------------- Firebase Game History --------------------

export const getHistory = async () => {
  const res = await fetch(`${FIREBASE_DB}/history.json`);
  const data = await res.json();
  if (!data) return [];

  // Each key is a room_id
  return Object.entries(data).map(([roomId, item]) => ({
    id: roomId,
    roomId: item.room_id || roomId,
    winner: item.winner || "—",
    timestamp: item.finished_at || null, // match backend key
  }));
};
