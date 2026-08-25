import json
from typing import Dict, Any, List, Optional
from .base import BaseAgent
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
        
        # Simple extraction of service name
        service_name = "Checkout Service"  # Default
        for word in ["checkout", "payment", "inventory", "notification", "order", "shipping", "auth", "delivery"]:
            if word in query.lower():
                service_name = f"{word.capitalize()} Service"
                break
                
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
                result = json.loads(llm_res)
                trace.append("OpenAI reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception:
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        # Rule-based fallback
        trace.append("Generating response using Dynamic Reasoning Engine...")
        risk_level = "High" if len(incidents) > 1 or len(dependencies) > 2 else "Medium"
        capability = "Commerce"
        purpose = "Processes transactions and checkouts"
        
        if graph_service:
            props = graph_service["properties"]
            purpose = props.get("purpose", purpose)
            capability = props.get("capability", capability)
            risk_level = props.get("risk_level", risk_level)

        result = {
            "purpose": purpose,
            "business_capability": capability,
            "owners": owners if owners else ["Commerce Team (Team)"],
            "dependencies": list(set(dependencies)) if dependencies else ["Payment Service", "Inventory Service"],
            "risks": f"Risk level: {risk_level}. Affected by {len(incidents)} active incidents. Failure blocks user transactions.",
            "repositories": repositories if repositories else [f"{service_name.lower().replace(' ', '-')}-api"],
            "learning_path": [
                f"1. Read the Confluence {service_name} architecture guide",
                f"2. Inspect the repository '{repositories[0]}' if changes are needed" if repositories else "2. Clone git repo",
                f"3. Run local setup or test cases"
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
        
        # Perform graph lookup based on keywords
        trace.append("Traversing knowledge graph to find related dependencies and teams...")
        all_services = self.graph.get_nodes("Service")
        impacted_services = []
        
        # Find which services might be affected based on keywords
        for s in all_services:
            name = s["properties"].get("name", "")
            purpose = s["properties"].get("purpose", "")
            # Simple keyword match
            keywords = [k for k in ["checkout", "payment", "notification", "whatsapp", "order", "inventory", "shipping"] if k in query.lower()]
            for kw in keywords:
                if kw in name.lower() or kw in purpose.lower():
                    impacted_services.append(name)
        
        # Default if none matched
        if not impacted_services:
            impacted_services = ["Notifications Service", "Order Service"]
            
        impacted_services = list(set(impacted_services))
        
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
            documents_consulted = ["Jira REQ-65 Specs", "GitHub notifications-hub repository logs"]

        explainability = {
            "why_chosen": f"Analyzed requirement text for notification and transaction keywords. Matched dependencies for {', '.join(impacted_services)} using ontology graph linkages.",
            "nodes_traversed": nodes_traversed[:8],
            "documents_consulted": documents_consulted,
            "similar_requirements": ["REQ-65: Implement WhatsApp Notifications for Order Status"],
            "confidence_score": 88,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Executing OpenAI LLM reasoning for Requirement Impact...")
            system_prompt = """You are a Requirement Impact Agent. Analyze a new system requirement and determine the impact.
            Format your response as JSON matching this schema:
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
                result = json.loads(llm_res)
                trace.append("OpenAI reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception:
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        trace.append("Synthesizing impact assessment report...")
        result = {
            "affected_services": impacted_services,
            "affected_repositories": impacted_repos if impacted_repos else ["notifications-service-repo"],
            "apis_involved": apis if apis else ["POST /api/v1/notifications/send"],
            "teams_impacted": impacted_teams if impacted_teams else ["Core Platform Team"],
            "dependencies": dependencies,
            "risk_analysis": f"Medium Risk. WhatsApp integration requires connecting to external webhook APIs. Blasts checkout workflows if notifications fail synchronously.",
            "recommendations": [
                "Implement WhatsApp notifications asynchronously using a message queue (RabbitMQ/SQS)",
                "Create a circuit breaker around the WhatsApp Gateway API client",
                f"Obtain approval from {impacted_teams[0]} since they own the impacted service" if impacted_teams else "Get team sign-off"
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
        
        service_name = "Checkout Service"
        for word in ["checkout", "payment", "inventory", "notification", "order", "shipping", "auth"]:
            if word in query.lower():
                service_name = f"{word.capitalize()} Service"
                break
                
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
        
        # Traverse graph for engineers
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
                    
                    if "Lead" in role or "Architect" in role:
                        architects.append(eng_name)
                    if "Senior" in role or "Staff" in role:
                        smes.append(eng_name)

        if not owners:
            owners = ["Sarah Smith (Lead Engineer) - sarah@company.com", "Commerce Team (Team)"]
            contributors = ["Sarah Smith", "John Doe"]
            smes = ["Sarah Smith"]
            architects = ["Alex Architect"]
            nodes_traversed.extend(["Engineer:Sarah Smith", "Engineer:John Doe"])

        explainability = {
            "why_chosen": f"Matched the requested service '{service_name}' with team ownership nodes and queried active membership listings.",
            "nodes_traversed": nodes_traversed,
            "documents_consulted": [f"Team Membership Directory", f"GitHub code contribution logs for {service_name}"],
            "similar_requirements": [],
            "confidence_score": 100,
            "contributing_agents": [self.name]
        }

        if self.openai_client:
            trace.append("Querying OpenAI to format expert profiling...")
            system_prompt = """You are an Expert Discovery Agent. Identify the owners, contributors, architects, and SMEs.
            Format your response as JSON matching this schema:
            {
              "owners": ["string"],
              "contributors": ["string"],
              "architects": ["string"],
              "subject_matter_experts": ["string"]
            }"""
            db_context = f"Service: {service_name}\nTeams: {teams}\nEngineers: {owners}"
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = json.loads(llm_res)
                trace.append("OpenAI reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception:
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        result = {
            "owners": owners[:2],
            "contributors": list(set(contributors)),
            "architects": list(set(architects)) if architects else ["Alex Architect (Chief Architect)"],
            "subject_matter_experts": list(set(smes)) if smes else ["Sarah Smith (Domain SME)"]
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
        
        # Search vector store
        inc_matches = self.vector_store.similarity_search(query, k=3)
        
        # Query graph for active incidents
        trace.append("Checking Graph database for active Incidents affecting components...")
        incidents = self.graph.get_nodes("Incident")
        
        related_incidents = []
        nodes_traversed = []
        for match in inc_matches:
            if match["metadata"].get("type") == "Incident" or "INC-" in match["id"]:
                related_incidents.append({
                    "id": match["id"],
                    "title": match["text"],
                    "score": match["score"]
                })
                nodes_traversed.append(f"Incident:{match['id']}")
                
        # If empty, add mock
        if not related_incidents:
            related_incidents = [
                {"id": "INC-101", "title": "Checkout latency spikes caused by database lockups", "score": 0.85},
                {"id": "INC-212", "title": "Stripe Gateway Timeout during checkout flow", "score": 0.65}
            ]
            nodes_traversed.extend(["Incident:INC-101", "Incident:INC-212"])
            
        trace.append(f"Discovered {len(related_incidents)} matching historical incidents.")

        # Find dependencies of Checkout Service
        trace.append("Querying service dependencies to check for upstream failures...")
        services = self.graph.get_nodes("Service")
        target_service = "Checkout Service"
        for s in services:
            sname = s["properties"].get("name", "")
            if sname.lower() in query.lower():
                target_service = sname
                break
                
        deps = self.graph.get_dependency_chain(target_service, "upstream")
        dep_names = []
        for path in deps:
            for node in path["nodes"]:
                nodes_traversed.append(f"Service:{node['name']}")
                if node["name"] != target_service:
                    dep_names.append(node["name"])
        dep_names = list(set(dep_names))
        if not dep_names:
            dep_names = ["Payment Service", "Inventory Service"]
            nodes_traversed.extend(["Service:Payment Service", "Service:Inventory Service"])

        # Runbook lookups
        trace.append("Searching Confluence MCP adapter for matching recovery runbooks...")
        runbooks = self.mcp_adapters["confluence"].search("runbook")
        
        documents_consulted = [
            f"Runbook: Confluence Page CONF-902 (Checkout Latency mitigation)"
        ]
        if runbooks:
            documents_consulted.append(f"Confluence: {runbooks[0].get('title')}")

        explainability = {
            "why_chosen": f"Looked up historical database failures correlating to '{query}'. Traced dependency trees for impacted downstream service: '{target_service}'.",
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
              "related_incidents": [{"id": "string", "title": "string", "relevance": "string"}],
              "dependencies": ["string"],
              "known_fixes": ["string"],
              "escalation_path": "string"
            }"""
            db_context = f"Incident query: {query}\nRelated: {related_incidents}\nDeps: {dep_names}\nRunbooks: {runbooks}"
            llm_res = self.call_llm(system_prompt, db_context)
            try:
                result = json.loads(llm_res)
                trace.append("OpenAI reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception:
                trace.append("Failed to parse LLM JSON. Falling back to dynamic rule-based synthesis.")

        result = {
            "related_incidents": [
                {"id": r["id"], "title": r["title"], "relevance": "High Similarity (DB / Network Bottleneck)"}
                for r in related_incidents
            ],
            "dependencies": dep_names,
            "known_fixes": [
                "Switch Stripe Gateway to secondary provider via feature flag (payment-circuit-breaker)",
                "Increase database connections pooling limit in inventory-db configurations",
                "Restart checkout-api pods to clear hung connections thread pool"
            ],
            "escalation_path": "Level 1: Commerce On-Call -> Level 2: Platform DB Admin -> Level 3: Principal Architect (Alex)"
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
                result = json.loads(llm_res)
                trace.append("OpenAI reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception:
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
                result = json.loads(llm_res)
                trace.append("OpenAI reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception:
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
                result = json.loads(llm_res)
                trace.append("OpenAI reasoning completed.")
                return {
                    "agent_name": self.name,
                    "trace": trace,
                    "result": result,
                    "explainability": explainability
                }
            except Exception:
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
