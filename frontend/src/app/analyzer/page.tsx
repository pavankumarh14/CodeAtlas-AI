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
  CheckCircle2,
  CircleDot,
  Network
} from "lucide-react";
import { ExplainabilityPanel, type Explainability } from "@/components/explainability-panel";

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

    const interval = setInterval(() => {
      setActiveStep(s => s + 1);
    }, 1200);

    try {
      const res = await fetch("/api/v1/analyze", {
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

  const liveHandoffStages = [
    { agent: "Orchestrator", detail: "Classifies the engineering question and selects the specialist workflow." },
    { agent: "Requirement Impact Agent", detail: "Searches connected requirements, repositories, APIs, and dependencies." },
    { agent: "Ontology Mentor Agent", detail: "Traverses the knowledge graph to add architecture and service context." },
    { agent: "Expert Discovery Agent", detail: "Finds the owning team, reviewers, and subject-matter experts." },
    { agent: "Recommendation Synthesizer", detail: "Builds the plan and attaches its auditable evidence trail." },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Search Header */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
        <h3 className="font-bold text-base text-white mb-2">Analyze Proposed Engineering Requirement</h3>
        <p className="text-slate-400 text-xs mb-6">
          Enter a feature request, such as “Add WhatsApp notifications for order updates.” Run Agents to see the execution plan in the center, the agent handoff trace on the left, and the evidence-backed Explainability Panel on the right.
        </p>
        <div className="mb-4 flex flex-wrap gap-2">
          {[
            "Add WhatsApp notifications for order updates",
            "Implement order status emails",
            "Create a payment retry workflow",
          ].map((example) => (
            <button key={example} type="button" onClick={() => setQuery(example)} disabled={loading} className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5 text-[11px] text-slate-300 transition hover:border-indigo-400 hover:text-white disabled:opacity-50">
              Try: {example}
            </button>
          ))}
        </div>
        
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
        <div className="rounded-2xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/35 via-slate-900 to-slate-900 p-6">
          <div className="mb-5 flex items-center gap-3">
            <BrainCircuit className="h-8 w-8 text-indigo-400 animate-spin" />
            <div>
              <h4 className="text-sm font-bold text-white">Live agent handoff in progress</h4>
              <p className="mt-1 font-mono text-xs text-indigo-200">{loadingSteps[Math.min(activeStep, loadingSteps.length - 1)]}</p>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-5">
            {liveHandoffStages.map((stage, index) => {
              const state = index < activeStep ? "complete" : index === activeStep ? "active" : "waiting";
              return (
                <div key={stage.agent} className={`rounded-xl border p-3 ${state === "active" ? "border-indigo-400/60 bg-indigo-500/10" : state === "complete" ? "border-emerald-400/30 bg-emerald-500/5" : "border-slate-800 bg-slate-950/45"}`}>
                  <div className="mb-2 flex items-center gap-1.5">
                    {state === "complete" ? <CheckCircle2 className="h-4 w-4 text-emerald-400" /> : state === "active" ? <Network className="h-4 w-4 animate-pulse text-indigo-300" /> : <CircleDot className="h-4 w-4 text-slate-600" />}
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${state === "waiting" ? "text-slate-500" : "text-slate-200"}`}>Step {index + 1}</span>
                  </div>
                  <p className="text-xs font-semibold text-slate-200">{stage.agent}</p>
                  <p className="mt-1 text-[10px] leading-relaxed text-slate-400">{stage.detail}</p>
                </div>
              );
            })}
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
            {/* ── Document Q&A Answer ────────────────────────────────── */}
            {(result.results.answer || result.results.key_findings) ? (
              <>
                <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-5">
                  <h3 className="font-bold text-base text-white flex items-center gap-2 border-b border-slate-800 pb-3">
                    <FileText className="h-5 w-5 text-indigo-400" />
                    Document Analysis Result
                  </h3>
                  <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                    {result.results.answer}
                  </div>

                  {result.results.key_findings && result.results.key_findings.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">Key Findings</h4>
                      <ul className="space-y-2">
                        {result.results.key_findings.map((finding: string, idx: number) => (
                          <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-950/40 p-3 rounded-lg border border-slate-800">
                            <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 mt-2 shrink-0"></span>
                            <span className="break-words">{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.results.source_references && result.results.source_references.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">Source References</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.results.source_references.map((ref: string, idx: number) => (
                          <span key={idx} className="px-3 py-1.5 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-medium">
                            {ref}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.results.confidence && (
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
                      <ShieldAlert className="h-4 w-4 text-indigo-400 shrink-0" />
                      <span className="text-xs text-slate-300">Confidence: <b className="text-white">{result.results.confidence}</b></span>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                {/* ── Pipeline / Legacy Agent Card ──────────────────── */}
                <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
                  <h3 className="font-bold text-base text-white flex items-center gap-2 border-b border-slate-800 pb-3">
                    <Layers className="h-5 w-5 text-indigo-400" />
                    Blast Radius & Ontology Impact
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Affected Services</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.results.impact_analysis?.services?.map((svc: string) => (
                          <span key={svc} className="px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-medium">{svc}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Target Repositories</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.results.impact_analysis?.repositories?.map((repo: string) => (
                          <span key={repo} className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-medium font-mono">{repo}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Involved APIs</h4>
                      <div className="flex flex-wrap gap-2">
                        {result.results.impact_analysis?.apis?.map((api: string) => (
                          <span key={api} className="px-3 py-1.5 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-medium font-mono">{api}</span>
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
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 flex gap-3">
                    <ShieldAlert className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-xs font-semibold text-slate-200">Risk Assessment</h4>
                      <p className="text-xs text-slate-400 mt-1">{result.results.impact_analysis?.risk || result.results.risks || "No elevated risk was identified by this agent."}</p>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
                  <h3 className="font-bold text-base text-white flex items-center gap-2 border-b border-slate-800 pb-3">
                    <FileText className="h-5 w-5 text-indigo-400" />
                    Synthesized Developer Playbook
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Implementation Guidelines</h4>
                      <ul className="space-y-2">
                        {result.results.generated_plan?.implementation?.map((step: string, idx: number) => (
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
                        {result.results.generated_plan?.testing?.map((test: string, idx: number) => (
                          <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-850/50">
                            <CheckSquare className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                            <span>{test}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">Key Contacts &amp; Reviewers</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/80 p-4 rounded-xl border border-slate-850">
                        <div>
                          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">SMEs &amp; Owners</span>
                          <ul className="text-xs text-slate-300 space-y-1 mt-1">
                            {result.results.key_contacts?.owners?.map((owner: string) => (
                              <li key={owner} className="flex items-center gap-1.5"><Users className="h-3 w-3 text-slate-500" />{owner}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Architects</span>
                          <ul className="text-xs text-slate-300 space-y-1 mt-1">
                            {result.results.key_contacts?.architects?.map((arch: string) => (
                              <li key={arch} className="flex items-center gap-1.5"><Settings className="h-3 w-3 text-slate-500" />{arch}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="xl:col-span-1 h-[750px] overflow-y-auto">
            <ExplainabilityPanel explainability={result.explainability as Explainability} />
          </div>

        </div>
      )}
    </div>
  );
}
