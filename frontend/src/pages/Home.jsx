import React from "react";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="text-white flex flex-col items-center mt-20 gap-6">
      <h1 className="text-5xl font-extrabold mb-6">Tic Tac Toe</h1>

      <button
        onClick={() => navigate("/singleplayer")}
        className="bg-blue-600 hover:bg-blue-700 px-6 py-4 rounded-lg w-80 text-xl"
      >
        Single Player (vs AI)
      </button>

      <button
        onClick={() => navigate("/multiplayer")}
        className="bg-green-600 hover:bg-green-700 px-6 py-4 rounded-lg w-80 text-xl"
      >
        Multiplayer Mode
      </button>
    </div>
  );
}

export default Home;
