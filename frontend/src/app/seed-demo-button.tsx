'use client';

import React from "react";

export default function SeedDemoButton() {
  return (
    <div className="space-y-2">
      <button
        type="button"
        onClick={async () => {
          if (
            confirm(
              "Seed real architecture mapped to your GitHub repositories (pavankumarh14) and auto-sync Freshservice incidents into Neo4j?"
            )
          ) {
            try {
              const res = await fetch("/api/v1/seed/real", { method: "POST" });
              if (res.ok) {
                // Auto-sync freshservice tickets right after
                try {
                  await fetch("/api/v1/freshworks/sync", { method: "POST" });
                } catch {}
                alert("Real Architecture & Freshservice incidents populated successfully!");
                window.location.reload();
              } else {
                alert("Real architecture seed failed. Ensure the backend server is running.");
              }
            } catch (e) {
              alert("Network error: " + e);
            }
          }
        }}
        className="w-full py-2 px-3 bg-gradient-to-r from-indigo-900/60 to-purple-900/60 hover:from-indigo-800 hover:to-purple-800 active:scale-[0.98] border border-indigo-500/40 text-indigo-200 hover:text-white rounded-lg text-xs font-semibold tracking-wider uppercase transition-all flex items-center justify-center gap-2 cursor-pointer shadow-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-3.5 w-3.5 text-indigo-400" aria-hidden>
          <path d="M12 2v20" />
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>
        Seed Real Architecture
      </button>

      <button
        type="button"
        onClick={async () => {
          if (
            confirm(
              "Load the CodeAtlas demo dataset? This populates 20 services, 20 repos, 50 requirements, and 30 incidents into Neo4j."
            )
          ) {
            try {
              const res = await fetch("/api/v1/seed", { method: "POST" });
              if (res.ok) {
                alert("Demo data populated successfully!");
                window.location.reload();
              } else {
                alert("Seed failed. Ensure the backend server is running.");
              }
            } catch (e) {
              alert("Network error: " + e);
            }
          }
        }}
        className="w-full py-2 px-3 bg-slate-800 hover:bg-slate-700 active:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-semibold tracking-wider uppercase transition-colors flex items-center justify-center gap-2 cursor-pointer"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-3.5 w-3.5" aria-hidden>
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M3 5V19A9 3 0 0 0 21 19V5" />
          <path d="M3 12A9 3 0 0 0 21 12" />
        </svg>
        Load Generic Demo
      </button>

      <button
        type="button"
        onClick={async () => {
          if (
            confirm(
              "Wipe all nodes, relationships, and vectors from Neo4j to start completely fresh?"
            )
          ) {
            try {
              const res = await fetch("/api/v1/database/clear", { method: "POST" });
              if (res.ok) {
                alert("Database wiped clean! (0 nodes in Neo4j)");
                window.location.reload();
              } else {
                alert("Failed to clear database.");
              }
            } catch (e) {
              alert("Network error: " + e);
            }
          }
        }}
        className="w-full py-2 px-3 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/40 text-rose-300 hover:text-rose-200 rounded-lg text-xs font-semibold tracking-wider uppercase transition-colors flex items-center justify-center gap-2 cursor-pointer"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-3.5 w-3.5" aria-hidden>
          <path d="M3 6h18" />
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
        </svg>
        Wipe / Clear DB
      </button>
    </div>
  );
}
