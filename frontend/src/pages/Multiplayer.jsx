// src/pages/Multiplayer.jsx
import React, { useState, useEffect } from "react";
import {
  createRoom,
  joinRoom,
  getRoom,
  makeMove,
  resetRoom,
} from "../utils/api";

function Multiplayer() {
  const [username, setUsername] = useState("");
  const [roomId, setRoomId] = useState("");
  const [joinedRoom, setJoinedRoom] = useState(null);
  const [player, setPlayer] = useState("");
  const [board, setBoard] = useState(Array(9).fill(null));
  const [turn, setTurn] = useState("");
  const [winner, setWinner] = useState(null);
  const [mode, setMode] = useState(""); // "create" | "join" | ""
  const [error, setError] = useState("");

  // --- CREATE ROOM ---
  const handleCreateRoom = async () => {
    try {
      if (!username.trim()) {
        setError("Please enter a username");
        return;
      }

      const createRes = await createRoom();
      if (!createRes?.room_id) {
        setError("Failed to create room. Try again.");
        return;
      }

      const newRoomId = createRes.room_id;
      setRoomId(newRoomId);

      const joinRes = await joinRoom(newRoomId, username);
      if (joinRes.error) {
        setError(joinRes.error);
        return;
      }

      setPlayer(joinRes.player);
      setJoinedRoom({
        room_id: newRoomId,
        players: { [joinRes.player]: username },
        board: Array(9).fill(null),
        turn: "X",
        winner: null,
      });

      setError("");
      setMode("");
    } catch (err) {
      console.error(err);
      setError("Failed to create room. Try again.");
    }
  };

  // --- JOIN ROOM ---
  const handleJoinRoom = async () => {
    try {
      if (!roomId.trim() || !username.trim()) {
        setError("Enter both username and room ID");
        return;
      }

      const res = await joinRoom(roomId, username);
      if (res.error) {
        setError(res.error);
        return;
      }

      setPlayer(res.player);
      setJoinedRoom({
        room_id: roomId,
        players: { [res.player]: username },
        board: Array(9).fill(null),
        turn: "X",
        winner: null,
      });

      setError("");
      setMode("");
    } catch (err) {
      console.error(err);
      setError("Failed to join room. Try again.");
    }
  };

  // --- POLL ROOM STATE ---
  useEffect(() => {
    if (!roomId) return;
    const interval = setInterval(async () => {
      try {
        const roomData = await getRoom(roomId);
        if (roomData) {
          setJoinedRoom((prev) => ({ ...prev, ...roomData }));
          if (roomData.board) setBoard(roomData.board);
          if (roomData.turn) setTurn(roomData.turn);
          if (roomData.winner) setWinner(roomData.winner);
        }
      } catch {
        clearInterval(interval);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [roomId]);

  // --- MAKE MOVE ---
  const handleMove = async (index) => {
    if (winner || !joinedRoom) return;
    if (board[index]) return; // prevent overwriting moves

    try {
      await makeMove(roomId, { index, player });
    } catch (err) {
      console.error(err);
    }
  };

  // --- RESET ROOM ---
  const handleReset = async () => {
    try {
      await resetRoom(roomId);
    } catch (err) {
      console.error(err);
    }
  };

  // --- EXIT ROOM ---
  const handleExit = () => {
    setJoinedRoom(null);
    setMode("");
    setUsername("");
    setRoomId("");
    setPlayer("");
    setBoard(Array(9).fill(null));
    setTurn("");
    setWinner(null);
    setError("");
  };

  // --- UI ---
  return (
    <div className="flex flex-col items-center text-white mt-12">
      <h2 className="text-3xl mb-4 font-semibold">Tic Tac Toe Multiplayer</h2>

      {/* STEP 1: Mode Selection */}
      {!mode && !joinedRoom && (
        <div className="flex flex-col gap-6 mt-8">
          <button
            onClick={() => setMode("create")}
            className="bg-green-600 hover:bg-green-700 px-6 py-4 rounded-lg w-80 text-lg"
          >
            Create Room
          </button>
          <button
            onClick={() => setMode("join")}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-4 rounded-lg w-80 text-lg"
          >
            Join Room
          </button>
        </div>
      )}

      {/* STEP 2A: Create Room */}
      {mode === "create" && !joinedRoom && (
        <div className="flex flex-col items-center gap-4 mt-6">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter Username"
            className="p-3 text-black rounded w-80"
          />
          <button
            onClick={handleCreateRoom}
            className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg w-80 text-lg"
          >
            Create Room
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </div>
      )}

      {/* STEP 2B: Join Room */}
      {mode === "join" && !joinedRoom && (
        <div className="flex flex-col items-center gap-4 mt-6">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter Username"
            className="p-3 text-black rounded w-80"
          />
          <input
            type="text"
            value={roomId}
            onChange={(e) => setRoomId(e.target.value)}
            placeholder="Enter Room ID"
            className="p-3 text-black rounded w-80"
          />
          <button
            onClick={handleJoinRoom}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg w-80 text-lg"
          >
            Join Room
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </div>
      )}

      {/* STEP 3: Game Board */}
      {joinedRoom && (
        <>
          <p className="mt-4">
            Room ID: <span className="bg-gray-700 px-2 py-1 rounded">{roomId}</span>
          </p>
          <p className="mt-2">
            You are Player: <b>{player}</b> ({username})
          </p>
          <p>Turn: <b>{turn}</b></p>

          {winner && (
            <div className="text-lg text-green-400 mb-3">
              {winner === "DRAW" ? "It's a Draw!" : `Winner: ${winner}`}
            </div>
          )}

          <div className="grid grid-cols-3 gap-3 mt-5">
            {board.map((cell, i) => (
              <button
                key={i}
                className="w-20 h-20 bg-gray-800 text-3xl font-bold rounded hover:bg-gray-700"
                onClick={() => handleMove(i)}
              >
                {cell}
              </button>
            ))}
          </div>

          <div className="flex gap-4 mt-6">
            <button
              onClick={handleReset}
              className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded"
            >
              Reset Game
            </button>
            <button
              onClick={handleExit}
              className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded"
            >
              Exit Room
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Multiplayer;
