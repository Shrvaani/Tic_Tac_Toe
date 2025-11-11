export default function Square({ value, onClick }) {
    return (
      <button
        onClick={onClick}
        className="w-20 h-20 text-4xl font-bold flex items-center justify-center 
                   bg-slate-800 border border-slate-700 hover:bg-slate-600 transition-all duration-200"
      >
        {value}
      </button>
    );
  }
  