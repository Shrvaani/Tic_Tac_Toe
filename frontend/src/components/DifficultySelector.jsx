export default function DifficultySelector({ difficulty, setDifficulty }) {
    const levels = ["easy", "medium", "hard"];
    return (
      <div className="flex gap-4 justify-center my-4">
        {levels.map((lvl) => (
          <button
            key={lvl}
            onClick={() => setDifficulty(lvl)}
            className={`px-4 py-2 rounded-lg border ${
              difficulty === lvl
                ? "bg-blue-600 border-blue-400"
                : "bg-slate-700 border-slate-600"
            } hover:bg-blue-700 transition`}
          >
            {lvl.toUpperCase()}
          </button>
        ))}
      </div>
    );
  }
  