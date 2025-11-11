import React, { useEffect, useState } from "react";
import { getLeaderboard } from "../utils/api";

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getLeaderboard();
      setLeaderboard(data.sort((a, b) => b.wins - a.wins));
    };
    fetchData();
  }, []);

  return (
    <div className="flex flex-col items-center mt-10 text-white">
      <h2 className="text-3xl font-bold mb-6">Leaderboard</h2>
      <table className="min-w-[600px] text-left border-separate border-spacing-y-2">
        <thead>
          <tr className="bg-gray-800">
            <th className="p-3">#</th>
            <th className="p-3">Username</th>
            <th className="p-3">Wins</th>
            <th className="p-3">Losses</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((entry, index) => (
            <tr key={entry.username} className="bg-gray-900">
              <td className="p-3">{index + 1}</td>
              <td className="p-3">{entry.username}</td>
              <td className="p-3">{entry.wins}</td>
              <td className="p-3">{entry.losses}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Leaderboard;
