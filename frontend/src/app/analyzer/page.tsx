"use client";

import React, { useState } from "react";
import { 
  Play, 
  Terminal, 
  Layers, 
  FileText, 
  Users, 
  ShieldAlert, 
  CheckSquare, 
  Loader2,
  BrainCircuit,
  Settings,
  CornerDownRight,
  Eye,
  GitMerge,
  FileCode,
  Gauge
} from "lucide-react";

export default function RequirementAnalyzer() {
  const [query, setQuery] = useState("Add WhatsApp notifications for order updates");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [activeStep, setActiveStep] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);

    let step = 0;
    const interval = setInterval(() => {
      setActiveStep(s => s + 1);
    }, 1200);

    try {
      const res = await fetch("http://localhost:8000/api/v1/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else {
        alert("Failed to analyze. Please ensure the backend server is running.");
      }
    } catch (err) {
      console.warn("Backend not active, using fallback simulation with Explainability Panel", err);
      setTimeout(() => {
        setResult({
          flow_type: "pipeline",
          target_agent: "Orchestrated Pipeline",
          duration_seconds: 2.14,
          execution_trace: [
            "[Orchestrator] Received user query: 'Add WhatsApp notifications for order updates'",
            "[Orchestrator] Evaluated query routing. Path chosen: REQUIREMENT_PIPELINE",
            "[Orchestrator] Step 1/3: Dispatching to Requirement Impact Agent...",
            "  [Requirement Impact Agent] Initializing Requirement Impact Agent...",
            "  [Requirement Impact Agent] Searching semantic vector store for matching services and files...",
            "  [Requirement Impact Agent] Traversing knowledge graph to find related dependencies and teams...",
            "  [Requirement Impact Agent] Triggering pluggable GitHub and Jira MCP Adapters...",
            "  [Requirement Impact Agent] Synthesizing impact assessment report...",
            "[Orchestrator] Step 2/3: Handing off to Ontology Mentor Agent for: Notifications Service...",
            "  [Ontology Mentor Agent] Querying graph database for neighbors, owners, and dependencies...",
            "  [Ontology Mentor Agent] Generating response using Dynamic Reasoning Engine...",
            "[Orchestrator] Step 3/3: Handing off to Expert Discovery Agent for service experts...",
            "  [Expert Discovery Agent] Retrieving database ownership path: Service -> Team -> MEMBERS -> Engineer",
            "[Orchestrator] Synthesizing collaborative reports into Implementation Plan...",
            "[Orchestrator] Pipeline completed in 2.14s."
          ],
          explainability: {
            why_chosen: "Synthesized orchestrated pipeline for requirement 'Add WhatsApp notifications for order updates'. Mobilized the Requirement Impact Agent to map dependencies, the Ontology Mentor to profile Notifications Service, and the Expert Finder to identify reviewers.",
            nodes_traversed: [
              "Service:Notifications Service",
              "Service:Order Service",
              "Repository:notifications-hub",
              "Repository:order-processor",
              "Team:Notifications Team",
              "Engineer:Emma Jones",
              "API:POST /api/v1/notifications/send"
            ],
            documents_consulted: [
              "Jira Adapter: REQ-65 WhatsApp Specs",
              "GitHub Adapter: notifications-hub repo logs",
              "Confluence Space: Notifications Setup Docs"
            ],
            similar_requirements: [
              "REQ-65: Implement WhatsApp Notifications for Order Status"
            ],
            confidence_score: 94,
            contributing_agents: [
              "Requirement Impact Agent",
              "Ontology Mentor Agent",
              "Expert Discovery Agent"
            ]
          },
          results: {
            requirement: query,
            impact_analysis: {
              services: ["Notifications Service", "Order Service"],
              repositories: ["notifications-hub", "order-processor"],
              apis: ["POST /api/v1/notifications/send"],
              risk: "Medium Risk. Connecting to external Twilio/WhatsApp APIs. Network timeouts could cascade if order processing threads are held synchronously."
            },
            service_details: {
              purpose: "Triggers transaction emails, transactional SMS, and messaging updates.",
              business_capability: "Notifications Management",
              dependencies: ["Auth Service"]
            },
            key_contacts: {
              owners: ["Emma Jones (Engineer) - emma.jones@company.com", "Notifications Team (Team)"],
              architects: ["Alex Architect (Chief Architect)"],
              subject_matter_experts: ["Emma Jones"]
            },
            generated_plan: {
              implementation: [
                "1. Extend schemas in 'notifications-hub' to support WhatsApp payload schemas.",
                "2. Implement WhatsApp dispatch client using external gateway webhooks.",
                "3. Set up an asynchronous queue worker (e.g. Celery / BullMQ) to publish notifications.",
                "4. Trigger notifications event publish from order-processor during order updates."
              ],
              testing: [
                "1. Mock external WhatsApp API sandbox responses to test gateway success/failure.",
                "2. Write unit tests for the message publisher client in order-processor.",
                "3. Run end-to-end integration tests using docker-compose profiles."
              ],
              reviewers: ["Emma Jones (Notifications Team)", "Alex Architect (Platform Architect)"]
            }
          }
        });
      }, 2000);
    } finally {
      clearInterval(interval);
      setLoading(false);
      setActiveStep(0);
    }
  };

  const loadingSteps = [
    "Evaluating query intent...",
    "Retrieving active engineering schema nodes...",
    "Querying Jira & GitHub MCP repositories...",
    "Running multi-agent collaborative handoffs...",
    "Drafting final implementation plan..."
  ];

  // Helper to color node categories in explainability
  const getNodeColorClass = (node: string) => {
    const parts = node.split(":");
    const type = parts[0];
    switch (type) {
      case "Service": return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      case "Team": return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
      case "Engineer": return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "Repository": return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "API": return "bg-teal-500/10 text-teal-400 border-teal-500/30";
      case "Incident": return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      case "Requirement": return "bg-pink-500/10 text-pink-400 border-pink-500/30";
      default: return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Search Header */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
        <h3 className="font-bold text-base text-white mb-2">Analyze Proposed Engineering Requirement</h3>
        <p className="text-slate-400 text-xs mb-6">
          Input a new product feature description below. The orchestrator will mobilize specialized agents (Impact, Ontology, Experts) to formulate an execution plan.
        </p>
        
        <form onSubmit={handleSubmit} className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            className="flex-1 px-4 py-3 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl text-sm text-slate-200 outline-none transition disabled:opacity-50"
            placeholder="Type your feature requirement (e.g., Migrate Auth keys to new secret manager)"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white rounded-xl text-sm font-semibold flex items-center gap-2 transition disabled:opacity-50 shadow-md shadow-indigo-950/50 cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-white" />
                Run Agents
              </>
            )}
          </button>
        </form>
      </div>

      {/* Loading Animation State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-16 bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl gap-4">
          <BrainCircuit className="h-10 w-10 text-indigo-500 animate-spin" />
          <div className="text-center">
            <h4 className="text-sm font-semibold text-slate-200">Mobilizing Specialized Agents</h4>
            <p className="text-xs text-slate-500 mt-1 font-mono">{loadingSteps[Math.min(activeStep, loadingSteps.length - 1)]}</p>
          </div>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          
          {/* Execution Trace & Agent Handoff Logs */}
          <div className="xl:col-span-1 p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col h-[750px]">
            <h3 className="font-bold text-sm text-white mb-4 flex items-center gap-2 border-b border-slate-800 pb-3">
              <Terminal className="h-4 w-4 text-indigo-400" />
              Agent Collaborative Trace
            </h3>
            
            <div className="flex-1 overflow-y-auto font-mono text-[10px] text-slate-400 space-y-2 bg-slate-950 p-4 rounded-xl border border-slate-850">
              {result.execution_trace.map((log: string, idx: number) => {
                const isOrch = log.startsWith("[Orchestrator]");
                const style = isOrch 
                  ? "text-indigo-400 font-semibold" 
                  : log.includes("Error") 
                    ? "text-rose-400" 
                    : "text-slate-400 pl-4";
                return (
                  <div key={idx} className={`${style} flex items-start gap-1`}>
                    {!isOrch && <CornerDownRight className="h-3 w-3 mt-0.5 text-slate-600 shrink-0" />}
                    <span>{log}</span>
                  </div>
                );
              })}
            </div>
            
            <div className="mt-4 text-[10px] text-slate-500 font-mono flex justify-between items-center bg-slate-950/40 p-2 rounded-lg border border-slate-850/50">
              <span>Path: {result.target_agent}</span>
              <span>Latency: {result.duration_seconds || 0}s</span>
            </div>
          </div>

          {/* Structured Output Details */}
          <div className="xl:col-span-2 space-y-8 h-[750px] overflow-y-auto pr-2">
            {/* Impact Assessment Card */}
            <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
              <h3 className="font-bold text-base text-white flex items-center gap-2 border-b border-slate-800 pb-3">
                <Layers className="h-5 w-5 text-indigo-400" />
                Blast Radius & Ontology Impact
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Affected Services</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.results.impact_analysis.services?.map((svc: string) => (
                      <span key={svc} className="px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-medium">
                        {svc}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Target Repositories</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.results.impact_analysis.repositories?.map((repo: string) => (
                      <span key={repo} className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-medium font-mono">
                        {repo}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Involved APIs</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.results.impact_analysis.apis?.map((api: string) => (
                      <span key={api} className="px-3 py-1.5 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-medium font-mono">
                        {api}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Service Context</h4>
                  <div className="text-xs text-slate-300">
                    <span className="font-semibold text-indigo-400">Capability:</span> {result.results.service_details?.business_capability}
                    <p className="mt-1"><span className="font-semibold text-indigo-400">Purpose:</span> {result.results.service_details?.purpose}</p>
                  </div>
                </div>
              </div>

              {/* Risk Rating Box */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 flex gap-3">
                <ShieldAlert className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-semibold text-slate-200">Risk Assessment</h4>
                  <p className="text-xs text-slate-400 mt-1">{result.results.impact_analysis.risk}</p>
                </div>
              </div>
            </div>

            {/* Implementation Recommendations Card */}
            <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
              <h3 className="font-bold text-base text-white flex items-center gap-2 border-b border-slate-800 pb-3">
                <FileText className="h-5 w-5 text-indigo-400" />
                Synthesized Developer Playbook
              </h3>

              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Implementation Guidelines</h4>
                  <ul className="space-y-2">
                    {result.results.generated_plan?.implementation.map((step: string, idx: number) => (
                      <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-850/50">
                        <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 mt-2 shrink-0"></span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Quality Assurance / Testing</h4>
                  <ul className="space-y-2">
                    {result.results.generated_plan?.testing.map((test: string, idx: number) => (
                      <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-850/50">
                        <CheckSquare className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                        <span>{test}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Key Contacts & Reviewers</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/80 p-4 rounded-xl border border-slate-850">
                    <div>
                      <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">SMEs & Owners</span>
                      <ul className="text-xs text-slate-300 space-y-1 mt-1">
                        {result.results.key_contacts.owners?.map((owner: string) => (
                          <li key={owner} className="flex items-center gap-1.5">
                            <Users className="h-3 w-3 text-slate-500" />
                            {owner}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Architects</span>
                      <ul className="text-xs text-slate-300 space-y-1 mt-1">
                        {result.results.key_contacts.architects?.map((arch: string) => (
                          <li key={arch} className="flex items-center gap-1.5">
                            <Settings className="h-3 w-3 text-slate-500" />
                            {arch}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Explainability Panel (Right Side Panel) */}
          <div className="xl:col-span-1 p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col gap-6 h-[750px] overflow-y-auto">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-slate-800 pb-3 shrink-0">
              <Eye className="h-4.5 w-4.5 text-indigo-400 animate-pulse" />
              AI Explainability Panel
            </h3>

            {result.explainability ? (
              <div className="space-y-6">
                
                {/* Confidence Meter */}
                <div className="flex flex-col items-center justify-center p-4 bg-slate-950 border border-slate-850 rounded-xl relative">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1">
                    <Gauge className="h-3.5 w-3.5 text-indigo-400" />
                    Confidence Score
                  </span>
                  <div className="relative flex items-center justify-center">
                    <svg className="w-20 h-20">
                      <circle className="text-slate-800" strokeWidth="5" stroke="currentColor" fill="transparent" r="34" cx="40" cy="40" />
                      <circle 
                        className="text-indigo-500 transition-all duration-1000" 
                        strokeWidth="5" 
                        strokeDasharray={213}
                        strokeDashoffset={213 - (213 * result.explainability.confidence_score) / 100}
                        strokeLinecap="round" 
                        stroke="currentColor" 
                        fill="transparent" 
                        r="34" 
                        cx="40" 
                        cy="40" 
                      />
                    </svg>
                    <span className="absolute text-lg font-extrabold text-white">{result.explainability.confidence_score}%</span>
                  </div>
                </div>

                {/* Why Chosen Callout */}
                <div className="p-4 bg-slate-950/80 border border-slate-850 rounded-xl space-y-2">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Why Chosen</span>
                  <p className="text-xs text-slate-300 leading-relaxed italic">
                    "{result.explainability.why_chosen}"
                  </p>
                </div>

                {/* Graph Nodes Traversed */}
                <div className="space-y-2">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                    <GitMerge className="h-3.5 w-3.5 text-indigo-400" />
                    Ontology Nodes Traversed ({result.explainability.nodes_traversed?.length})
                  </span>
                  <div className="flex flex-wrap gap-1.5 max-h-[140px] overflow-y-auto p-2 bg-slate-950 border border-slate-850 rounded-xl">
                    {result.explainability.nodes_traversed?.map((node: string) => (
                      <span 
                        key={node} 
                        className={`px-2 py-1 rounded text-[9px] font-mono border font-semibold ${getNodeColorClass(node)}`}
                      >
                        {node}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Documents Consulted */}
                <div className="space-y-2">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                    <FileCode className="h-3.5 w-3.5 text-indigo-400" />
                    Knowledge Sources Consulted
                  </span>
                  <ul className="text-xs text-slate-400 space-y-1.5 bg-slate-950 p-3 rounded-xl border border-slate-850">
                    {result.explainability.documents_consulted?.map((doc: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="h-1.5 w-1.5 rounded-full bg-slate-600 mt-1.5 shrink-0"></span>
                        <span className="truncate">{doc}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Similar Requirements Used */}
                {result.explainability.similar_requirements?.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                      Similar Requirements Mapped
                    </span>
                    <ul className="text-xs text-slate-400 space-y-1 bg-slate-950 p-3 rounded-xl border border-slate-850">
                      {result.explainability.similar_requirements?.map((req: string, idx: number) => (
                        <li key={idx} className="truncate">
                          🔍 {req}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Contributing Agents Flow */}
                <div className="space-y-2">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                    Contributing Agent Graph
                  </span>
                  <div className="flex flex-col gap-1.5 bg-slate-950 p-3 rounded-xl border border-slate-850 font-mono text-[9px]">
                    {result.explainability.contributing_agents?.map((agent: string, idx: number) => (
                      <div key={idx} className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-indigo-500 shrink-0"></span>
                        <span className="text-slate-300 font-semibold">{agent}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center text-slate-500 h-full gap-2">
                <HelpCircle className="h-6 w-6 text-slate-700" />
                <span className="text-xs">No analysis trace loaded.</span>
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
