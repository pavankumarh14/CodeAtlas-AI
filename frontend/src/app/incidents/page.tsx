"use client";

import React, { useState, useEffect } from "react";
import { 
  AlertTriangle, 
  Search, 
  HelpCircle, 
  Loader2, 
  Flame, 
  Heart, 
  ShieldAlert, 
  History 
} from "lucide-react";

export default function IncidentRoom() {
  const [activeIncidents, setActiveIncidents] = useState<any[]>([
    { inc_id: "INC-212", title: "INC-212: Payment API Gateway Timeout", severity: "Critical", status: "Active" },
    { inc_id: "INC-213", title: "INC-213: Redis Cache evicted catalog keys", severity: "High", status: "Active" }
  ]);
  const [selectedIncident, setSelectedIncident] = useState("INC-212");
  const [customQuery, setCustomQuery] = useState("Checkout latency spiked above 2000ms");
  const [loading, setLoading] = useState(false);
  const [troubleshootResult, setTroubleshootResult] = useState<any>({
    related_incidents: [
      { id: "INC-101", title: "INC-101: Checkout latency spikes caused by database lockups", relevance: "High Similarity (DB / Network Bottleneck)" },
      { id: "INC-212", title: "INC-212: Stripe Gateway Timeout during checkout flow", relevance: "Direct Incident Match" }
    ],
    dependencies: ["Payment Service", "Inventory Service", "Cart Service"],
    known_fixes: [
      "Switch Stripe Gateway to secondary provider via feature flag (payment-circuit-breaker)",
      "Increase database connections pooling limit in inventory-db configurations",
      "Restart checkout-api pods to clear hung connections thread pool"
    ],
    escalation_path: "Level 1: Commerce On-Call -> Level 2: Platform DB Admin -> Level 3: Principal Architect (Alex)"
  });

  useEffect(() => {
    async function fetchIncidents() {
      try {
        const res = await fetch("/api/v1/incidents");
        if (res.ok) {
          const data = await res.json();
          const active = data.filter((i: any) => i.status === "Active" || i.status === "Triggered");
          if (active.length > 0) {
            setActiveIncidents(active);
            setSelectedIncident(active[0].inc_id);
          }
        }
      } catch (err) {
        console.warn("Backend offline, loading mock incidents.", err);
      }
    }
    fetchIncidents();
  }, []);

  const handleTroubleshoot = async (queryText: string) => {
    setLoading(true);
    setTroubleshootResult(null);
    try {
      const res = await fetch("/api/v1/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText })
      });
      if (res.ok) {
        const data = await res.json();
        setTroubleshootResult(data.results);
      } else {
        alert("Failed to analyze incident query.");
      }
    } catch (err) {
      console.warn("Backend offline, generating mock diagnostic.", err);
      setTimeout(() => {
        setTroubleshootResult({
          related_incidents: [
            { id: "INC-212", title: "INC-212: Stripe Gateway Timeout during checkout flow", relevance: "Exact Match" },
            { id: "INC-101", title: "INC-101: Checkout latency spikes caused by database lockups", relevance: "Related Component (DB Lock)" }
          ],
          dependencies: ["Payment Service", "Billing Service"],
          known_fixes: [
            "Trigger Stripe payment gateway failover script: switch Stripe/Adyen gateway.",
            "Verify network latency alerts in Grafana panels.",
            "Restart checkout-api kubernetes pods."
          ],
          escalation_path: "Level 1: Commerce SRE -> Level 2: Gateway Integration Owner (John Doe) -> Level 3: Infrastructure Lead"
        });
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Active Incidents Selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Left selector column */}
        <div className="md:col-span-1 p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col justify-between h-[300px]">
          <div>
            <h3 className="font-bold text-sm text-white flex items-center gap-2 mb-3">
              <Flame className="h-4.5 w-4.5 text-rose-500 animate-pulse" />
              Active Outages
            </h3>
            <p className="text-slate-400 text-xs mb-4">Select an active incident from the ontology database to run diagnostics.</p>
            
            <div className="space-y-2 overflow-y-auto max-h-[160px] pr-1">
              {activeIncidents.map(inc => (
                <button
                  key={inc.inc_id}
                  onClick={() => {
                    setSelectedIncident(inc.inc_id);
                    setCustomQuery(`Diagnose ${inc.title}`);
                  }}
                  className={`w-full text-left p-3 rounded-lg text-xs font-semibold border transition-all ${
                    selectedIncident === inc.inc_id
                      ? "bg-rose-500/10 border-rose-500/40 text-rose-300"
                      : "bg-slate-950 border-slate-850 text-slate-400 hover:border-slate-800"
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="truncate pr-2">{inc.title.replace(/INC-\d+: /, '')}</span>
                    <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-[9px] text-rose-400 shrink-0 uppercase font-mono">
                      {inc.inc_id}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => handleTroubleshoot(customQuery)}
            disabled={loading}
            className="w-full py-2.5 bg-rose-600 hover:bg-rose-500 active:bg-rose-700 text-white text-xs font-bold uppercase rounded-lg shadow-md shadow-rose-950/50 flex items-center justify-center gap-2 transition disabled:opacity-50 cursor-pointer"
          >
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <AlertTriangle className="h-3.5 w-3.5" />}
            Diagnose Incident
          </button>
        </div>

        {/* Custom troubleshooting text area */}
        <div className="md:col-span-2 p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col justify-between h-[300px]">
          <div>
            <h3 className="font-bold text-sm text-white flex items-center gap-2 mb-3">
              <Search className="h-4.5 w-4.5 text-indigo-400" />
              Custom Diagnostic Analysis
            </h3>
            <p className="text-slate-400 text-xs mb-4">Or type a custom error message or log trail to trace related components.</p>
            
            <textarea
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              disabled={loading}
              className="w-full h-[120px] p-3 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl text-xs text-slate-200 outline-none resize-none transition"
              placeholder="e.g. Database connection pool is full on payment gateway service"
            />
          </div>

          <button
            onClick={() => handleTroubleshoot(customQuery)}
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-bold uppercase rounded-lg shadow-md shadow-indigo-950/50 flex items-center justify-center gap-2 transition disabled:opacity-50 cursor-pointer"
          >
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Search className="h-3.5 w-3.5" />}
            Troubleshoot Query
          </button>
        </div>
      </div>

      {/* Troubleshooting Diagnostic results */}
      {loading && (
        <div className="flex items-center justify-center py-20 gap-3 bg-slate-900/40 border border-slate-800 rounded-2xl">
          <Loader2 className="h-5 w-5 text-indigo-500 animate-spin" />
          <span className="text-slate-400 text-xs font-mono font-medium">Diagnosing upstream graph & runbooks...</span>
        </div>
      )}

      {troubleshootResult && !loading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Related Historical Incidents */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <History className="h-4.5 w-4.5 text-rose-400" />
              Related Historical Incidents
            </h3>
            <div className="space-y-3">
              {troubleshootResult.related_incidents?.map((inc: any, idx: number) => (
                <div key={idx} className="p-4 bg-slate-950 border border-slate-850 rounded-xl">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-semibold text-slate-200">{inc.title}</span>
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[9px] font-mono text-slate-400 font-bold uppercase shrink-0">
                      {inc.id}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-500 mt-2">Relevance: <span className="font-semibold text-rose-400">{inc.relevance}</span></p>
                </div>
              ))}
            </div>
          </div>

          {/* Root cause dependencies & fixes */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4 md:col-span-2">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <ShieldAlert className="h-4.5 w-4.5 text-indigo-400" />
              Diagnosed Root Causes & Runbooks
            </h3>
            
            <div className="space-y-4">
              <div>
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Impacted Upstream Dependencies</span>
                <div className="flex flex-wrap gap-2 mt-1.5">
                  {troubleshootResult.dependencies?.map((dep: string) => (
                    <span key={dep} className="px-2.5 py-1 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold font-mono">
                      {dep}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Recommended Incident Playbooks</span>
                <ul className="space-y-2 mt-2">
                  {troubleshootResult.known_fixes?.map((fix: string, idx: number) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-950 p-3 rounded-lg border border-slate-850">
                      <span className="h-1.5 w-1.5 rounded-full bg-rose-500 mt-2 shrink-0"></span>
                      <span>{fix}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-850 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">On-Call Escalation Matrix</span>
                <p className="text-xs font-semibold font-mono text-emerald-400 mt-1">{troubleshootResult.escalation_path}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
