'use client';

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Share2,
  FileSearch,
  FolderGit2,
  Users,
  AlertTriangle,
  ShieldAlert,
  History,
  Database,
  BrainCircuit
} from "lucide-react";

type ClientShellProps = {
  children: React.ReactNode;
};

export default function ClientShell({ children }: ClientShellProps) {
  const pathname = usePathname();

  const navItems = [
    { name: "Home Dashboard", href: "/", icon: Home },
    { name: "Knowledge Graph", href: "/graph", icon: Share2 },
    { name: "Requirement Analyzer", href: "/analyzer", icon: FileSearch },
    { name: "Repository Intake", href: "/repositories", icon: FolderGit2 },
    { name: "Expert Finder", href: "/experts", icon: Users },
    { name: "Incident Room", href: "/incidents", icon: AlertTriangle },
    { name: "Knowledge Gaps", href: "/gaps", icon: ShieldAlert },
    { name: "Agent Activity Log", href: "/logs", icon: History }
  ];

  return (
    <body className="h-full flex overflow-hidden font-sans antialiased">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
        <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800 bg-slate-950/50">
          <BrainCircuit className="h-7 w-7 text-indigo-500 animate-pulse" />
          <div>
            <h1 className="font-bold text-lg tracking-tight text-white">CodeAtlas AI</h1>
            <span className="text-[10px] text-indigo-400 font-mono uppercase tracking-widest font-semibold">Engineering Brain</span>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-900/30"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? "text-white" : "text-slate-400"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800 bg-slate-950/30">
          <button
            type="button"
            onClick={async () => {
              if (confirm("Load the CodeAtlas demo dataset? This replaces the current in-memory sample data with services, repositories, requirements, incidents, teams, and engineers used in the guided demo.")) {
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
            <Database className="h-3.5 w-3.5" />
            Load Demo Data
          </button>
          <p className="mt-2 text-center text-[10px] leading-relaxed text-slate-500">
            Reloads the sample engineering company used by the demo.
          </p>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 bg-slate-950 overflow-hidden relative">
        <header className="h-16 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between px-8 shrink-0">
          <div>
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-widest font-mono">
              {navItems.find(item => item.href === pathname)?.name || "Dashboard"}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span className="text-xs text-slate-400 font-medium">Orchestrator Online</span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          {children}
        </div>
      </main>
    </body>
  );
}
