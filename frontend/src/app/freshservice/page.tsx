"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Wifi, WifiOff, RefreshCw, CheckCircle2, AlertCircle, Loader2, ExternalLink, BrainCircuit, ChevronDown, ChevronUp, XCircle } from "lucide-react";

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
    suspected_cause?: string;
    dependencies?: string[];
    known_fixes?: string[];
    escalation_path?: string;
    routing?: { group: string | null; applied: boolean; summary: string };
  };
  posted_to_freshservice: boolean;
}

export default function FreshserviceIntegrationPage() {
  const [fsStatus, setFsStatus] = useState<FreshserviceStatus | null>(null);
  const [isTestingFs, setIsTestingFs] = useState(false);
  const [fsTestMessage, setFsTestMessage] = useState<string | null>(null);
  const [fsSyncing, setFsSyncing] = useState(false);
  const [fsSyncResult, setFsSyncResult] = useState<string | null>(null);
  const [fsTickets, setFsTickets] = useState<FreshserviceTicket[]>([]);
  const [diagnosingId, setDiagnosingId] = useState<number | null>(null);
  const [diagnosisResults, setDiagnosisResults] = useState<Record<number, DiagnosisResult>>({});
  const [collapsedDiagnosis, setCollapsedDiagnosis] = useState<Set<number>>(new Set());
  const [agentTrace, setAgentTrace] = useState<Record<number, Array<{step: string; status: string; timestamp: string}>>>({});

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

  const handleTestConnection = async () => {
    setIsTestingFs(true);
    setFsTestMessage(null);
    try {
      const res = await fetch("/api/v1/freshworks/status");
      const data = await res.json();
      setFsStatus(data);
      if (data.status === "connected") {
        setFsTestMessage(`✅ Connection verified: Live connection to ${data.domain || "Freshservice"} is active (HTTP 200)`);
      } else {
        setFsTestMessage(`⚠️ Status: ${data.message || data.status}`);
      }
    } catch (e) {
      setFsStatus({ status: "connection_error", message: "Backend unreachable" });
      setFsTestMessage("❌ Error: Could not reach backend server at http://localhost:8000");
    } finally {
      setIsTestingFs(false);
    }
  };

  const syncFreshserviceTickets = async () => {
    setFsSyncing(true);
    setFsSyncResult(null);
    try {
      const res = await fetch("/api/v1/freshworks/sync", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setFsSyncResult(`✅ ${data.message || `Synced ${data.synced} tickets`}`);
        await fetchFreshserviceTickets();
      } else {
        setFsSyncResult("❌ Sync failed. Check API key and try again.");
      }
    } catch (e) {
      setFsSyncResult("❌ Connection error during sync.");
    } finally {
      setFsSyncing(false);
    }
  };

  const diagnoseTicket = async (ticketId: number) => {
    setDiagnosingId(ticketId);
    setAgentTrace((prev) => ({
      ...prev,
      [ticketId]: [
        { step: "Starting diagnosis...", status: "in_progress", timestamp: new Date().toLocaleTimeString() }
      ]
    }));

    try {
      const res = await fetch("/api/v1/freshworks/diagnose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticket_id: ticketId, post_note: true }),
      });
      if (res.ok) {
        const data: DiagnosisResult = await res.json();
        setDiagnosisResults((prev) => ({ ...prev, [ticketId]: data }));
        setAgentTrace((prev) => ({
          ...prev,
          [ticketId]: [
            ...(prev[ticketId] || []),
            { step: "Diagnosis complete", status: "complete", timestamp: new Date().toLocaleTimeString() }
          ]
        }));
      }
    } catch (e) {
      console.error("Diagnosis failed", e);
    } finally {
      setDiagnosingId(null);
    }
  };

  useEffect(() => {
    fetchFreshserviceStatus();
    fetchFreshserviceTickets();
  }, [fetchFreshserviceStatus, fetchFreshserviceTickets]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Freshservice Integration</h2>
          <p className="text-slate-400 text-sm mt-1">Manage live connection to Freshservice tickets and webhooks</p>
        </div>
        <div className="flex items-center gap-2">
          {fsStatus?.status === "connected" ? (
            <div className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-semibold rounded-lg flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
              Connected
            </div>
          ) : (
            <div className="px-3 py-1.5 bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm font-semibold rounded-lg flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-rose-500"></div>
              Disconnected
            </div>
          )}
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Connection Status */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            {fsStatus?.status === "connected" ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            ) : (
              <AlertCircle className="h-5 w-5 text-rose-400" />
            )}
            <h3 className="font-semibold text-white">Connection Status</h3>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-slate-400">
              <span className="text-slate-500">Domain:</span> {fsStatus?.domain || "Not configured"}
            </p>
            <p className="text-sm text-slate-400">
              <span className="text-slate-500">Status:</span> {fsStatus?.status || "Unknown"}
            </p>
            {fsStatus?.http_status && (
              <p className="text-sm text-slate-400">
                <span className="text-slate-500">HTTP Status:</span> {fsStatus.http_status}
              </p>
            )}
          </div>
          <button
            onClick={handleTestConnection}
            disabled={isTestingFs}
            className="w-full mt-4 px-4 py-2.5 rounded-lg bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white font-semibold text-sm flex items-center justify-center gap-2 transition"
          >
            {isTestingFs ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Wifi className="h-4 w-4" />
                Test Connection
              </>
            )}
          </button>
          {fsTestMessage && (
            <p className={`mt-3 text-xs p-2 rounded ${fsTestMessage.includes("✅") ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>
              {fsTestMessage}
            </p>
          )}
        </div>

        {/* Sync Tickets */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            <RefreshCw className="h-5 w-5 text-indigo-400" />
            <h3 className="font-semibold text-white">Sync Tickets to Graph</h3>
          </div>
          <p className="text-sm text-slate-400 mb-4">
            Import all open tickets from Freshservice and match them to services in the knowledge graph.
          </p>
          <button
            onClick={syncFreshserviceTickets}
            disabled={fsSyncing || fsStatus?.status !== "connected"}
            className="w-full px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold text-sm flex items-center justify-center gap-2 transition"
          >
            {fsSyncing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Syncing...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4" />
                Sync Now
              </>
            )}
          </button>
          {fsSyncResult && (
            <p className={`mt-3 text-xs p-2 rounded ${fsSyncResult.includes("✅") ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>
              {fsSyncResult}
            </p>
          )}
        </div>
      </div>

      {/* Synced Tickets */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
        <h3 className="font-semibold text-white mb-4 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5 text-teal-400" />
            Synced Tickets ({fsTickets.length})
          </span>
        </h3>

        {fsTickets.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-400 text-sm">No tickets synced yet.</p>
            <p className="text-slate-500 text-xs mt-1">Click "Sync Now" to import tickets from Freshservice.</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {fsTickets.map((ticket) => {
              const priorityMap: Record<number, { label: string; color: string }> = {
                1: { label: "Low", color: "bg-slate-700 text-slate-300" },
                2: { label: "Medium", color: "bg-blue-700 text-blue-300" },
                3: { label: "High", color: "bg-orange-700 text-orange-300" },
                4: { label: "Critical", color: "bg-rose-700 text-rose-300" },
              };
              const statusMap: Record<number, string> = {
                2: "Open",
                3: "Pending",
                4: "Resolved",
                5: "Closed",
              };
              const priority = priorityMap[ticket.priority] || priorityMap[2];
              const status = statusMap[ticket.status] || "Open";

              const diagnosis = diagnosisResults[ticket.id];

              return (
                <div
                  key={ticket.id}
                  className="p-3 bg-slate-950 border border-slate-800 rounded-lg hover:border-teal-500/30 transition"
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-slate-500">FS-{ticket.id}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${priority.color}`}>
                        {priority.label}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        {status}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <a
                        href={`https://freshworks065.freshservice.com/helpdesk/tickets/${ticket.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 rounded hover:bg-slate-800 text-slate-500 hover:text-teal-400 transition"
                        title="Open in Freshservice"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                      <button
                        type="button"
                        onClick={() => diagnoseTicket(ticket.id)}
                        disabled={diagnosingId === ticket.id}
                        className="p-1.5 rounded hover:bg-indigo-500/15 text-slate-500 hover:text-indigo-400 transition disabled:opacity-50"
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

                  <h4 className="text-sm font-semibold text-slate-200 line-clamp-2 mb-1">
                    {ticket.subject}
                  </h4>
                  <p className="text-xs text-slate-500">
                    {new Date(ticket.created_at).toLocaleDateString()}
                  </p>

                  {/* Agent Trace Panel */}
                  {diagnosingId === ticket.id && agentTrace[ticket.id] && (
                    <div className="mt-3 p-2 bg-slate-900/60 border border-indigo-500/20 rounded space-y-1 animate-fadeIn">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1">
                        <Loader2 className="h-2.5 w-2.5 animate-spin" />
                        Agent Trace
                      </p>
                      <div className="space-y-1 max-h-20 overflow-y-auto">
                        {agentTrace[ticket.id].map((trace, idx) => (
                          <div key={idx} className="text-[10px] text-slate-400 flex items-center gap-1.5">
                            <span>
                              {trace.status === "in_progress" && <Loader2 className="h-2 w-2 animate-spin text-amber-400" />}
                              {trace.status === "complete" && <CheckCircle2 className="h-2 w-2 text-emerald-400" />}
                              {trace.status === "error" && <XCircle className="h-2 w-2 text-rose-400" />}
                            </span>
                            <span className="text-slate-300">{trace.step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Diagnosis Result */}
                  {diagnosis && (
                    <div className="mt-3 pt-3 border-t border-slate-800 space-y-1.5 animate-fadeIn">
                      <button
                        type="button"
                        onClick={() => {
                          const newCollapsed = new Set(collapsedDiagnosis);
                          if (newCollapsed.has(ticket.id)) {
                            newCollapsed.delete(ticket.id);
                          } else {
                            newCollapsed.add(ticket.id);
                          }
                          setCollapsedDiagnosis(newCollapsed);
                        }}
                        className="w-full text-left text-[10px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1 hover:text-indigo-200 transition cursor-pointer"
                      >
                        {collapsedDiagnosis.has(ticket.id) ? (
                          <ChevronUp className="h-3 w-3" />
                        ) : (
                          <ChevronDown className="h-3 w-3" />
                        )}
                        <BrainCircuit className="h-3 w-3" /> AI Diagnosis
                      </button>

                      {!collapsedDiagnosis.has(ticket.id) && (
                        <div className="space-y-1.5 pt-1">
                          <p className="text-xs text-slate-300">
                            <span className="text-slate-500">Cause:</span> {diagnosis.diagnosis.suspected_cause || "Unknown"}
                          </p>
                          {diagnosis.diagnosis.dependencies && diagnosis.diagnosis.dependencies.length > 0 && (
                            <p className="text-xs text-slate-300">
                              <span className="text-slate-500">Impacted:</span> {diagnosis.diagnosis.dependencies.join(", ")}
                            </p>
                          )}
                          {diagnosis.diagnosis.known_fixes && diagnosis.diagnosis.known_fixes.length > 0 && (
                            <p className="text-xs text-slate-300">
                              <span className="text-slate-500">Fix:</span> {diagnosis.diagnosis.known_fixes[0]}
                            </p>
                          )}
                          <p className="text-xs text-slate-300">
                            <span className="text-slate-500">Escalation:</span> {diagnosis.diagnosis.escalation_path || "On-Call"}
                          </p>
                          {diagnosis.diagnosis.routing && (
                            <p className={`text-xs ${diagnosis.diagnosis.routing.applied ? "text-sky-300" : "text-slate-300"}`}>
                              <span className="text-slate-500">Routing:</span> {diagnosis.diagnosis.routing.summary}
                            </p>
                          )}
                          {diagnosis.posted_to_freshservice && (
                            <p className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1">
                              <CheckCircle2 className="h-3 w-3" /> Note posted to Freshservice
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
