import React, { useEffect, useState } from "react";
import { getHistory } from "../utils/api";

function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      const data = await getHistory();
      setHistory(data.sort((a, b) => (b.timestamp > a.timestamp ? 1 : -1)));
    };
    fetchHistory();
  }, []);

  const formatDate = (timestamp) => {
    if (!timestamp) return "Invalid Date";
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return "Invalid Date";
    }
  };

  return (
    <div className="flex flex-col items-center mt-10 text-white">
      <h2 className="text-3xl font-bold mb-6">Game History</h2>
      <table className="min-w-[700px] text-left border-separate border-spacing-y-2">
        <thead>
          <tr className="bg-gray-800">
            <th className="p-3">Room ID</th>
            <th className="p-3">Winner</th>
            <th className="p-3">Date</th>
          </tr>
        </thead>
        <tbody>
          {history.map((item) => (
            <tr key={item.id} className="bg-gray-900">
              <td className="p-3">{item.roomId}</td>
              <td className="p-3 text-green-400">{item.winner}</td>
              <td className="p-3">{formatDate(item.timestamp)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default History;
