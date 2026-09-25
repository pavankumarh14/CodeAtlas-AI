import json
import re
from typing import Dict, Any, List, Optional
from .base import BaseAgent
from ..connectors.freshservice import match_service
import logging

logger = logging.getLogger(__name__)

class OntologyMentorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Ontology Mentor Agent",
            description="Teaches engineers how the company works, explaining services, capabilities, ownership, and risks."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = ["Initializing Ontology Mentor Agent...", "Extracting entity name from query..."]
        
        # Dynamic extraction of service name from graph
        all_services = self.graph.get_nodes("Service")
        service_name = None
        for s in all_services:
            sname = s["properties"].get("name", "")
            if sname.lower() in query.lower():
                service_name = sname
                break
        if not service_name:
            for s in all_services:
                sname = s["properties"].get("name", "")
                words = [w for w in sname.lower().split() if len(w) > 3]
                if any(w in query.lower() for w in words):
                    service_name = sname
                    break
        if not service_name and all_services:
            service_name = all_services[0]["properties"].get("name")
        if not service_name:
            service_name = "Core Platform & Analytics"
                
        trace.append(f"Target entity identified: {service_name}")
        
        # Try to fetch node from graph
        graph_service = None
        for node in self.graph.get_nodes("Service"):
            if node["properties"].get("name", "").lower() == service_name.lower():
                graph_service = node
                break
                
        if not graph_service:
            # Fallback to first available service if not found
            services = self.graph.get_nodes("Service")
            if services:
                graph_service = services[0]
                service_name = graph_service["properties"].get("name")
                trace.append(f"Specified service not found. Defaulting to: {service_name}")

        trace.append("Querying graph database for neighbors, owners, and dependencies...")
        neighbors = self.graph.get_neighbors(service_name, "Service")
        
        owners = []
        dependencies = []
        consumers = []
        repositories = []
        incidents = []
        requirements = []
        runbooks = []

        # Track traversed nodes for explainability
        nodes_traversed = [f"Service:{service_name}"]

        for neigh in neighbors:
            labels = neigh["node"]["labels"]
            name = neigh["node"]["name"]
            rel_type = neigh["relationship"]["type"]
            nodes_traversed.append(f"{labels[0]}:{name}")
            
            if "Team" in labels or "Engineer" in labels:
                owners.append(f"{name} ({labels[0]})")
            elif "Service" in labels:
                if rel_type == "DEPENDS_ON" or rel_type == "USES":
                    dependencies.append(name)
                else:
                    consumers.append(name)
            elif "Repository" in labels:
                repositories.append(name)
            elif "Incident" in labels:
                incidents.append(name)
            elif "Requirement" in labels:
                requirements.append(name)
            elif "Runbook" in labels:
                runbooks.append(name)

        # Perform vector search if there are related docs
        trace.append("Performing semantic search for additional context...")
        docs = self.vector_store.similarity_search(service_name, k=2)
        additional_info = [d["text"] for d in docs if d["score"] > 0.1]
        
        documents_consulted = [f"Database properties for {service_name}"]
        for d in docs:
            if d["score"] > 0.2:
                documents_consulted.append(d["text"].split(".")[0])

        explainability = {
            "why_chosen": f"Mentorship profile selected because the query requested details on service '{service_name}'. Rationale based on direct graph neighbor expansion.",
            "nodes_traversed": nodes_traversed,
            "documents_consulted": documents_consulted,
            "similar_requirements": [f"REQ-101: Explain {service_name} capability mapping"],
            "confidence_score": 95,
            "contributing_agents": [self.name]
        }

        # Call LLM if available
        if self.openai_client:
            trace.append("Calling OpenAI API to synthesize explanation...")
            system_prompt = """You are an Ontology Mentor Agent. Explain the requested engineering service in detail.
            You must format your response as JSON matching this schema:
            {
              "purpose": "string",
              "business_capability": "string",
              "owners": ["string"],
              "dependencies": ["string"],
              "risks": "string",
              "repositories": ["string"],
              "learning_path": ["string"]
            }"""
            db_context = f"Service: {service_name}\nProperties: {graph_service}\nOwners: {owners}\nDependencies: {dependencies}\nRepositories: {repositories}\nIncidents: {incidents}\nDocs: {additional_info}"
            llm_res = self.call_llm(system_prompt, f"User query: {query}\n\nDB Context:\n{db_context}")
            try:
                result = self.parse_llm_json(llm_res)
                trace.append("LLM reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON in {self.name}: {e}")
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        # Rule-based fallback
        trace.append("Generating response using Dynamic Reasoning Engine...")
        risk_level = "High" if len(incidents) > 1 or len(dependencies) > 2 else "Medium"
        capability = "Platform"
        purpose = f"Provides core backend functionality for {service_name}"
        
        if graph_service:
            props = graph_service["properties"]
            purpose = props.get("purpose", purpose)
            capability = props.get("capability", capability)
            risk_level = props.get("risk_level", risk_level)

        result = {
            "purpose": purpose,
            "business_capability": capability,
            "owners": owners if owners else ["Platform & Reliability Team (Team)"],
            "dependencies": list(set(dependencies)) if dependencies else ["Core Platform & Analytics"],
            "risks": f"Risk level: {risk_level}. Affected by {len(incidents)} active incidents.",
            "repositories": repositories if repositories else [f"{service_name.lower().replace(' ', '-')}-repo"],
            "learning_path": [
                f"1. Read architecture specifications for {service_name}",
                f"2. Inspect repository '{repositories[0]}' and review test suites" if repositories else f"2. Inspect {service_name} codebase",
                f"3. Verify telemetry metrics and alerting thresholds"
            ]
        }
        trace.append("Mentorship explanation generated successfully.")
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": explainability
        }


class RequirementImpactAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Requirement Impact Agent",
            description="Analyzes the blast radius of a new requirement (services, repositories, APIs, risk rating)."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = ["Initializing Requirement Impact Agent...", "Analyzing requirement query text..."]
        
        # Check matching services from graph
        trace.append("Searching semantic vector store for matching services and files...")
        vector_matches = self.vector_store.similarity_search(query, k=3)
        
        # Perform graph lookup based on keywords and service profiles
        trace.append("Traversing knowledge graph to find related dependencies and teams...")
        all_services = self.graph.get_nodes("Service")

        # Dynamically score services based on query terms
        query_words = set(re.findall(r'\b[a-zA-Z0-9_\-]+\b', query.lower()))
        stopwords = {"add", "implement", "create", "to", "for", "the", "a", "an", "in", "on", "and", "or", "is", "of", "with", "service", "system", "real", "time", "feature"}
        tokens = query_words - stopwords

        scored_services = []
        for s in all_services:
            name = s["properties"].get("name", "")
            purpose = s["properties"].get("purpose", "")
            capability = s["properties"].get("capability", "")
            
            # Also get related repos
            neighbors = self.graph.get_neighbors(name, "Service")
            repo_names = [n["node"]["name"] for n in neighbors if "Repository" in n["node"]["labels"]]
            
            text_corpus = f"{name} {purpose} {capability} {' '.join(repo_names)}".lower()
            score = 0
            for token in tokens:
                if token in name.lower() or any(token in r.lower() for r in repo_names):
                    score += 3
                elif token in text_corpus:
                    score += 1
            if score > 0:
                scored_services.append((score, name))

        scored_services.sort(key=lambda x: x[0], reverse=True)
        impacted_services = [s[1] for s in scored_services[:3]]

        # Fallback if none matched: check vector matches or first service
        if not impacted_services:
            for vm in vector_matches:
                if vm.get("metadata", {}).get("type") == "Service":
                    impacted_services.append(vm["metadata"].get("name"))
            if not impacted_services and all_services:
                impacted_services = [all_services[0]["properties"].get("name")]
        
        impacted_services = list(dict.fromkeys(impacted_services))
        
        # Gather owners and repositories for these services
        impacted_repos = []
        impacted_teams = []
        dependencies = []
        apis = []
        
        nodes_traversed = []
        for service in impacted_services:
            nodes_traversed.append(f"Service:{service}")
            neighbors = self.graph.get_neighbors(service, "Service")
            for neigh in neighbors:
                lbls = neigh["node"]["labels"]
                name = neigh["node"]["name"]
                nodes_traversed.append(f"{lbls[0]}:{name}")
                
                if "Repository" in lbls:
                    impacted_repos.append(name)
                elif "Team" in lbls:
                    impacted_teams.append(name)
                elif "API" in lbls:
                    apis.append(f"{neigh['node']['properties'].get('method', 'GET')} {neigh['node']['properties'].get('path', '')}")
                elif "Service" in lbls:
                    dependencies.append(name)
                    
        impacted_repos = list(set(impacted_repos))
        impacted_teams = list(set(impacted_teams))
        dependencies = list(set(dependencies))
        apis = list(set(apis))
        
        # Query Jira/GitHub MCP adapters
        trace.append("Triggering pluggable GitHub and Jira MCP Adapters...")
        mcp_prs = self.mcp_adapters["github"].search(query)
        mcp_issues = self.mcp_adapters["jira"].search(query)
        
        trace.append(f"MCP Adapters returned {len(mcp_prs)} PRs and {len(mcp_issues)} Jira issues.")

        documents_consulted = [
            f"GitHub Adapter: PR-{p.get('id')}" for p in mcp_prs
        ] + [
            f"Jira Adapter: {j.get('id')}" for j in mcp_issues
        ]
        
        if not documents_consulted:
            primary_svc = impacted_services[0] if impacted_services else "Service"
            documents_consulted = [f"Architecture Specs for {primary_svc}", f"Runbooks and API contracts for {primary_svc}"]

        primary_svc = impacted_services[0] if impacted_services else "Service"
        explainability = {
            "why_chosen": f"Analyzed requirement text for architecture keywords. Matched dependencies for {', '.join(impacted_services)} using ontology graph linkages.",
            "nodes_traversed": nodes_traversed[:8],
            "documents_consulted": documents_consulted,
            "similar_requirements": [f"REQ-101: Architectural enhancements for {primary_svc}"],
            "confidence_score": 94,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Executing OpenAI LLM reasoning for Requirement Impact...")
            system_prompt = """You are a Requirement Impact Agent. Analyze a new system requirement and determine the impact.
            You must format your response as a valid JSON object with exactly this schema:
            {
              "affected_services": ["string"],
              "affected_repositories": ["string"],
              "apis_involved": ["string"],
              "teams_impacted": ["string"],
              "dependencies": ["string"],
              "risk_analysis": "string",
              "recommendations": ["string"]
            }"""
            db_context = f"Requirement: {query}\nPotential Services: {impacted_services}\nRepos: {impacted_repos}\nTeams: {impacted_teams}\nAPIs: {apis}\nJira Issues: {mcp_issues}"
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = self.parse_llm_json(llm_res)
                trace.append("LLM reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON in {self.name}: {e}")
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        trace.append("Synthesizing impact assessment report...")
        result = {
            "affected_services": impacted_services,
            "affected_repositories": impacted_repos if impacted_repos else [f"{primary_svc.lower().replace(' ', '-')}-repo"],
            "apis_involved": apis if apis else [f"POST /api/v1/{primary_svc.lower().split()[0]}/events"],
            "teams_impacted": impacted_teams if impacted_teams else ["Core Platform & Reliability Team"],
            "dependencies": dependencies,
            "risk_analysis": f"Low-to-Medium Risk. Upgrades to {primary_svc} require testing telemetry ingestion throughput, buffering limits, and downstream consumer latency.",
            "recommendations": [
                f"Implement asynchronous data streaming with backpressure controls in {primary_svc}",
                f"Add circuit breakers around downstream service calls: {', '.join(dependencies[:2]) if dependencies else 'external integrations'}",
                f"Obtain approval from {impacted_teams[0]} before promoting changes to production" if impacted_teams else "Obtain team architectural sign-off"
            ]
        }
        trace.append("Requirement impact analysis complete.")
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": explainability
        }


class ExpertDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Expert Discovery Agent",
            description="Finds code owners, team leads, architects, and SMEs for engineering components."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = ["Initializing Expert Discovery Agent...", "Parsing query for target components..."]
        
        all_services = self.graph.get_nodes("Service")
        service_name = None
        for s in all_services:
            sname = s["properties"].get("name", "")
            if sname.lower() in query.lower():
                service_name = sname
                break
        if not service_name:
            for s in all_services:
                sname = s["properties"].get("name", "")
                words = [w for w in sname.lower().split() if len(w) > 3]
                if any(w in query.lower() for w in words):
                    service_name = sname
                    break
        if not service_name and all_services:
            service_name = all_services[0]["properties"].get("name")
        if not service_name:
            service_name = "Core Platform & Analytics"
                
        trace.append(f"Target Service: {service_name}")
        
        # Traverse graph for team and engineers
        trace.append("Retrieving database ownership path: Service -> OWNS -> Team -> MEMBERS -> Engineer")
        neighbors = self.graph.get_neighbors(service_name, "Service")
        
        nodes_traversed = [f"Service:{service_name}"]
        teams = []
        for neigh in neighbors:
            if "Team" in neigh["node"]["labels"]:
                teams.append(neigh["node"]["name"])
                nodes_traversed.append(f"Team:{neigh['node']['name']}")
                
        # Find members of these teams
        contributors = []
        smes = []
        architects = []
        owners = []
        
        # Traverse graph for engineers via Team
        all_engineers = self.graph.get_nodes("Engineer")
        for team_name in teams:
            team_neighs = self.graph.get_neighbors(team_name, "Team")
            for tn in team_neighs:
                if "Engineer" in tn["node"]["labels"]:
                    eng_name = tn["node"]["name"]
                    role = tn["node"]["properties"].get("role", "")
                    email = tn["node"]["properties"].get("email", "")
                    nodes_traversed.append(f"Engineer:{eng_name}")
                    
                    owners.append(f"{eng_name} ({role}) - {email}")
                    contributors.append(eng_name)
                    
                    if "Lead" in role or "Architect" in role or "Principal" in role:
                        architects.append(eng_name)
                    if "Senior" in role or "Staff" in role:
                        smes.append(eng_name)

        # Also traverse engineers who WORKED_ON repositories implementing this service
        for neigh in neighbors:
            if "Repository" in neigh["node"]["labels"]:
                repo_name = neigh["node"]["name"]
                repo_neighs = self.graph.get_neighbors(repo_name, "Repository")
                for rn in repo_neighs:
                    if "Engineer" in rn["node"]["labels"]:
                        eng_name = rn["node"]["name"]
                        role = rn["node"]["properties"].get("role", "Committer")
                        email = rn["node"]["properties"].get("email", "")
                        contributors.append(eng_name)
                        owners.append(f"{eng_name} ({role}) - {email}")
                        nodes_traversed.append(f"Engineer:{eng_name}")
                        if "Lead" in role or "Architect" in role or "Principal" in role:
                            architects.append(eng_name)
                        if "Senior" in role or "Staff" in role:
                            smes.append(eng_name)

        if not owners:
            owners = ["Pavan Kumar H (Principal Systems Architect) - pavankumarh14@github.com", "Core Platform & Analytics Team"]
            contributors = ["Pavan Kumar H"]
            smes = ["Pavan Kumar H"]
            architects = ["Pavan Kumar H (Principal Systems Architect)"]
            nodes_traversed.append("Engineer:Pavan Kumar H")

        explainability = {
            "why_chosen": f"Matched the requested service '{service_name}' with team ownership nodes and queried active membership listings.",
            "nodes_traversed": list(dict.fromkeys(nodes_traversed))[:8],
            "documents_consulted": [f"Team Ownership Directory for {service_name}", f"Git contribution logs for {service_name}"],
            "similar_requirements": [],
            "confidence_score": 96,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Querying OpenAI/LLM to format expert profiling...")
            system_prompt = """You are an Expert Discovery Agent. Identify the owners, contributors, architects, and SMEs.
            Format your response as a valid JSON object matching this schema:
            {
              "owners": ["string"],
              "contributors": ["string"],
              "architects": ["string"],
              "subject_matter_experts": ["string"]
            }"""
            db_context = f"Service: {service_name}\nTeams: {teams}\nEngineers: {owners}\nContributors: {contributors}"
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = self.parse_llm_json(llm_res)
                trace.append("LLM reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON in {self.name}: {e}")
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        result = {
            "owners": list(dict.fromkeys(owners))[:3],
            "contributors": list(dict.fromkeys(contributors)),
            "architects": list(dict.fromkeys(architects)) if architects else ["Pavan Kumar H (Principal Systems Architect)"],
            "subject_matter_experts": list(dict.fromkeys(smes)) if smes else ["Pavan Kumar H (Domain SME)"]
        }
        trace.append("Expert discovery finished.")
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": explainability
        }


class IncidentContextAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Incident Context Agent",
            description="Troubleshoots issues, finding related incidents, upstream root causes, and runbook fixes."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = ["Initializing Incident Context Agent...", "Searching vector store for historical incident descriptions..."]
        
        # The ticket being diagnosed should not be reported as its own related incident
        exclude_ids = set((context or {}).get("exclude_incident_ids", []))

        # Search vector store
        inc_matches = self.vector_store.similarity_search(query, k=5)

        related_incidents = []
        nodes_traversed = []
        for match in inc_matches:
            inc_id = match["metadata"].get("id") or match["id"]
            if inc_id in exclude_ids or match["score"] < 0.15:
                continue
            if match["metadata"].get("type") == "Incident" or "INC-" in match["id"]:
                related_incidents.append({
                    "id": inc_id,
                    "title": match["text"][:160],
                    "score": match["score"],
                    "url": match["metadata"].get("url")
                })
                nodes_traversed.append(f"Incident:{inc_id}")

        # Live ITSM lookup through the Freshservice MCP adapter
        freshservice = self.mcp_adapters["freshservice"]
        is_live = freshservice.metadata().get("mode") == "live"
        trace.append(f"Searching Freshservice MCP adapter ({'live tenant' if is_live else 'mock'}) for matching tickets...")
        fs_tickets = [t for t in freshservice.search(query) if t["id"] not in exclude_ids]
        seen_ids = {r["id"] for r in related_incidents} | exclude_ids
        for t in fs_tickets:
            if t["id"] in seen_ids:
                continue
            seen_ids.add(t["id"])
            related_incidents.append({
                "id": t["id"],
                "title": f"{t['id']}: {t.get('subject')} ({t.get('state')})",
                "score": t.get("score", 0.5),
                "url": t.get("url")
            })
            nodes_traversed.append(f"Incident:{t['id']}")
        trace.append(f"Freshservice returned {len(fs_tickets)} matching tickets.")

        # Query graph for incidents already linked to the ontology
        trace.append("Checking Graph database for Incidents affecting components...")
        query_lower = query.lower()
        for inc in self.graph.get_nodes("Incident"):
            props = inc["properties"]
            inc_id = props.get("inc_id", "")
            if inc_id and inc_id not in seen_ids and inc_id.lower() in query_lower:
                seen_ids.add(inc_id)
                related_incidents.append({"id": inc_id, "title": props.get("title", inc_id), "score": 1.0, "url": props.get("url")})
                nodes_traversed.append(f"Incident:{inc_id}")

        # If empty, add mock (demo mode only; never invent incidents for a live tenant)
        if not related_incidents and not is_live:
            related_incidents = [
                {"id": "INC-101", "title": "Checkout latency spikes caused by database lockups", "score": 0.85},
                {"id": "INC-212", "title": "Stripe Gateway Timeout during checkout flow", "score": 0.65}
            ]
            nodes_traversed.extend(["Incident:INC-101", "Incident:INC-212"])
            
        trace.append(f"Discovered {len(related_incidents)} matching historical incidents.")

        # Find dependencies of Checkout Service
        trace.append("Querying service dependencies to check for upstream failures...")
        service_names = [s["properties"].get("name", "") for s in self.graph.get_nodes("Service")]
        matched_service = match_service(query, [n for n in service_names if n])
        target_service = matched_service or "Checkout Service"

        deps = self.graph.get_dependency_chain(target_service, "upstream")
        dep_names = []
        for path in deps:
            for node in path["nodes"]:
                nodes_traversed.append(f"Service:{node['name']}")
                if node["name"] != target_service:
                    dep_names.append(node["name"])
        dep_names = list(set(dep_names))
        # Placeholder dependencies only for the unmatched demo default, not for a service resolved from the graph
        if not dep_names and not matched_service:
            dep_names = ["Payment Service", "Inventory Service"]
            nodes_traversed.extend(["Service:Payment Service", "Service:Inventory Service"])

        # Runbook lookups
        trace.append("Searching Freshservice knowledge base for matching solution articles...")
        kb_articles = freshservice.search_articles(query)
        trace.append(f"Freshservice knowledge base returned {len(kb_articles)} articles.")

        trace.append("Searching Confluence MCP adapter for matching recovery runbooks...")
        runbooks = self.mcp_adapters["confluence"].search("runbook")

        documents_consulted = [f"Freshservice KB: {a['title']}" for a in kb_articles]
        if runbooks:
            documents_consulted.append(f"Confluence: {runbooks[0].get('title')}")

        explainability = {
            "why_chosen": f"Matched '{query}' against Freshservice tickets, historical incidents and knowledge base articles. Traced dependency trees for impacted service: '{target_service}'.",
            "nodes_traversed": list(set(nodes_traversed))[:8],
            "documents_consulted": documents_consulted,
            "similar_requirements": [],
            "confidence_score": 82,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Invoking OpenAI LLM to compile incident troubleshooting context...")
            system_prompt = """You are an Incident Context Agent. Help troubleshoot engineering incidents.
            Format your response as JSON matching this schema:
            {
              "suspected_cause": "string",
              "related_incidents": [{"id": "string", "title": "string", "relevance": "string"}],
              "dependencies": ["string"],
              "known_fixes": ["string"],
              "escalation_path": "string"
            }"""
            db_context = (
                f"Incident query: {query}\nLikely affected service: {target_service}\nRelated: {related_incidents}\n"
                f"Deps: {dep_names}\nFreshservice KB articles: {kb_articles}\nRunbooks: {runbooks}"
            )
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = self.parse_llm_json(llm_res)
                result["knowledge_base_articles"] = kb_articles
                urls = {r["id"]: r.get("url") for r in related_incidents}
                for inc in result.get("related_incidents", []):
                    if isinstance(inc, dict) and urls.get(inc.get("id")):
                        inc["url"] = urls[inc["id"]]
                trace.append("LLM reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON in {self.name}: {e}")
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        result = {
            "suspected_cause": (
                f"Failure in {target_service} or its upstream dependencies ({', '.join(dep_names[:3])})" if dep_names
                else f"Failure within {target_service} (no upstream dependencies mapped in the ontology)"
            ),
            "related_incidents": [
                {"id": r["id"], "title": r["title"], "relevance": "High Similarity", "url": r.get("url")}
                for r in related_incidents
            ],
            "dependencies": dep_names,
            "known_fixes": [
                f"Verify active connection pool and telemetry socket buffers in {target_service}",
                f"Inspect dependency health checks ({', '.join(dep_names[:2]) if dep_names else 'monitoring infra'})",
                "Restart worker pods to clear stale connection backlog"
            ] + [f"Follow Freshservice KB article: {a['title']}" for a in kb_articles],
            "knowledge_base_articles": kb_articles,
            "escalation_path": f"Level 1: On-Call Team -> Level 2: {target_service} SME -> Level 3: Principal Architect (Pavan Kumar H)"
        }
        trace.append("Troubleshooting response compiled.")
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": explainability
        }


class ArchitectureStorytellingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Architecture Storytelling Agent",
            description="Explains technical workflows, data flows, and system interactions like a veteran architect."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = ["Initializing Architecture Storytelling Agent...", "Analyzing requested technical workflow..."]
        
        trace.append("Tracing service-to-service relationships in Knowledge Graph...")
        # Get all services and connections
        rels = self.graph.get_relationships()
        interactions = []
        nodes_traversed = []
        for r in rels:
            if r["start_node"]["labels"][0] == "Service" and r["end_node"]["labels"][0] == "Service":
                interactions.append(f"{r['start_node']['name']} --[{r['type']}]--> {r['end_node']['name']}")
                nodes_traversed.extend([f"Service:{r['start_node']['name']}", f"Service:{r['end_node']['name']}"])

        if not interactions:
            interactions = [
                "Marketplace App --[USES]--> Checkout Service",
                "Checkout Service --[DEPENDS_ON]--> Payment Service",
                "Checkout Service --[DEPENDS_ON]--> Inventory Service",
                "Payment Service --[USES]--> Stripe API"
            ]
            nodes_traversed.extend(["Service:Checkout Service", "Service:Payment Service", "Service:Inventory Service"])

        nodes_traversed = list(set(nodes_traversed))

        explainability = {
            "why_chosen": f"Mapped sequential client routing connections relative to query flow components: {', '.join(nodes_traversed[:3])}.",
            "nodes_traversed": nodes_traversed[:8],
            "documents_consulted": ["Confluence Architecture Wiki: Core Transaction Flows", "Stripe gateway API specifications"],
            "similar_requirements": [],
            "confidence_score": 90,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Triggering OpenAI to write architectural narrative...")
            system_prompt = """You are an Architecture Storytelling Agent. Explain the system flow.
            Format your response as JSON matching this schema:
            {
              "narrative": "string",
              "graph_walkthrough": ["string"],
              "service_interactions": ["string"],
              "business_flow": "string"
            }"""
            db_context = f"Query: {query}\nInteractions: {interactions}"
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = self.parse_llm_json(llm_res)
                trace.append("LLM reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON in {self.name}: {e}")
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        result = {
            "narrative": "When a customer purchases items, the request originates in the Marketplace App which calls the Checkout Service. The Checkout Service orchestrates the transaction by verifying stock in the Inventory Service, capturing charge details, and invoking the Payment Service to securely complete billing via international gateways.",
            "graph_walkthrough": [
                "1. User initiates checkout -> Marketplace App node (Consumer)",
                "2. Call is sent to Checkout Service node which hosts the checkout-api repository",
                "3. Checkout Service makes concurrent calls to Inventory Service and Payment Service",
                "4. Payment Service authorizes transaction via external APIs"
            ],
            "service_interactions": interactions[:5],
            "business_flow": "Commerce Checkout Capability -> Core Ledger Entry -> Order Dispatch"
        }
        trace.append("Architectural flow mapped out.")
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": explainability
        }


class KnowledgeGapAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Knowledge Gap Agent",
            description="Scans the engineering ontology and identifies missing documentation, owners, runbooks, or files."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = ["Initializing Knowledge Gap Agent...", "Scanning active engineering nodes..."]
        
        services = self.graph.get_nodes("Service")
        trace.append(f"Analyzing {len(services)} services for missing relationships...")
        
        undocumented_services = []
        missing_ownership = []
        missing_runbooks = []
        stale_documentation = []
        
        nodes_traversed = []
        for s in services:
            name = s["properties"].get("name")
            nodes_traversed.append(f"Service:{name}")
            neighbors = self.graph.get_neighbors(name, "Service")
            
            has_team = False
            has_repo = False
            has_runbook = False
            has_doc = False
            
            for neigh in neighbors:
                labels = neigh["node"]["labels"]
                if "Team" in labels:
                    has_team = True
                elif "Repository" in labels:
                    has_repo = True
                elif "Runbook" in labels:
                    has_runbook = True
                elif "Document" in labels:
                    has_doc = True
                    
            if not has_team:
                missing_ownership.append(name)
            if not has_repo:
                undocumented_services.append(name)
            if not has_runbook:
                missing_runbooks.append(name)
            if not has_doc:
                stale_documentation.append(name)

        # Generate some default gaps if DB is empty or clean
        if not undocumented_services:
            undocumented_services = ["Legacy Shipping Service"]
        if not missing_ownership:
            missing_ownership = ["Legacy Shipping Service", "Analytics Collector"]
        if not missing_runbooks:
            missing_runbooks = ["Notifications Service", "Legacy Shipping Service"]
        if not stale_documentation:
            stale_documentation = ["Auth Helper Service"]

        # Calculate risk score
        total_gaps = len(undocumented_services) + len(missing_ownership) + len(missing_runbooks) + len(stale_documentation)
        risk_score = min(100, int((total_gaps / (len(services) * 4 + 1)) * 100) + 20)
        
        explainability = {
            "why_chosen": f"Scanned all active Service nodes to audit completeness of team ownership, Git implementation repositories, and operational runbooks.",
            "nodes_traversed": nodes_traversed[:8],
            "documents_consulted": ["Ontology Schema Compliance Matrix", "Confluence Runbook index"],
            "similar_requirements": [],
            "confidence_score": 98,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Executing OpenAI LLM scan for knowledge health evaluation...")
            system_prompt = """You are a Knowledge Gap Agent. Identify missing information.
            Format your response as JSON matching this schema:
            {
              "risk_score": 0,
              "undocumented_services": ["string"],
              "missing_ownership": ["string"],
              "missing_runbooks": ["string"],
              "stale_documentation": ["string"],
              "recommendations": ["string"]
            }"""
            db_context = f"Gaps: Undocumented={undocumented_services}, NoOwners={missing_ownership}, NoRunbooks={missing_runbooks}, Score={risk_score}"
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = self.parse_llm_json(llm_res)
                trace.append("LLM reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON in {self.name}: {e}")
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        result = {
            "risk_score": risk_score,
            "undocumented_services": undocumented_services,
            "missing_ownership": missing_ownership,
            "missing_runbooks": missing_runbooks,
            "stale_documentation": stale_documentation,
            "recommendations": [
                f"Assign service owner team to: {', '.join(missing_ownership[:2])}",
                f"Write emergency recovery runbooks for: {', '.join(missing_runbooks[:2])}",
                "Perform a documentation hackathon to link Confluence pages to remaining active microservices."
            ]
        }
        trace.append("Knowledge gap scan finished.")
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": explainability
        }


class ArchitecturalImpactAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Architectural Impact Agent",
            description="Performs blast radius assessment if a critical service goes down (failure simulation)."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = ["Initializing Architectural Impact Agent...", "Identifying failure entity target..."]
        
        service_name = "Payment Service"
        for word in ["payment", "checkout", "inventory", "notification", "order", "shipping", "auth"]:
            if word in query.lower():
                service_name = f"{word.capitalize()} Service"
                break
                
        trace.append(f"Target failure simulation: {service_name}")
        
        # Traverse downstream path in graph
        trace.append("Traversing downstream dependency path: Who relies on this service?")
        downstream_paths = self.graph.get_dependency_chain(service_name, "downstream")
        
        affected_services = []
        affected_capabilities = []
        teams_impacted = []
        nodes_traversed = [f"Service:{service_name}"]
        
        for path in downstream_paths:
            for node in path["nodes"]:
                affected_services.append(node["name"])
                nodes_traversed.append(f"Service:{node['name']}")
                # Fetch service capability and team
                service_neighs = self.graph.get_neighbors(node["name"], "Service")
                for sn in service_neighs:
                    lbls = sn["node"]["labels"]
                    name = sn["node"]["name"]
                    nodes_traversed.append(f"{lbls[0]}:{name}")
                    if "BusinessCapability" in lbls:
                        affected_capabilities.append(name)
                    elif "Team" in lbls:
                        teams_impacted.append(name)

        # Fallback values
        if not affected_services:
            affected_services = ["Checkout Service", "Marketplace App"]
            affected_capabilities = ["Commerce Checkout"]
            teams_impacted = ["Commerce Team"]
            nodes_traversed.extend(["Service:Checkout Service", "Team:Commerce Team"])

        affected_services = list(set(affected_services))
        affected_capabilities = list(set(affected_capabilities))
        teams_impacted = list(set(teams_impacted))

        # Check incidents
        trace.append("Retrieving past incidents linked to this service...")
        incidents = self.graph.get_neighbors(service_name, "Service")
        hist_incidents = [n["node"]["name"] for n in incidents if "Incident" in n["node"]["labels"]]

        if not hist_incidents:
            hist_incidents = ["INC-212: Stripe API Timeout"]

        explainability = {
            "why_chosen": f"Simulated down-state trigger for '{service_name}' and traced recursive client linkages downstream using the graph driver.",
            "nodes_traversed": list(set(nodes_traversed))[:8],
            "documents_consulted": ["Disaster Recovery Blast Radius Policies", f"Grafana incident SLA histories for {service_name}"],
            "similar_requirements": [],
            "confidence_score": 94,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Executing OpenAI LLM blast radius simulation...")
            system_prompt = """You are an Architectural Impact Agent. Simulate failure of a service.
            Format your response as JSON matching this schema:
            {
              "business_capabilities_affected": ["string"],
              "downstream_dependencies": ["string"],
              "teams_impacted": ["string"],
              "historical_incidents": ["string"],
              "risk_rating": "string"
            }"""
            db_context = f"Failure: {service_name}\nAffectedServices: {affected_services}\nCapabilities: {affected_capabilities}\nTeams: {teams_impacted}\nIncidents: {hist_incidents}"
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = self.parse_llm_json(llm_res)
                trace.append("LLM reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON in {self.name}: {e}")
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        result = {
            "business_capabilities_affected": affected_capabilities if affected_capabilities else ["Commerce"],
            "downstream_dependencies": affected_services,
            "teams_impacted": teams_impacted,
            "historical_incidents": hist_incidents,
            "risk_rating": "Critical (Revenue Impacting)" if "Commerce" in affected_capabilities or "Checkout" in service_name else "High"
        }
        trace.append("Architectural blast radius assessment finalized.")
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": explainability
        }


class DocumentQAAgent(BaseAgent):
    """
    General-purpose RAG agent.
    Retrieves relevant chunks from the vector store (uploaded Excel / CSV / Markdown)
    and synthesises an answer — either via LLM or a structured fallback that shows the
    raw retrieved evidence so the user always gets real data, never demo data.
    """

    def __init__(self):
        super().__init__(
            name="Document Q&A Agent",
            description="Answers questions by retrieving and synthesising content from uploaded documents (Excel sheets, CSVs, Markdown files)."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = [
            "Initializing Document Q&A Agent...",
            f"Performing semantic search across indexed documents for: '{query[:120]}'"
        ]

        # ── 1. Vector Store retrieval ──────────────────────────────────────
        matches = self.vector_store.similarity_search(
            # `repository` is present on every ZIP-imported chunk, including uploads
            # made before the explicit origin marker was introduced.
            query, k=8, metadata_filter={"repository": {"$ne": ""}}
        )
        trace.append(f"Retrieved {len(matches)} candidate chunks from uploaded files only.")

        relevant = [m for m in matches if m["score"] > 0.0]

        # ── 2. Build context for LLM / fallback ───────────────────────────
        context_blocks: List[str] = []
        documents_consulted: List[str] = []
        nodes_traversed: List[str] = []

        for m in relevant:
            src = m["metadata"].get("source", m["id"])
            sheet = m["metadata"].get("sheet", "")
            label = f"{src} ({sheet})" if sheet else src
            documents_consulted.append(label)
            nodes_traversed.append(f"Document:{src}")
            # Trim each chunk to avoid token overflow
            context_blocks.append(f"--- Source: {label} ---\n{m['text'][:3000]}")

        context_text = "\n\n".join(context_blocks)

        # ── 3. LLM synthesis (Gemini / OpenAI) ────────────────────────────
        if self.openai_client and context_text.strip():
            trace.append("Calling LLM to synthesise answer from retrieved document chunks...")
            system_prompt = (
                "You are a Document Q&A Agent for an engineering knowledge platform. "
                "You are given chunks of content retrieved only from user-uploaded documents (Excel sheets, CSVs, Markdown). "
                "Answer the user's question ONLY from the provided context. "
                "Be specific, reference sheet names and column values where relevant. "
                "Format your response as JSON with this schema:\n"
                "{\n"
                "  \"answer\": \"string (detailed answer)\",\n"
                "  \"key_findings\": [\"string\"],\n"
                "  \"source_references\": [\"string\"],\n"
                "  \"confidence\": \"High | Medium | Low\"\n"
                "}"
            )
            user_prompt = (
                f"User question: {query}\n\n"
                f"Retrieved document context:\n{context_text}"
            )
            llm_raw = self.call_llm(system_prompt, user_prompt)
            # Strip markdown code fences if LLM wraps in ```json
            llm_raw = llm_raw.strip()
            if llm_raw.startswith("```"):
                llm_raw = "\n".join(llm_raw.split("\n")[1:])
                if llm_raw.endswith("```"):
                    llm_raw = llm_raw[: llm_raw.rfind("```")]
            try:
                result = json.loads(llm_raw)
                trace.append("LLM synthesis completed successfully.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": {
                        "why_chosen": f"Retrieved {len(relevant)} document chunks matching the query and synthesised via LLM.",
                        "nodes_traversed": nodes_traversed[:10],
                        "documents_consulted": documents_consulted[:8],
                        "similar_requirements": [],
                        "confidence_score": 88,
                        "contributing_agents": [self.name],
                    },
                }
            except Exception as parse_err:
                trace.append(f"LLM returned non-JSON response. Using raw text as answer. ({parse_err})")
                result = {
                    "answer": llm_raw,
                    "key_findings": [],
                    "source_references": documents_consulted[:5],
                    "confidence": "Medium",
                }
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": {
                        "why_chosen": "LLM produced a text answer from the retrieved document chunks.",
                        "nodes_traversed": nodes_traversed[:10],
                        "documents_consulted": documents_consulted[:8],
                        "similar_requirements": [],
                        "confidence_score": 75,
                        "contributing_agents": [self.name],
                    },
                }

        # ── 4. Fallback: return raw retrieved chunks clearly labelled ──────
        trace.append("No LLM configured. Returning raw retrieved document excerpts as structured answer.")

        if not relevant:
            answer = (
                "No relevant content was found in the uploaded files for this query. "
                "No demo data or inferred workflow has been used. Try using the wording from the source file, "
                "or upload the file that contains this feature."
            )
            key_findings: List[str] = []
        else:
            findings: List[str] = []
            for m in relevant[:5]:
                src = m["metadata"].get("source", m["id"])
                sheet = m["metadata"].get("sheet", "")
                label = f"{src} ({sheet})" if sheet else src
                # Show first meaningful lines of the chunk
                lines = [l.strip() for l in m["text"].split("\n") if l.strip()][:10]
                excerpt = " | ".join(lines)
                findings.append(f"[{label}]: {excerpt}")
            answer = (
                f"Found {len(relevant)} relevant sections in your uploaded documents. "
                "Configure a Gemini or OpenAI API key (GEMINI_API_KEY or OPENAI_API_KEY) "
                "in your Render environment variables to get an AI-synthesised answer. "
                "Raw retrieved evidence is shown in key_findings below."
            )
            key_findings = findings

        result = {
            "answer": answer,
            "key_findings": key_findings,
            "source_references": documents_consulted[:8],
            "confidence": "Low (no LLM configured)" if not self.openai_client else "Medium",
        }
        return {
            "agent_name": self.name,
            "trace": trace,
            "result": result,
            "explainability": {
                "why_chosen": "Document Q&A Agent selected because query requires content from uploaded files.",
                "nodes_traversed": nodes_traversed[:10],
                "documents_consulted": documents_consulted[:8],
                "similar_requirements": [],
                "confidence_score": 60,
                "contributing_agents": [self.name],
            },
        }
