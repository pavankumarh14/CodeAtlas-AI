import {
  Bot,
  FileCode2,
  Gauge,
  GitFork,
  Network,
  SearchCheck,
  Sparkles,
} from "lucide-react";

export type Explainability = {
  why_chosen: string;
  nodes_traversed: string[];
  documents_consulted: string[];
  similar_requirements: string[];
  confidence_score: number;
  contributing_agents: string[];
};

const nodeColor = (node: string) => {
  switch (node.split(":")[0]) {
    case "Service": return "border-blue-400/30 bg-blue-400/10 text-blue-300";
    case "Repository": return "border-violet-400/30 bg-violet-400/10 text-violet-300";
    case "Team": return "border-amber-400/30 bg-amber-400/10 text-amber-300";
    case "Engineer": return "border-emerald-400/30 bg-emerald-400/10 text-emerald-300";
    case "API": return "border-cyan-400/30 bg-cyan-400/10 text-cyan-300";
    case "Requirement": return "border-pink-400/30 bg-pink-400/10 text-pink-300";
    default: return "border-slate-700 bg-slate-800 text-slate-300";
  }
};

export function ExplainabilityPanel({ explainability }: { explainability: Explainability }) {
  const confidence = Math.max(0, Math.min(100, explainability.confidence_score));

  return (
    <aside className="rounded-2xl border border-indigo-500/25 bg-gradient-to-b from-indigo-950/35 via-slate-900 to-slate-900 p-5 shadow-xl shadow-indigo-950/10">
      <div className="mb-5 flex items-start justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <p className="flex items-center gap-2 text-sm font-bold text-white"><Sparkles className="h-4 w-4 text-indigo-400" /> Explainability Panel</p>
          <p className="mt-1 text-[11px] text-slate-400">Evidence behind this recommendation</p>
        </div>
        <div className="rounded-lg border border-indigo-400/30 bg-indigo-400/10 px-2 py-1 font-mono text-[10px] font-bold text-indigo-300">AUDITABLE</div>
      </div>

      <div className="grid grid-cols-[1fr_auto] items-center gap-4 rounded-xl border border-slate-800 bg-slate-950/70 p-3">
        <div>
          <p className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-widest text-slate-500"><Gauge className="h-3.5 w-3.5 text-indigo-400" /> Confidence score</p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400" style={{ width: `${confidence}%` }} /></div>
        </div>
        <span className="text-xl font-extrabold text-white">{confidence}%</span>
      </div>

      <section className="mt-5">
        <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-slate-500"><SearchCheck className="h-3.5 w-3.5 text-indigo-400" /> Why this answer was chosen</p>
        <p className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-xs leading-relaxed text-slate-300">{explainability.why_chosen}</p>
      </section>

      <section className="mt-5">
        <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-slate-500"><Network className="h-3.5 w-3.5 text-indigo-400" /> Graph nodes traversed</p>
        <div className="flex flex-wrap gap-1.5 rounded-xl border border-slate-800 bg-slate-950/60 p-3">
          {explainability.nodes_traversed.map((node) => <span key={node} className={`rounded-md border px-2 py-1 font-mono text-[9px] font-semibold ${nodeColor(node)}`}>{node}</span>)}
        </div>
      </section>

      <section className="mt-5 grid gap-4">
        <div>
          <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-slate-500"><FileCode2 className="h-3.5 w-3.5 text-indigo-400" /> Documents consulted</p>
          <ul className="space-y-1.5 rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-xs text-slate-300">
            {explainability.documents_consulted.map((document) => <li key={document} className="flex gap-2"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400" />{document}</li>)}
          </ul>
        </div>
        <div>
          <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-slate-500"><GitFork className="h-3.5 w-3.5 text-indigo-400" /> Similar requirements used</p>
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-xs text-slate-300">{explainability.similar_requirements.join(" · ")}</div>
        </div>
      </section>

      <section className="mt-5">
        <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-slate-500"><Bot className="h-3.5 w-3.5 text-indigo-400" /> Contributing agents</p>
        <div className="flex flex-wrap gap-2 rounded-xl border border-slate-800 bg-slate-950/60 p-3">
          {explainability.contributing_agents.map((agent, index) => <span key={agent} className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-200"><span className="flex h-4 w-4 items-center justify-center rounded-full bg-indigo-500/20 text-[9px] text-indigo-300">{index + 1}</span>{agent}</span>)}
        </div>
      </section>
    </aside>
  );
}
