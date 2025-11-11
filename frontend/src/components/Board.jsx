import React, { useState } from "react";
import { aiMove } from "../utils/api";
import DifficultySelector from "../components/DifficultySelector";

function Board() {
  const [board, setBoard] = useState(Array(9).fill(null));
  const [winner, setWinner] = useState(null);
  const [turn, setTurn] = useState("X");
  const [difficulty, setDifficulty] = useState("medium");

  const checkWinner = (b) => {
    const combos = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
    ];
    for (const [a, b_, c] of combos) {
      if (b[a] && b[a] === b[b_] && b[a] === b[c]) return b[a];
    }
    if (b.every((cell) => cell)) return "DRAW";
    return null;
  };

  const handleClick = async (index) => {
    if (winner || board[index] !== null || turn !== "X") return;

    // Human move
    const newBoard = [...board];
    newBoard[index] = "X";
    setBoard(newBoard);
    setTurn("O");

    const humanWin = checkWinner(newBoard);
    if (humanWin) {
      setWinner(humanWin);
      return;
    }

    try {
      // Normalize board for backend
      const normalizedBoard = newBoard.map((cell) =>
        cell === "" ? null : cell
      );

      // Decide AI move based on difficulty
      let aiIndex;

      if (difficulty === "easy") {
        // 70% chance random move, 30% smart
        const emptyCells = normalizedBoard
          .map((v, i) => (v === null ? i : null))
          .filter((v) => v !== null);
        if (Math.random() < 0.7) {
          aiIndex =
            emptyCells[Math.floor(Math.random() * emptyCells.length)];
        } else {
          const res = await aiMove(normalizedBoard, "O");
          aiIndex = res.best_move;
        }
      } else if (difficulty === "medium") {
        // 50% random, 50% smart
        const emptyCells = normalizedBoard
          .map((v, i) => (v === null ? i : null))
          .filter((v) => v !== null);
        if (Math.random() < 0.5) {
          aiIndex =
            emptyCells[Math.floor(Math.random() * emptyCells.length)];
        } else {
          const res = await aiMove(normalizedBoard, "O");
          aiIndex = res.best_move;
        }
      } else {
        // hard = always optimal
        const res = await aiMove(normalizedBoard, "O");
        aiIndex = res.best_move;
      }

      // Apply AI move
      if (aiIndex !== null && aiIndex !== undefined && newBoard[aiIndex] === null) {
        setTimeout(() => {
          const aiBoard = [...newBoard];
          aiBoard[aiIndex] = "O";
          const aiWin = checkWinner(aiBoard);
          setBoard(aiBoard);
          if (aiWin) setWinner(aiWin);
          else setTurn("X");
        }, 400);
      } else {
        setTurn("X");
      }
    } catch (err) {
      console.error("AI move error:", err);
      setTurn("X");
    }
  };

  const resetGame = () => {
    setBoard(Array(9).fill(null));
    setWinner(null);
    setTurn("X");
  };

  return (
    <div className="flex flex-col items-center text-white mt-12">
      <h2 className="text-3xl mb-4 font-semibold">Single Player (vs AI)</h2>

      <DifficultySelector
        difficulty={difficulty}
        setDifficulty={setDifficulty}
      />

      {winner && (
        <div className="text-lg text-green-400 mb-3">
          {winner === "DRAW" ? "It's a Draw!" : `Winner: ${winner}`}
        </div>
      )}

      <div className="grid grid-cols-3 gap-3">
        {board.map((cell, i) => (
          <button
            key={i}
            className="w-20 h-20 bg-gray-800 text-3xl font-bold rounded hover:bg-gray-700"
            onClick={() => handleClick(i)}
          >
            {cell}
          </button>
        ))}
      </div>

      <div className="mt-5 flex gap-4">
        <button
          onClick={resetGame}
          className="bg-gray-700 hover:bg-gray-600 px-6 py-2 rounded"
        >
          Reset Game
        </button>
      </div>
    </div>
  );
}

export default Board;
