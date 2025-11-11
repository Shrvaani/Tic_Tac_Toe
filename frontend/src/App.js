import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Multiplayer from "./pages/Multiplayer";
import Board from "./components/Board";
import History from "./pages/History";
import Leaderboard from "./components/Leaderboard";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-black text-white">
        {/* Simple Navbar */}
        <nav className="flex justify-end gap-6 p-4 bg-gray-900 shadow">
          <Link to="/" className="hover:text-blue-400">
            Home
          </Link>
          <Link to="/leaderboard" className="hover:text-blue-400">
            Leaderboard
          </Link>
          <Link to="/history" className="hover:text-blue-400">
            History
          </Link>
        </nav>

        {/* Main Routes */}
        <Routes>
          <Route path="/" element={<Home />} /> {/* Landing Page */}
          <Route path="/singleplayer" element={<Board />} /> {/* AI Mode */}
          <Route path="/multiplayer" element={<Multiplayer />} /> {/* Online */}
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
