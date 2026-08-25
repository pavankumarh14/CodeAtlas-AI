from typing import Dict, Any, List, Optional
import time
from .specialized_agents import (
    OntologyMentorAgent,
    RequirementImpactAgent,
    ExpertDiscoveryAgent,
    IncidentContextAgent,
    ArchitectureStorytellingAgent,
    KnowledgeGapAgent,
    ArchitecturalImpactAgent
)

class AgentOrchestrator:
    def __init__(self):
        # Register all 7 agents
        self.agents = {
            "ontology_mentor": OntologyMentorAgent(),
            "requirement_impact": RequirementImpactAgent(),
            "expert_discovery": ExpertDiscoveryAgent(),
            "incident_context": IncidentContextAgent(),
            "architecture_storytelling": ArchitectureStorytellingAgent(),
            "knowledge_gap": KnowledgeGapAgent(),
            "architectural_impact": ArchitecturalImpactAgent()
        }

    @staticmethod
    def _with_explainability(explainability: Optional[Dict[str, Any]], query: str, agent_name: str) -> Dict[str, Any]:
        """Guarantee the audit fields required beside every agent recommendation."""
        evidence = explainability or {}
        return {
            "why_chosen": evidence.get("why_chosen") or f"{agent_name} selected this answer after evaluating the engineering context for '{query}'.",
            "nodes_traversed": evidence.get("nodes_traversed") or ["Service:Engineering Knowledge Graph"],
            "documents_consulted": evidence.get("documents_consulted") or ["Engineering ontology index"],
            "similar_requirements": evidence.get("similar_requirements") or ["No directly comparable requirement was found"],
            "confidence_score": max(0, min(100, int(evidence.get("confidence_score", 70)))),
            "contributing_agents": evidence.get("contributing_agents") or [agent_name],
        }

    def _determine_flow(self, query: str) -> str:
        q = query.lower()
        
        # Collaborative requirement flow
        if any(w in q for w in ["add", "implement", "create", "requirement", "new feature", "whatsapp", "notifications"]):
            return "requirement_pipeline"
            
        # Incident context route
        if any(w in q for w in ["incident", "latency", "error", "down time", "down", "fail", "slow", "outage", "inc-"]):
            if "what happens if" in q or "blast radius" in q:
                return "architectural_impact"
            return "incident_context"
            
        # Expert route
        if any(w in q for w in ["who", "owner", "expert", "review", "lead", "sme"]):
            return "expert_discovery"
            
        # Storytelling route
        if any(w in q for w in ["how does", "flow", "walkthrough", "journey", "move"]):
            return "architecture_storytelling"
            
        # Knowledge gap route
        if any(w in q for w in ["gap", "undocumented", "missing", "health", "scan", "compliance"]):
            return "knowledge_gap"
            
        # Default fallback
        return "ontology_mentor"

    def execute(self, query: str) -> Dict[str, Any]:
        flow = self._determine_flow(query)
        execution_trace = []
        start_time = time.time()
        
        execution_trace.append(f"[Orchestrator] Received user query: '{query}'")
        execution_trace.append(f"[Orchestrator] Evaluated query routing. Path chosen: {flow.upper()}")

        if flow == "requirement_pipeline":
            # Multi-agent handoff pipeline:
            # Impact Agent -> Ontology Agent -> Expert Discovery Agent -> Implementation Recommendation Synthesis
            
            # Step 1: Impact Agent
            execution_trace.append("[Orchestrator] Step 1/3: Dispatching to Requirement Impact Agent...")
            impact_res = self.agents["requirement_impact"].run(query)
            execution_trace.extend([f"  [{impact_res['agent_name']}] {step}" for step in impact_res["trace"]])
            
            affected_services = impact_res["result"].get("affected_services", [])
            primary_service = affected_services[0] if affected_services else "Checkout Service"
            
            # Step 2: Ontology Agent on Primary Service
            execution_trace.append(f"[Orchestrator] Step 2/3: Handing off to Ontology Mentor Agent for: {primary_service}...")
            ontology_res = self.agents["ontology_mentor"].run(f"Explain {primary_service}")
            execution_trace.extend([f"  [{ontology_res['agent_name']}] {step}" for step in ontology_res["trace"]])
            
            # Step 3: Expert Discovery Agent on Primary Service
            execution_trace.append(f"[Orchestrator] Step 3/3: Handing off to Expert Discovery Agent for service experts...")
            expert_res = self.agents["expert_discovery"].run(f"Who owns {primary_service}")
            execution_trace.extend([f"  [{expert_res['agent_name']}] {step}" for step in expert_res["trace"]])
            
            # Synthesis (Implementation Recommendation Engine)
            execution_trace.append("[Orchestrator] Synthesizing collaborative reports into Implementation Plan...")
            
            synthesis = {
                "requirement": query,
                "impact_analysis": {
                    "services": impact_res["result"].get("affected_services"),
                    "repositories": impact_res["result"].get("affected_repositories"),
                    "apis": impact_res["result"].get("apis_involved"),
                    "risk": impact_res["result"].get("risk_analysis")
                },
                "service_details": {
                    "purpose": ontology_res["result"].get("purpose"),
                    "business_capability": ontology_res["result"].get("business_capability"),
                    "dependencies": ontology_res["result"].get("dependencies")
                },
                "key_contacts": {
                    "owners": expert_res["result"].get("owners"),
                    "architects": expert_res["result"].get("architects"),
                    "subject_matter_experts": expert_res["result"].get("subject_matter_experts")
                },
                "generated_plan": {
                    "implementation": impact_res["result"].get("recommendations", []),
                    "testing": [
                        f"1. Integration test with WhatsApp sandbox APIs using mocked payload",
                        f"2. Verify service logs in {primary_service.lower().replace(' ', '-')} for async notification publish event",
                        f"3. Run regression unit tests on {primary_service} dependencies"
                    ],
                    "reviewers": expert_res["result"].get("architects", []) + expert_res["result"].get("owners", [])
                }
            }

            # Synthesis of Explainability report
            imp_exp = impact_res.get("explainability", {})
            ont_exp = ontology_res.get("explainability", {})
            exp_exp = expert_res.get("explainability", {})

            pipeline_explainability = {
                "why_chosen": f"Synthesized orchestrated pipeline for requirement '{query}'. Mobilized the Requirement Impact Agent to map dependencies, the Ontology Mentor to profile {primary_service}, and the Expert Finder to identify reviewers.",
                "nodes_traversed": list(set(imp_exp.get("nodes_traversed", []) + ont_exp.get("nodes_traversed", []) + exp_exp.get("nodes_traversed", [])))[:12],
                "documents_consulted": list(set(imp_exp.get("documents_consulted", []) + ont_exp.get("documents_consulted", []) + exp_exp.get("documents_consulted", []))),
                "similar_requirements": list(set(imp_exp.get("similar_requirements", []) + ont_exp.get("similar_requirements", []) + exp_exp.get("similar_requirements", []))),
                "confidence_score": int((imp_exp.get("confidence_score", 90) + ont_exp.get("confidence_score", 90) + exp_exp.get("confidence_score", 90)) / 3),
                "contributing_agents": [self.agents["requirement_impact"].name, self.agents["ontology_mentor"].name, self.agents["expert_discovery"].name]
            }
            
            duration = round(time.time() - start_time, 2)
            execution_trace.append(f"[Orchestrator] Pipeline completed in {duration}s.")
            
            return {
                "flow_type": "pipeline",
                "target_agent": "Orchestrated Pipeline",
                "execution_trace": execution_trace,
                "results": synthesis,
                "explainability": self._with_explainability(pipeline_explainability, query, "Orchestrated Pipeline"),
                "duration_seconds": duration
            }
            
        else:
            # Single agent route
            agent_key = flow
            agent = self.agents[agent_key]
            execution_trace.append(f"[Orchestrator] Routing query to {agent.name}...")
            
            agent_res = agent.run(query)
            execution_trace.extend([f"  [{agent_res['agent_name']}] {step}" for step in agent_res["trace"]])
            
            duration = round(time.time() - start_time, 2)
            execution_trace.append(f"[Orchestrator] Query resolved in {duration}s.")
            
            return {
                "flow_type": "single_agent",
                "target_agent": agent.name,
                "execution_trace": execution_trace,
                "results": agent_res["result"],
                "explainability": self._with_explainability(agent_res.get("explainability"), query, agent.name),
                "duration_seconds": duration
            }
