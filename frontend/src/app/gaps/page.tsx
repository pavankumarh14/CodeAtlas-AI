"use client";

import React, { useState, useEffect } from "react";
import { 
  ShieldAlert, 
  HelpCircle, 
  BookOpen, 
  Users, 
  FileText, 
  ArrowRight, 
  Loader2,
  CheckCircle2
} from "lucide-react";

export default function KnowledgeGaps() {
  const [loading, setLoading] = useState(true);
  const [gaps, setGaps] = useState<any>({
    risk_score: 45,
    undocumented_services: ["Legacy Shipping Service", "Billing Service"],
    missing_ownership: ["Legacy Shipping Service", "Analytics Collector", "Auditing Service"],
    missing_runbooks: ["Notifications Service", "Legacy Shipping Service", "Shipping Rate Service"],
    stale_documentation: ["Auth Helper Service", "Reviews Service"],
    recommendations: [
      "Assign service owner team to: Legacy Shipping Service and Analytics Collector",
      "Write emergency recovery runbooks for Notifications Service and Legacy Shipping Service",
      "Perform a documentation hackathon to link Confluence pages to remaining active microservices."
    ]
  });

  useEffect(() => {
    async function fetchGaps() {
      setLoading(true);
      try {
        const res = await fetch("/api/v1/knowledge-gaps");
        if (res.ok) {
          const data = await res.json();
          setGaps(data);
        }
      } catch (err) {
        console.warn("Backend offline, running on mock knowledge compliance scan.", err);
      } finally {
        setLoading(false);
      }
    }
    fetchGaps();
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner and Score */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Risk Assessment Card */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col justify-between items-center text-center">
          <div className="w-full flex justify-between items-center border-b border-slate-800 pb-3 mb-4">
            <h3 className="font-bold text-sm text-white">Knowledge Risk Level</h3>
            <ShieldAlert className="h-5 w-5 text-indigo-500" />
          </div>

          <div className="my-4 relative">
            <svg className="w-28 h-28">
              <circle className="text-slate-800" strokeWidth="6" stroke="currentColor" fill="transparent" r="48" cx="56" cy="56" />
              <circle 
                className="text-indigo-500 transition-all duration-1000" 
                strokeWidth="6" 
                strokeDasharray={301}
                strokeDashoffset={301 - (301 * gaps.risk_score) / 100}
                strokeLinecap="round" 
                stroke="currentColor" 
                fill="transparent" 
                r="48" 
                cx="56" 
                cy="56" 
              />
            </svg>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
              <span className="text-2xl font-extrabold text-white">{gaps.risk_score}</span>
              <p className="text-[8px] font-bold text-slate-500 uppercase tracking-widest mt-0.5">Risk Index</p>
            </div>
          </div>

          <p className="text-slate-400 text-xs mt-2 leading-relaxed">
            {gaps.risk_score > 60 
              ? "Critical knowledge gaps detected. High probability of operational delays during outages."
              : gaps.risk_score > 30
                ? "Moderate risk. Missing owners and runbooks on newer microservices require attention."
                : "Excellent code compliance. Graph is fully detailed."}
          </p>
        </div>

        {/* Recommendations list */}
        <div className="lg:col-span-2 p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <h3 className="font-bold text-sm text-white border-b border-slate-800 pb-3 flex items-center gap-2">
            <CheckCircle2 className="h-4.5 w-4.5 text-indigo-400" />
            Compliance Action Recommendations
          </h3>
          {loading ? (
            <div className="flex items-center justify-center py-16 gap-2">
              <Loader2 className="h-5 w-5 text-indigo-500 animate-spin" />
              <span className="text-slate-500 text-xs font-mono">Running compliance scan...</span>
            </div>
          ) : (
            <ul className="space-y-3">
              {gaps.recommendations?.map((rec: string, idx: number) => (
                <li key={idx} className="p-3 bg-slate-950 border border-slate-850 rounded-xl text-xs text-slate-300 flex items-start gap-2.5">
                  <ArrowRight className="h-4 w-4 text-indigo-400 mt-0.5 shrink-0" />
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Main lists grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        
        {/* Undocumented Services */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <h4 className="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-800 pb-2.5">
            <HelpCircle className="h-4 w-4 text-slate-500" />
            Undocumented
          </h4>
          <div className="space-y-2">
            {gaps.undocumented_services?.map((svc: string) => (
              <div key={svc} className="p-2 bg-slate-950 border border-slate-850 rounded-lg text-xs font-semibold text-slate-300">
                {svc}
              </div>
            ))}
          </div>
        </div>

        {/* Missing Owners */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <h4 className="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-800 pb-2.5">
            <Users className="h-4 w-4 text-slate-500" />
            No Owner Team
          </h4>
          <div className="space-y-2">
            {gaps.missing_ownership?.map((svc: string) => (
              <div key={svc} className="p-2 bg-slate-950 border border-slate-850 rounded-lg text-xs font-semibold text-slate-300">
                {svc}
              </div>
            ))}
          </div>
        </div>

        {/* Missing Runbooks */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <h4 className="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-800 pb-2.5">
            <BookOpen className="h-4 w-4 text-slate-500" />
            No Runbooks
          </h4>
          <div className="space-y-2">
            {gaps.missing_runbooks?.map((svc: string) => (
              <div key={svc} className="p-2 bg-slate-950 border border-slate-850 rounded-lg text-xs font-semibold text-slate-300">
                {svc}
              </div>
            ))}
          </div>
        </div>

        {/* Stale Documentation */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <h4 className="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-800 pb-2.5">
            <FileText className="h-4 w-4 text-slate-500" />
            Stale Docs
          </h4>
          <div className="space-y-2">
            {gaps.stale_documentation?.map((svc: string) => (
              <div key={svc} className="p-2 bg-slate-950 border border-slate-850 rounded-lg text-xs font-semibold text-slate-300">
                {svc}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
