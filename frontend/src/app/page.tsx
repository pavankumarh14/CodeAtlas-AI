"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { 
  Server, 
  GitBranch, 
  Users, 
  FileText, 
  AlertOctagon, 
  ArrowRight,
  Activity,
  Database,
  Trash2,
  RefreshCw,
  Wifi,
  WifiOff,
  ExternalLink,
  BrainCircuit,
  Loader2,
  CheckCircle2,
  XCircle
} from "lucide-react";

const demoUseCases = [
  {
    title: "Requirement → execution plan",
    description: "Turn a proposed feature into affected services, owners, risks, tests, and an explainable plan.",
    query: "Add WhatsApp notifications for order updates",
    href: "/analyzer",
    capability: "Knowledge-to-Action",
  },
  {
    title: "Incident → root-cause context",
    description: "Trace an outage to services, prior incidents, runbooks, and the right responders.",
    query: "Investigate INC-212 Payment API Gateway Timeout",
    href: "/incidents",
    capability: "Knowledge Graph Reasoning",
  },
  {
    title: "Service → the right expert",
    description: "Find owners, architects, and subject-matter experts before making a change.",
    query: "Who owns Checkout Service?",
    href: "/experts",
    capability: "Reusable Agent Skills",
  },
];

interface Stats {
  services: number;
  repositories: number;
  teams: number;
  engineers: number;
  requirements: number;
  active_incidents: number;
  system_health_score: number;
}

interface Incident {
  inc_id: string;
  title: string;
  severity: string;
  status: string;
  root_cause?: string;
}

interface Requirement {
  req_id: string;
  title: string;
  priority: string;
  status: string;
}

interface FreshserviceStatus {
  status: string;
  domain?: string;
  message?: string;
  http_status?: number;
}

interface FreshserviceTicket {
  id: number;
  subject: string;
  priority: number;
  status: number;
  created_at: string;
  description_text?: string;
}

interface DiagnosisResult {
  ticket_id: number;
  subject: string;
  diagnosis: {
    root_cause?: string;
    dependencies?: string[];
    escalation_path?: string;
  };
  posted_to_freshservice: boolean;
}

export default function HomeDashboard() {
  const [stats, setStats] = useState<Stats>({
    services: 0,
    repositories: 0,
    teams: 0,
    engineers: 0,
    requirements: 0,
    active_incidents: 0,
    system_health_score: 100
  });
  
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [requirements, setRequirements] = useState<Requirement[]>([]);

  const [, setLoading] = useState(true);

  // Freshservice state
  const [fsStatus, setFsStatus] = useState<FreshserviceStatus | null>(null);
  const [fsTickets, setFsTickets] = useState<FreshserviceTicket[]>([]);
  const [fsSyncing, setFsSyncing] = useState(false);
  const [fsSyncResult, setFsSyncResult] = useState<string | null>(null);
  const [isTestingFs, setIsTestingFs] = useState(false);
  const [fsTestMessage, setFsTestMessage] = useState<string | null>(null);
  const [diagnosingId, setDiagnosingId] = useState<number | null>(null);
  const [diagnosisResults, setDiagnosisResults] = useState<Record<number, DiagnosisResult>>({});

  const fetchFreshserviceStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/freshworks/status");
      if (res.ok) {
        const data = await res.json();
        setFsStatus(data);
        return data;
      }
    } catch (e) {
      setFsStatus({ status: "connection_error", message: "Backend unreachable" });
    }
    return null;
  }, []);

  const handleTestConnection = async () => {
    setIsTestingFs(true);
    setFsTestMessage(null);
    try {
      const res = await fetch("/api/v1/freshworks/status");
      const data = await res.json();
      setFsStatus(data);
      if (data.status === "connected") {
        setFsTestMessage(`Connection verified: Live connection to ${data.domain || "Freshservice"} is active (HTTP 200)`);
        await fetchFreshserviceTickets();
      } else {
        setFsTestMessage(data.message || `Status: ${data.status}`);
      }
    } catch (e) {
      setFsStatus({ status: "connection_error", message: "Backend unreachable" });
      setFsTestMessage("Error: Could not reach backend server at http://localhost:8000");
    } finally {
      setIsTestingFs(false);
    }
  };

  const fetchFreshserviceTickets = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/freshworks/tickets");
      if (res.ok) {
        const data = await res.json();
        setFsTickets(data);
      }
    } catch (e) {
      console.warn("Could not fetch Freshservice tickets", e);
    }
  }, []);

  const syncFreshserviceTickets = async () => {
    setFsSyncing(true);
    setFsSyncResult(null);
    try {
      const res = await fetch("/api/v1/freshworks/sync", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setFsSyncResult(data.message || `Synced ${data.synced} tickets`);
        // Refresh dashboard stats and incidents after sync
        const statsRes = await fetch("/api/v1/stats");
        if (statsRes.ok) setStats(await statsRes.json());
        const incRes = await fetch("/api/v1/incidents");
        if (incRes.ok) {
          const incData = await incRes.json();
          setIncidents(incData.filter((i: any) => i.status === "Active" || i.status === "Triggered").slice(0, 5));
        }
        await fetchFreshserviceTickets();
      } else {
        setFsSyncResult("Sync failed. Check API key and try again.");
      }
    } catch (e) {
      setFsSyncResult("Connection error during sync.");
    } finally {
      setFsSyncing(false);
    }
  };

  const diagnoseTicket = async (ticketId: number) => {
    setDiagnosingId(ticketId);
    try {
      const res = await fetch("/api/v1/freshworks/diagnose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticket_id: ticketId, post_note: true }),
      });
      if (res.ok) {
        const data: DiagnosisResult = await res.json();
        setDiagnosisResults((prev) => ({ ...prev, [ticketId]: data }));
      }
    } catch (e) {
      console.error("Diagnosis failed", e);
    } finally {
      setDiagnosingId(null);
    }
  };

  useEffect(() => {
    async function fetchData() {
      try {
        const statsRes = await fetch("/api/v1/stats");
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
        
        const incRes = await fetch("/api/v1/incidents");
        if (incRes.ok) {
          const incData = await incRes.json();
          setIncidents(incData.filter((i: any) => i.status === "Active" || i.status === "Triggered").slice(0, 5));
        }

        const reqRes = await fetch("/api/v1/requirements");
        if (reqRes.ok) {
          const reqData = await reqRes.json();
          setRequirements(reqData.slice(0, 5));
        }

        // Fetch Freshservice status & tickets
        await fetchFreshserviceStatus();
        await fetchFreshserviceTickets();
      } catch (e) {
        console.warn("Backend server not reachable. Running on mock display data.", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [fetchFreshserviceStatus, fetchFreshserviceTickets]);

  const statCards = [
    { name: "Services", value: stats.services, icon: Server, color: "text-blue-500", bg: "bg-blue-500/10" },
    { name: "Repositories", value: stats.repositories, icon: GitBranch, color: "text-purple-500", bg: "bg-purple-500/10" },
    { name: "Teams", value: stats.teams, icon: Users, color: "text-yellow-500", bg: "bg-yellow-500/10" },
    { name: "Engineers", value: stats.engineers, icon: Users, color: "text-emerald-500", bg: "bg-emerald-500/10" },
    { name: "Requirements", value: stats.requirements, icon: FileText, color: "text-pink-500", bg: "bg-pink-500/10" },
    { name: "Active Incidents", value: stats.active_incidents, icon: AlertOctagon, color: "text-rose-500", bg: "bg-rose-500/10" }
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Welcome to CodeAtlas AI</h2>
          <p className="text-slate-400 text-sm max-w-xl">
            Your engineering brain: AI recommendations grounded in the knowledge graph, code, requirements, docs, owners, and architecture context.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={async () => {
              if (confirm("Wipe all data from the database to start completely fresh?")) {
                const res = await fetch("/api/v1/database/clear", { method: "POST" });
                if (res.ok) {
                  alert("Database wiped clean! (0 nodes in Neo4j)");
                  window.location.reload();
                } else {
                  alert("Failed to clear database.");
                }
              }
            }}
            className="px-4 py-2.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/50 text-rose-300 font-semibold text-xs tracking-wider uppercase transition flex items-center gap-2 cursor-pointer"
          >
            Clear Database
            <Trash2 className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            onClick={async () => {
              if (confirm("Populate database with the CodeAtlas demo dataset?")) {
                const res = await fetch("/api/v1/seed", { method: "POST" });
                if (res.ok) {
                  alert("Demo data loaded successfully!");
                  window.location.reload();
                } else {
                  alert("Failed to seed database.");
                }
              }
            }}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-semibold text-xs tracking-wider uppercase transition flex items-center gap-2 cursor-pointer"
          >
            Load Demo Data
            <Database className="h-3.5 w-3.5" />
          </button>
          <Link
            href="/analyzer"
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs tracking-wider uppercase transition shadow-md shadow-indigo-900/40 flex items-center gap-2 group"
          >
            Analyze Requirement
            <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link href="/repositories" className="px-4 py-2.5 rounded-xl border border-slate-700 hover:border-indigo-400 text-slate-200 hover:text-white font-semibold text-xs tracking-wider uppercase transition flex items-center gap-2">
            Add Repository
            <GitBranch className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>



      <div className="rounded-2xl border border-indigo-500/25 bg-indigo-950/20 p-6">
        <div className="mb-5 flex flex-col justify-between gap-3 md:flex-row md:items-end">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-indigo-300">Start a guided demo</p>
            <h3 className="mt-1 text-lg font-bold text-white">Choose a real engineering question</h3>
            <p className="mt-1 text-sm text-slate-400">Open a use case, run its sample question, then review the recommendation and Explainability Panel.</p>
          </div>
          <div className="flex flex-wrap gap-2 text-[10px] font-semibold uppercase tracking-wider">
            {["Reusable Agent Skills", "Agent Handoffs", "Knowledge-to-Action", "MCP Integrations", "Knowledge Graph Reasoning"].map((item) => (
              <span key={item} className="rounded-full border border-indigo-400/25 bg-indigo-400/10 px-2.5 py-1 text-indigo-200">✓ {item}</span>
            ))}
          </div>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {demoUseCases.map((useCase) => (
            <Link key={useCase.title} href={useCase.href} className="group rounded-xl border border-slate-800 bg-slate-950/65 p-4 transition hover:border-indigo-400/50 hover:bg-slate-900">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-indigo-300">{useCase.capability}</p>
              <h4 className="mt-2 text-sm font-bold text-white">{useCase.title}</h4>
              <p className="mt-2 min-h-10 text-xs leading-relaxed text-slate-400">{useCase.description}</p>
              <p className="mt-3 rounded-md bg-slate-900 px-2 py-1.5 font-mono text-[10px] text-slate-300">Try: “{useCase.query}”</p>
              <p className="mt-3 flex items-center gap-1 text-xs font-semibold text-indigo-300">Open use case <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" /></p>
            </Link>
          ))}
        </div>
      </div>

      {/* Grid Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-6">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.name} className="p-6 bg-slate-900 border border-slate-800 rounded-2xl hover:border-slate-700/80 transition-all group">
              <div className={`p-3 w-fit rounded-xl ${card.bg} ${card.color} mb-4 group-hover:scale-105 transition-transform`}>
                <Icon className="h-6 w-6" />
              </div>
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase">{card.name}</p>
              <h3 className="text-2xl font-bold text-white mt-1">{card.value}</h3>
            </div>
          );
        })}
      </div>

      {/* Freshservice Integration Panel */}
      <div className="rounded-2xl border border-teal-500/25 bg-gradient-to-br from-teal-950/20 via-slate-900 to-slate-900 p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-teal-500/10">
              <Wifi className="h-5 w-5 text-teal-400" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                Freshservice Integration
                {fsStatus?.status === "connected" && (
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Connected
                  </span>
                )}
                {fsStatus?.status === "unconfigured" && (
                  <span className="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                    <WifiOff className="h-3 w-3" />
                    API Key Missing
                  </span>
                )}
                {fsStatus?.status === "unauthorized" && (
                  <span className="px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                    <XCircle className="h-3 w-3" />
                    Unauthorized
                  </span>
                )}
                {fsStatus?.status === "connection_error" && (
                  <span className="px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                    <XCircle className="h-3 w-3" />
                    Unreachable
                  </span>
                )}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {fsStatus?.domain ? (
                  <a href={`https://${fsStatus.domain}`} target="_blank" rel="noopener noreferrer" className="hover:text-teal-400 transition flex items-center gap-1">
                    {fsStatus.domain} <ExternalLink className="h-3 w-3" />
                  </a>
                ) : "Freshworks065 Tenant"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleTestConnection}
              disabled={isTestingFs}
              className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-60 border border-slate-700 text-slate-300 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer"
            >
              {isTestingFs ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin text-teal-400" />
              ) : (
                <RefreshCw className="h-3.5 w-3.5" />
              )}
              {isTestingFs ? "Testing..." : "Test Connection"}
            </button>
            <button
              type="button"
              onClick={syncFreshserviceTickets}
              disabled={Boolean(fsSyncing || fsStatus?.status !== "connected")}
              className="px-3 py-2 rounded-lg bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer"
            >
              {fsSyncing ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Database className="h-3.5 w-3.5" />
              )}
              {fsSyncing ? "Syncing..." : "Sync Tickets to Graph"}
            </button>
          </div>
        </div>

        {/* Test Connection Banner */}
        {fsTestMessage && (
          <div className={`mb-4 px-4 py-2.5 rounded-lg text-xs font-medium flex items-center justify-between gap-2 ${
            fsTestMessage.includes("verified") || fsTestMessage.includes("active")
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
              : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
          }`}>
            <div className="flex items-center gap-2">
              {fsTestMessage.includes("verified") || fsTestMessage.includes("active") ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
              ) : (
                <XCircle className="h-4 w-4 shrink-0 text-rose-400" />
              )}
              <span>{fsTestMessage}</span>
            </div>
            <button
              onClick={() => setFsTestMessage(null)}
              className="text-slate-400 hover:text-slate-200 text-xs px-1 cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        {/* Sync Result Banner */}
        {fsSyncResult && (
          <div className={`mb-4 px-4 py-2.5 rounded-lg text-xs font-medium flex items-center gap-2 ${
            fsSyncResult.includes("Successfully") || fsSyncResult.includes("Synced")
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
              : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
          }`}>
            {fsSyncResult.includes("Successfully") || fsSyncResult.includes("Synced") ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : (
              <XCircle className="h-4 w-4" />
            )}
            {fsSyncResult}
          </div>
        )}

        {/* Unconfigured State */}
        {fsStatus?.status === "unconfigured" && (
          <div className="py-8 text-center border border-dashed border-slate-700 rounded-xl">
            <WifiOff className="h-8 w-8 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-400 font-medium">Freshservice API key not configured</p>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Add your API key to <code className="px-1.5 py-0.5 rounded bg-slate-800 text-teal-300 text-[11px]">.env</code> → <code className="px-1.5 py-0.5 rounded bg-slate-800 text-teal-300 text-[11px]">FRESHSERVICE_API_KEY=your-key</code> then restart the backend.
            </p>
          </div>
        )}

        {/* Live Tickets Grid */}
        {fsStatus?.status === "connected" && (
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {fsTickets.length === 0 ? (
              <div className="col-span-full py-8 text-center text-slate-500 text-sm">
                No tickets loaded yet. Click <strong className="text-teal-400">Sync Tickets to Graph</strong> to import live data.
              </div>
            ) : (
              fsTickets.slice(0, 9).map((ticket) => {
                const priorityMap: Record<number, { label: string; color: string }> = {
                  1: { label: "Low", color: "text-slate-400 bg-slate-800" },
                  2: { label: "Medium", color: "text-blue-400 bg-blue-500/10" },
                  3: { label: "High", color: "text-orange-400 bg-orange-500/10" },
                  4: { label: "Critical", color: "text-rose-400 bg-rose-500/10" },
                };
                const statusMap: Record<number, string> = { 2: "Open", 3: "Pending", 4: "Resolved", 5: "Closed" };
                const priority = priorityMap[ticket.priority] || priorityMap[2];
                const statusLabel = statusMap[ticket.status] || "Open";
                const diagnosis = diagnosisResults[ticket.id];

                return (
                  <div key={ticket.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl hover:border-teal-500/30 transition group">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-[10px] font-mono text-slate-500">FS-{ticket.id}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${priority.color}`}>
                        {priority.label}
                      </span>
                    </div>
                    <h4 className="text-sm font-semibold text-slate-200 line-clamp-2 mb-2">{ticket.subject}</h4>
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        statusLabel === "Resolved" || statusLabel === "Closed"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : statusLabel === "Pending"
                          ? "bg-amber-500/10 text-amber-400"
                          : "bg-blue-500/10 text-blue-400"
                      }`}>
                        {statusLabel}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <a
                          href={`https://freshworks065.freshservice.com/helpdesk/tickets/${ticket.id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded-md hover:bg-slate-800 text-slate-500 hover:text-teal-400 transition"
                          title="Open in Freshservice"
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                        <button
                          type="button"
                          onClick={() => diagnoseTicket(ticket.id)}
                          disabled={diagnosingId === ticket.id}
                          className="p-1.5 rounded-md hover:bg-indigo-500/15 text-slate-500 hover:text-indigo-400 transition disabled:opacity-50 cursor-pointer"
                          title="AI Diagnose"
                        >
                          {diagnosingId === ticket.id ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <BrainCircuit className="h-3.5 w-3.5" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Inline Diagnosis Result */}
                    {diagnosis && (
                      <div className="mt-3 pt-3 border-t border-slate-800 space-y-1.5 animate-fadeIn">
                        <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1">
                          <BrainCircuit className="h-3 w-3" /> AI Diagnosis
                        </p>
                        <p className="text-xs text-slate-300">
                          <span className="text-slate-500">Cause:</span> {diagnosis.diagnosis.root_cause || "Unknown"}
                        </p>
                        {diagnosis.diagnosis.dependencies && diagnosis.diagnosis.dependencies.length > 0 && (
                          <p className="text-xs text-slate-300">
                            <span className="text-slate-500">Impacted:</span> {diagnosis.diagnosis.dependencies.join(", ")}
                          </p>
                        )}
                        <p className="text-xs text-slate-300">
                          <span className="text-slate-500">Escalation:</span> {diagnosis.diagnosis.escalation_path || "On-Call"}
                        </p>
                        {diagnosis.posted_to_freshservice && (
                          <p className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1">
                            <CheckCircle2 className="h-3 w-3" /> Note posted to Freshservice
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>

      {/* Main Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* System Health Status */}
        <div className="lg:col-span-1 p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-base text-white">System Architecture Health</h3>
              <Activity className="h-5 w-5 text-indigo-500" />
            </div>
            
            {/* Circle progress bar */}
            <div className="flex justify-center my-6 relative">
              <svg className="w-36 h-36">
                <circle 
                  className="text-slate-800" 
                  strokeWidth="8" 
                  stroke="currentColor" 
                  fill="transparent" 
                  r="64" 
                  cx="72" 
                  cy="72" 
                />
                <circle 
                  className="text-indigo-500 transition-all duration-1000" 
                  strokeWidth="8" 
                  strokeDasharray={402}
                  strokeDashoffset={402 - (402 * stats.system_health_score) / 100}
                  strokeLinecap="round" 
                  stroke="currentColor" 
                  fill="transparent" 
                  r="64" 
                  cx="72" 
                  cy="72" 
                />
              </svg>
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                <span className="text-3xl font-extrabold text-white">{stats.system_health_score}%</span>
                <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mt-0.5">Coverage</p>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-4 mt-6">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium">Compliance Gaps</span>
              <Link href="/gaps" className="text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1">
                View Report <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </div>

        {/* Active Incidents */}
        <div className="lg:col-span-1 p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              Active Outages
              {incidents.length > 0 && (
                <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 text-[10px] font-bold uppercase tracking-wider">
                  Active
                </span>
              )}
            </h3>
            <AlertOctagon className="h-5 w-5 text-rose-500" />
          </div>

          <div className="space-y-4">
            {incidents.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-sm">
                No active incidents reported. All systems functional.
              </div>
            ) : (
              incidents.map((inc) => (
                <div key={inc.inc_id} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-start gap-3">
                  <span className={`h-2 w-2 rounded-full mt-1.5 shrink-0 ${inc.severity === "Critical" ? "bg-rose-500 animate-pulse" : "bg-orange-500"}`}></span>
                  <div className="min-w-0">
                    <h4 className="text-sm font-semibold text-slate-200 truncate">{inc.title}</h4>
                    <p className="text-xs text-slate-400 mt-1">Severity: <span className="font-semibold text-rose-400">{inc.severity}</span></p>
                    {inc.root_cause && <p className="text-xs text-slate-500 mt-0.5 truncate">Root Cause: {inc.root_cause}</p>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Requirements */}
        <div className="lg:col-span-1 p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-base text-white">Recent Requirements</h3>
            <FileText className="h-5 w-5 text-pink-500" />
          </div>

          <div className="space-y-4">
            {requirements.slice(0, 4).map((req) => (
              <div key={req.req_id} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <h4 className="text-sm font-semibold text-slate-200 truncate">{req.title.replace(/Feature Requirement REQ-\d+: /, '')}</h4>
                  <span className="text-[10px] font-mono text-slate-500">{req.req_id}</span>
                </div>
                <div className="shrink-0 text-right">
                  <span className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-semibold ${
                    req.status === "Implemented" ? "bg-emerald-500/10 text-emerald-400" :
                    req.status === "In Progress" ? "bg-indigo-500/10 text-indigo-400" : "bg-slate-800 text-slate-400"
                  }`}>
                    {req.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
