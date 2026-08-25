"use client";

import { useState } from "react";
import { Archive, CheckCircle2, CloudUpload, FolderGit2, GitBranch, LockKeyhole, Sparkles } from "lucide-react";

type RepositoryProfile = {
  repository: string;
  url: string;
  description: string;
  default_branch: string;
  languages: string[];
  files_scanned: number;
  tree_truncated: boolean;
  manifests: string[];
  documents: string[];
  api_candidates: string[];
  graph_nodes_added: number;
};

export default function RepositoryIntakePage() {
  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceName, setSourceName] = useState("");
  const [staged, setStaged] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [profile, setProfile] = useState<RepositoryProfile | null>(null);

  const stageRepository = (event: React.FormEvent) => {
    event.preventDefault();
    if (!sourceUrl.trim() && !sourceName.trim()) return;
    setStaged(true);
  };

  const analyzePublicRepository = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!sourceUrl.trim()) return;
    setLoading(true);
    setError("");
    setProfile(null);
    try {
      const response = await fetch("/api/v1/repositories/import", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ repository_url: sourceUrl }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Could not inspect this repository.");
      setProfile(payload);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not inspect this repository.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-7 animate-fadeIn">
      <div className="rounded-2xl border border-indigo-500/25 bg-gradient-to-r from-indigo-950/35 via-slate-900 to-slate-900 p-7">
        <div className="flex items-start gap-4">
          <div className="rounded-xl bg-indigo-500/15 p-3"><FolderGit2 className="h-7 w-7 text-indigo-300" /></div>
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-indigo-300">Bring your own engineering context</p>
            <h2 className="mt-1 text-2xl font-bold text-white">Repository Intake</h2>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-400">Add a repository source to the Engineering Brain. The next ingestion step maps its code, APIs, dependencies, documentation, and ownership into the knowledge graph.</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <form onSubmit={analyzePublicRepository} className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center gap-2"><GitBranch className="h-5 w-5 text-indigo-400" /><h3 className="font-bold text-white">Public Git repository</h3></div>
          <p className="mt-2 text-xs leading-relaxed text-slate-400">Paste a public GitHub URL. CodeAtlas reads repository metadata and file structure in real time, then adds discovered documentation to the graph.</p>
          <label className="mt-5 block text-xs font-semibold text-slate-300">Repository URL</label>
          <input value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} placeholder="https://github.com/org/repository" className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-indigo-400" />
          <button type="submit" disabled={loading} className="mt-4 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:opacity-50"><Sparkles className="h-4 w-4" /> {loading ? "Inspecting repository…" : "Analyze public repository"}</button>
        </form>

        <form onSubmit={stageRepository} className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center gap-2"><Archive className="h-5 w-5 text-amber-400" /><h3 className="font-bold text-white">ZIP source upload</h3></div>
          <p className="mt-2 text-xs leading-relaxed text-slate-400">Use this for a local repository or source bundle. The upload control is ready for the repository-ingestion service.</p>
          <label className="mt-5 flex min-h-28 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-950/70 p-4 text-center transition hover:border-indigo-400">
            <CloudUpload className="h-6 w-6 text-slate-500" />
            <span className="mt-2 text-sm font-semibold text-slate-300">Choose a ZIP file</span>
            <span className="mt-1 text-[11px] text-slate-500">Source stays private to your deployment.</span>
            <input type="file" accept=".zip,application/zip" className="sr-only" onChange={(event) => { setSourceName(event.target.files?.[0]?.name || ""); setStaged(false); }} />
          </label>
          <button type="submit" disabled={!sourceName} className="mt-4 inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"><CloudUpload className="h-4 w-4" /> Stage upload</button>
        </form>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex items-center gap-2"><LockKeyhole className="h-4 w-4 text-slate-400" /><h3 className="text-sm font-bold text-white">Safe ingestion contract</h3></div>
        <div className="mt-4 grid gap-3 text-xs text-slate-400 md:grid-cols-3">
          <p><span className="font-semibold text-slate-200">1. Read structure</span><br />Identify manifests, services, routes, tests, and docs.</p>
          <p><span className="font-semibold text-slate-200">2. Build context</span><br />Connect code evidence to graph nodes and existing requirements.</p>
          <p><span className="font-semibold text-slate-200">3. Explain action</span><br />Show exactly which files and relationships informed each recommendation.</p>
        </div>
      </div>

      {staged && (
        <div className="flex items-start gap-3 rounded-2xl border border-emerald-400/25 bg-emerald-500/10 p-5">
          <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />
          <div><p className="text-sm font-bold text-emerald-200">Repository source staged</p><p className="mt-1 text-xs leading-relaxed text-emerald-100/75">{sourceName || sourceUrl} is ready for the repository-ingestion service. This preview records the intended source only; it does not clone, upload, or analyze code yet.</p></div>
        </div>
      )}
      {error && <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-200">{error}</div>}
      {profile && (
        <section className="rounded-2xl border border-indigo-400/25 bg-slate-900 p-6">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-indigo-300">Live repository profile</p>
          <h3 className="mt-1 text-xl font-bold text-white">{profile.repository}</h3>
          <p className="mt-2 text-sm text-slate-400">{profile.description}</p>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <p className="rounded-xl bg-slate-950 p-3 text-xs text-slate-400"><b className="block text-lg text-white">{profile.files_scanned}</b> files inspected</p>
            <p className="rounded-xl bg-slate-950 p-3 text-xs text-slate-400"><b className="block text-lg text-white">{profile.graph_nodes_added}</b> graph nodes added</p>
            <p className="rounded-xl bg-slate-950 p-3 text-xs text-slate-400"><b className="block text-lg text-white">{profile.default_branch}</b> default branch</p>
          </div>
          <div className="mt-5 grid gap-5 md:grid-cols-3 text-xs">
            <div><p className="font-semibold text-slate-200">Languages</p><p className="mt-2 text-slate-400">{profile.languages.join(", ") || "Not detected"}</p></div>
            <div><p className="font-semibold text-slate-200">Manifests</p><p className="mt-2 break-words text-slate-400">{profile.manifests.join(", ") || "None found"}</p></div>
            <div><p className="font-semibold text-slate-200">API / route clues</p><p className="mt-2 break-words text-slate-400">{profile.api_candidates.join(", ") || "None found"}</p></div>
          </div>
          {profile.tree_truncated && <p className="mt-4 text-xs text-amber-300">GitHub returned a large repository tree; this profile uses the first 1,000 files.</p>}
        </section>
      )}
    </div>
  );
}
