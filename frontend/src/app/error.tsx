'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="w-full max-w-lg mx-auto p-8 rounded-2xl bg-slate-900 border border-slate-800 text-center">
      <div className="mb-6">
        <div className="w-14 h-14 mx-auto rounded-full bg-rose-500/10 flex items-center justify-center mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-7 w-7 text-rose-500"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <h2 className="text-lg font-bold text-white mb-2">Something went wrong</h2>
        <p className="text-sm text-slate-400">
          Failed to load this section. You can try again.
        </p>
        {error.digest && (
          <p className="mt-3 text-xs font-mono text-slate-500 break-all">
            Error ID: {error.digest}
          </p>
        )}
      </div>
      <button
        onClick={() => retry()}
        className="py-2.5 px-5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition shadow-md shadow-indigo-900/40"
      >
        Try again
      </button>
    </div>
  );
}
