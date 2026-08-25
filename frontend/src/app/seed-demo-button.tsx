'use client';

export default function SeedDemoButton() {
  return (
    <button
      type="button"
      onClick={async () => {
        if (
          confirm(
            "Load the CodeAtlas demo dataset? This replaces the current in-memory sample data with services, repositories, requirements, incidents, teams, and engineers used in the guided demo."
          )
        ) {
          try {
            const res = await fetch("/api/v1/seed", { method: "POST" });
            if (res.ok) {
              alert("Demo data loaded successfully!");
              window.location.reload();
            } else {
              alert("Seed failed. Ensure the backend server is running.");
            }
          } catch (e) {
            alert("Network error connecting to backend: " + e);
          }
        }
      }}
      className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 active:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-semibold tracking-wider uppercase transition-colors flex items-center justify-center gap-2"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="h-3.5 w-3.5"
        aria-hidden
      >
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M3 5V19A9 3 0 0 0 21 19V5" />
        <path d="M3 12A9 3 0 0 0 21 12" />
      </svg>
      Load Demo Data
    </button>
  );
}
