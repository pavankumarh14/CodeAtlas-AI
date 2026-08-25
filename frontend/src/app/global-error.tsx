'use client';

import { useEffect } from 'react';

export default function GlobalError({
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
    <html lang="en" className="h-full bg-slate-950 text-slate-100 dark">
      <body className="h-full flex items-center justify-center font-sans antialiased">
        <div className="w-full max-w-md p-8 rounded-2xl bg-slate-900 border border-slate-800 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 mx-auto rounded-full bg-rose-500/10 flex items-center justify-center mb-4">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 text-rose-500"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Something went wrong</h2>
            <p className="text-sm text-slate-400">
              An unexpected error occurred while loading the application.
            </p>
            {error.digest && (
              <p className="mt-3 text-xs font-mono text-slate-500 break-all">
                Error ID: {error.digest}
              </p>
            )}
          </div>
          <button
            onClick={() => retry()}
            className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition shadow-md shadow-indigo-900/40"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
