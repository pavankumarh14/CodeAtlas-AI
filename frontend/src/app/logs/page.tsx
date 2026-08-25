"use client";

import React, { useState, useEffect } from "react";
import { History, RefreshCw, CheckCircle, AlertOctagon, Cpu, Loader2 } from "lucide-react";

export default function AgentLogs() {
  const [logs, setLogs] = useState<any[]>([
    { id: "1", timestamp: new Date().toISOString(), query: "Add WhatsApp notifications for order updates", flow_type: "pipeline", target_agent: "Orchestrated Pipeline", duration_ms: 2140, status: "Success" },
    { id: "2", timestamp: new Date(Date.now() - 600000).toISOString(), query: "Explain Checkout Service to me.", flow_type: "single_agent", target_agent: "Ontology Mentor Agent", duration_ms: 450, status: "Success" },
    { id: "3", timestamp: new Date(Date.now() - 1200000).toISOString(), query: "Checkout latency increased.", flow_type: "single_agent", target_agent: "Incident Context Agent", duration_ms: 320, status: "Success" },
    { id: "4", timestamp: new Date(Date.now() - 1800000).toISOString(), query: "What happens if Payment Service goes down?", flow_type: "single_agent", target_agent: "Architectural Impact Agent", duration_ms: 280, status: "Success" }
  ]);
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/agent-activity-log");
      if (res.ok) {
        const data = await res.json();
        if (data.length > 0) {
          setLogs(data);
        }
      }
    } catch (err) {
      console.warn("Backend offline, showing session-based logs simulation.", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header and Refresh controls */}
      <div className="flex items-center justify-between p-6 bg-slate-900 border border-slate-800 rounded-2xl">
        <div>
          <h3 className="font-bold text-base text-white">Agent Activity Ledger</h3>
          <p className="text-slate-400 text-xs mt-1">
            Review historical orchestration requests, pipeline paths, latency timings, and exit statuses.
          </p>
        </div>
        <button
          onClick={fetchLogs}
          disabled={loading}
          className="p-2.5 bg-slate-800 hover:bg-slate-750 active:bg-slate-850 rounded-xl border border-slate-700 text-slate-300 hover:text-white transition flex items-center gap-2 text-xs font-semibold cursor-pointer disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          Refresh
        </button>
      </div>

      {/* Ledger Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950 border-b border-slate-800">
                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Time</th>
                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Query</th>
                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Route Type</th>
                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Target Path</th>
                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Latency</th>
                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-850/30 transition-colors">
                  <td className="p-4 text-xs text-slate-500 font-mono">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="p-4 text-xs font-semibold text-slate-200 truncate max-w-[250px]" title={log.query}>
                    {log.query}
                  </td>
                  <td className="p-4 text-xs">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                      log.flow_type === "pipeline" ? "bg-indigo-500/10 text-indigo-400" : "bg-slate-800 text-slate-400"
                    }`}>
                      {log.flow_type}
                    </span>
                  </td>
                  <td className="p-4 text-xs text-slate-300 font-medium">
                    <span className="flex items-center gap-1.5">
                      <Cpu className="h-3.5 w-3.5 text-indigo-400" />
                      {log.target_agent}
                    </span>
                  </td>
                  <td className="p-4 text-xs text-slate-400 font-mono">
                    {log.duration_ms}ms
                  </td>
                  <td className="p-4 text-xs">
                    {log.status.startsWith("Error") ? (
                      <span className="flex items-center gap-1 text-rose-400 font-semibold">
                        <AlertOctagon className="h-3.5 w-3.5 shrink-0" />
                        Failed
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                        <CheckCircle className="h-3.5 w-3.5 shrink-0" />
                        Success
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
