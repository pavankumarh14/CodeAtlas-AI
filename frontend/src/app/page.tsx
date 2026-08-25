"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { 
  ShieldAlert, 
  Server, 
  GitBranch, 
  Users, 
  FileText, 
  AlertOctagon, 
  ArrowRight,
  TrendingDown,
  Activity,
  Heart
} from "lucide-react";

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

export default function HomeDashboard() {
  const [stats, setStats] = useState<Stats>({
    services: 20,
    repositories: 20,
    teams: 5,
    engineers: 25,
    requirements: 50,
    active_incidents: 2,
    system_health_score: 85
  });
  
  const [incidents, setIncidents] = useState<Incident[]>([
    { inc_id: "INC-212", title: "INC-212: Payment API Gateway Timeout", severity: "Critical", status: "Active", root_cause: "Stripe API timeouts" },
    { inc_id: "INC-213", title: "INC-213: Redis Cache evicted catalog keys", severity: "High", status: "Active", root_cause: "Cache TTL configuration" }
  ]);
  
  const [requirements, setRequirements] = useState<Requirement[]>([
    { req_id: "REQ-101", title: "Feature Requirement REQ-101: Add WhatsApp notifications for order updates", priority: "High", status: "In Progress" },
    { req_id: "REQ-102", title: "Feature Requirement REQ-102: Migrate payment tokens to ISO format", priority: "Critical", status: "Proposed" },
    { req_id: "REQ-103", title: "Feature Requirement REQ-103: Optimize database indices for search indexing", priority: "Medium", status: "Implemented" }
  ]);

  const [loading, setLoading] = useState(true);

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
      } catch (e) {
        console.warn("Backend server not reachable. Running on mock display data.", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

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
        <div className="flex items-center gap-4 shrink-0">
          <Link
            href="/analyzer"
            className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition shadow-md shadow-indigo-900/40 flex items-center gap-2 group"
          >
            Analyze Requirement
            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </Link>
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
