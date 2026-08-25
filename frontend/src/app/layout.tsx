import type { Metadata } from "next";
import Link from "next/link";
import SeedDemoButton from "./seed-demo-button";
import "./globals.css";

export const metadata: Metadata = {
  title: "CodeAtlas AI - The Living Engineering Ontology & Knowledge Graph",
  description: "AI-powered Knowledge Graph & Living Ontology Platform for Engineering Organizations",
};

const ICON_PATH_SVG = {
  Home:
    '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
  Share2:
    '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
  FileSearch:
    '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><circle cx="11.5" cy="14.5" r="2.5"/><path d="m13.27 16.27 1.9 1.9"/>',
  FolderGit2:
    '<path d="M9 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H20a2 2 0 0 1 2 2v5"/><circle cx="13" cy="12" r="2"/><circle cx="20" cy="19" r="2"/><path d="m15 9-3-3"/><path d="M18 19c-1.5-1.5-3-2-5-2s-3.5.5-5 2"/>',
  Users:
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  AlertTriangle:
    '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  ShieldAlert:
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
  History:
    '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
  BrainCircuit:
    '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/>',
  Database:
    '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
};

function IconSVG({ iconName, className }: { iconName: keyof typeof ICON_PATH_SVG; className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden
      dangerouslySetInnerHTML={{ __html: ICON_PATH_SVG[iconName] }}
    />
  );
}

const navItems: Array<{ name: string; href: string; icon: keyof typeof ICON_PATH_SVG }> = [
  { name: "Home Dashboard", href: "/", icon: "Home" },
  { name: "Knowledge Graph", href: "/graph", icon: "Share2" },
  { name: "Requirement Analyzer", href: "/analyzer", icon: "FileSearch" },
  { name: "Repository Intake", href: "/repositories", icon: "FolderGit2" },
  { name: "Expert Finder", href: "/experts", icon: "Users" },
  { name: "Incident Room", href: "/incidents", icon: "AlertTriangle" },
  { name: "Knowledge Gaps", href: "/gaps", icon: "ShieldAlert" },
  { name: "Agent Activity Log", href: "/logs", icon: "History" },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-950 text-slate-100 dark">
      <body className="h-full flex overflow-hidden font-sans antialiased">
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
          <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800 bg-slate-950/50">
            <IconSVG iconName="BrainCircuit" className="h-7 w-7 text-indigo-500 animate-pulse" />
            <div>
              <h1 className="font-bold text-lg tracking-tight text-white">CodeAtlas AI</h1>
              <span className="text-[10px] text-indigo-400 font-mono uppercase tracking-widest font-semibold">Engineering Brain</span>
            </div>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                data-href={item.href}
                data-nav-link
                className="nav-item flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
              >
                <IconSVG iconName={item.icon} className="nav-icon h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>

          <div className="p-4 border-t border-slate-800 bg-slate-950/30">
            <SeedDemoButton />
            <p className="mt-2 text-center text-[10px] leading-relaxed text-slate-500">
              Reloads the sample engineering company used by the demo.
            </p>
          </div>
        </aside>

        <main className="flex-1 flex flex-col min-w-0 bg-slate-950 overflow-hidden relative">
          <header className="h-16 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between px-8 shrink-0">
            <div>
              <h2
                className="text-sm font-semibold text-slate-300 uppercase tracking-widest font-mono"
                data-header-title="Dashboard"
                data-nav-title
              />
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

        <script
          dangerouslySetInnerHTML={{
            __html: `
(function () {
  try {
    var path = window.location.pathname.replace(/\\/+$/, '') || '/';
    var links = document.querySelectorAll('[data-nav-link]');
    links.forEach(function (a) {
      var href = a.getAttribute('data-href') || a.getAttribute('href');
      if (!href) return;
      var clean = href.replace(/\\/+$/, '') || '/';
      if (clean === path) a.setAttribute('data-active', 'true');
    });
    var titleEl = document.querySelector('[data-nav-title]');
    if (titleEl) {
      var activeLink = document.querySelector('[data-nav-link][data-active="true"]');
      if (activeLink) {
        var label = activeLink.textContent || 'Dashboard';
        titleEl.setAttribute('data-header-title', (label || '').trim());
      }
    }
  } catch (e) { /* no-op if DOM not ready */ }
})();
`,
          }}
          defer
        />
      </body>
    </html>
  );
}
