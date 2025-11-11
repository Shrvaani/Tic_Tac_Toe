import { useState } from "react";
import Home from "./pages/Home";

export default function App() {
  const [squares, setSquares] = useState(Array(9).fill(null));
  const [xIsNext, setXIsNext] = useState(true);
  const [difficulty, setDifficulty] = useState("easy");
  const [winner, setWinner] = useState(null);

  const checkWinner = (board) => {
    const lines = [
      [0,1,2],[3,4,5],[6,7,8],
      [0,3,6],[1,4,7],[2,5,8],
      [0,4,8],[2,4,6]
    ];
    for (let [a,b,c] of lines) {
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return board[a];
      }
    }
    return null;
  };

  const aiMove = (board) => {
    // For now, random AI — later connect to Python backend
    const empty = board.map((v, i) => (v ? null : i)).filter((v) => v !== null);
    return empty[Math.floor(Math.random() * empty.length)];
  };

  const handleClick = (i) => {
    if (squares[i] || winner) return;

    const newBoard = [...squares];
    newBoard[i] = "X";
    setSquares(newBoard);

    const result = checkWinner(newBoard);
    if (result) {
      setWinner(result);
      return;
    }

    setTimeout(() => {
      const aiIndex = aiMove(newBoard);
      if (aiIndex !== undefined) {
        newBoard[aiIndex] = "O";
        const res = checkWinner(newBoard);
        if (res) setWinner(res);
        setSquares([...newBoard]);
      }
    }, 400);
  };

  const resetGame = () => {
    setSquares(Array(9).fill(null));
    setWinner(null);
    setXIsNext(true);
  };

  return (
    <Home
      squares={squares}
      onClick={handleClick}
      difficulty={difficulty}
      setDifficulty={setDifficulty}
      winner={winner}
      resetGame={resetGame}
    />
  );
}
