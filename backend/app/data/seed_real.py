import logging
from ..graph import get_graph_driver
from ..vectorstore import get_vector_store

logger = logging.getLogger(__name__)

def seed_real_architecture():
    """
    Populates Neo4j with real architecture mapped directly to Pavan Kumar H's 
    public GitHub repositories and connected to Freshservice incidents.
    """
    graph = get_graph_driver()
    vector_store = get_vector_store()

    logger.info("Clearing existing database before seeding real architecture...")
    graph.clear()
    vector_store.clear()

    # 1. Seed Teams
    teams = [
        {"name": "Core Platform & Analytics Team", "description": "Builds living ontology, repository analytics, and developer intelligence tooling."},
        {"name": "Reliability & Observability Team", "description": "Manages system telemetry, health guardian monitors, and incident alerting."},
        {"name": "DevOps & QA Automation Team", "description": "Orchestrates CI/CD pipelines, end-to-end Playwright automation, and release quality gates."},
        {"name": "Communications & Integrations Team", "description": "Handles notification routing, messaging channels (Beacon), and IT service desk hooks."},
        {"name": "Product & Growth Team", "description": "Develops agile sprint planning, market radar analytics, and user interfaces."}
    ]
    for team in teams:
        graph.add_node("Team", team)
    logger.info("Seeded 5 Teams.")

    # 2. Seed Engineers
    engineers = [
        {"name": "Pavan Kumar H", "email": "pavankumarh14@github.com", "role": "Principal Systems Architect", "github": "pavankumarh14", "team": "Core Platform & Analytics Team"},
        {"name": "Sarah Chen", "email": "sarah.chen@company.com", "role": "Lead SRE", "github": "sarahchen-sre", "team": "Reliability & Observability Team"},
        {"name": "Alex Rivera", "email": "alex.rivera@company.com", "role": "Senior QA Automation Engineer", "github": "arivera-qa", "team": "DevOps & QA Automation Team"},
        {"name": "Maya Patel", "email": "maya.patel@company.com", "role": "Staff Backend Engineer", "github": "mpatel-dev", "team": "Communications & Integrations Team"},
        {"name": "Marcus Vance", "email": "marcus.vance@company.com", "role": "Fullstack Product Engineer", "github": "mvance-code", "team": "Product & Growth Team"},
        {"name": "Elena Rostova", "email": "elena.r@company.com", "role": "Data & ML Engineer", "github": "erostova", "team": "Product & Growth Team"},
        {"name": "Devon Miller", "email": "devon.m@company.com", "role": "DevOps Engineer", "github": "devonm-ops", "team": "DevOps & QA Automation Team"},
        {"name": "Liam Connor", "email": "liam.c@company.com", "role": "Cloud Platform Engineer", "github": "lconnor", "team": "Core Platform & Analytics Team"}
    ]
    for eng in engineers:
        graph.add_node("Engineer", {k: v for k, v in eng.items() if k != "team"})
        graph.add_relationship("Engineer", eng["name"], "Team", eng["team"], "MEMBER_OF")
    logger.info("Seeded 8 Engineers and Team memberships.")

    # 3. Seed Services (Mapped to Real GitHub Repositories)
    services = [
        {
            "name": "Health Monitoring Service",
            "purpose": "Monitors microservice health signals, cluster anomalies, and telemetry metrics.",
            "capability": "Observability",
            "failure_impact": "Loss of infrastructure telemetry and degraded anomaly detection.",
            "risk_level": "High",
            "team": "Reliability & Observability Team"
        },
        {
            "name": "Alerting Service",
            "purpose": "Dispatches critical operational alerts, pager escalation, and incident webhooks.",
            "capability": "Observability",
            "failure_impact": "Engineers are not notified during production outages.",
            "risk_level": "High",
            "team": "Reliability & Observability Team"
        },
        {
            "name": "Notification Service",
            "purpose": "Multi-channel notification dispatcher supporting Email, SMS, Webhooks, and Freshservice.",
            "capability": "Communications",
            "failure_impact": "Transactional emails and alert delivery fail to send.",
            "risk_level": "Medium",
            "team": "Communications & Integrations Team"
        },
        {
            "name": "Project Management Service",
            "purpose": "Manages agile sprints, story point burn-down velocity, and developer task assignment.",
            "capability": "Productivity",
            "failure_impact": "Sprint planning dashboards and board metrics unavailable.",
            "risk_level": "Low",
            "team": "Product & Growth Team"
        },
        {
            "name": "QA Automation Service",
            "purpose": "Executes end-to-end browser regression suites with Playwright across staging environments.",
            "capability": "Quality Assurance",
            "failure_impact": "Deployment gates block release candidate promotions.",
            "risk_level": "Medium",
            "team": "DevOps & QA Automation Team"
        },
        {
            "name": "Documentation Service",
            "purpose": "Centralizes markdown knowledge bases, API specifications, and interactive runbooks.",
            "capability": "Core Platform",
            "failure_impact": "Developers cannot search onboarding guides or API contracts.",
            "risk_level": "Low",
            "team": "Core Platform & Analytics Team"
        },
        {
            "name": "Frontend App",
            "purpose": "Customer-facing web portal for user accounts, checkout workflows, and profile dashboards.",
            "capability": "User Experience",
            "failure_impact": "Users experience 500 error pages and cannot browse the portal.",
            "risk_level": "High",
            "team": "Product & Growth Team"
        },
        {
            "name": "Market Intelligence Service",
            "purpose": "Aggregates competitive metrics, ticker trends, and financial market insights.",
            "capability": "Analytics",
            "failure_impact": "Market analytics reports and data feeds are stale.",
            "risk_level": "Low",
            "team": "Product & Growth Team"
        },
        {
            "name": "Funding Platform",
            "purpose": "Coordinates investor pledges, portfolio tracking, and grant allocation workflows.",
            "capability": "Fintech",
            "failure_impact": "Campaign disbursements and fundraising transactions blocked.",
            "risk_level": "Medium",
            "team": "Product & Growth Team"
        },
        {
            "name": "Core Platform & Analytics",
            "purpose": "Living knowledge graph platform orchestrating AI agents, repository intake, and incident triage.",
            "capability": "Developer Intelligence",
            "failure_impact": "Impact analysis and automated incident RCA unavailable.",
            "risk_level": "High",
            "team": "Core Platform & Analytics Team"
        },
        {
            "name": "Payment Gateway Service",
            "purpose": "Processes merchant credit card billing, wallet debits, and external payment gateway webhooks.",
            "capability": "Fintech",
            "failure_impact": "Customers experience payment failures and checkout order drop-offs.",
            "risk_level": "Critical",
            "team": "Communications & Integrations Team"
        }
    ]

    for svc in services:
        team_name = svc["team"]
        svc_node = {k: v for k, v in svc.items() if k != "team"}
        graph.add_node("Service", svc_node)
        graph.add_relationship("Team", team_name, "Service", svc["name"], "OWNS")

        vector_store.add_texts(
            texts=[f"Service: {svc['name']}. Purpose: {svc['purpose']}. Capability: {svc['capability']}. Risk: {svc['risk_level']}"],
            metadatas=[{"type": "Service", "name": svc["name"], "origin": "real"}],
            ids=[f"service-{svc['name'].lower().replace(' ', '-')[:30]}"]
        )
    logger.info("Seeded 11 Services and Team ownership.")

    # 4. Seed Real Repositories (Mapped to Pavan Kumar H's GitHub Repos)
    repos = [
        {
            "name": "DataHub-Health-Guardian",
            "url": "https://github.com/pavankumarh14/DataHub-Health-Guardian",
            "languages": "Python, Shell",
            "service": "Health Monitoring Service",
            "owner": "Pavan Kumar H"
        },
        {
            "name": "PulseCommand-AI",
            "url": "https://github.com/pavankumarh14/PulseCommand-AI",
            "languages": "TypeScript, Python",
            "service": "Alerting Service",
            "owner": "Sarah Chen"
        },
        {
            "name": "Beacon",
            "url": "https://github.com/pavankumarh14/Beacon",
            "languages": "Go, Python",
            "service": "Notification Service",
            "owner": "Maya Patel"
        },
        {
            "name": "SprintPilot",
            "url": "https://github.com/pavankumarh14/SprintPilot",
            "languages": "TypeScript, React",
            "service": "Project Management Service",
            "owner": "Marcus Vance"
        },
        {
            "name": "EndToEndPlayWrightAutomationTool",
            "url": "https://github.com/pavankumarh14/EndToEndPlayWrightAutomationTool",
            "languages": "TypeScript, JavaScript",
            "service": "QA Automation Service",
            "owner": "Alex Rivera"
        },
        {
            "name": "DocAnchor",
            "url": "https://github.com/pavankumarh14/DocAnchor",
            "languages": "Python, Markdown",
            "service": "Documentation Service",
            "owner": "Pavan Kumar H"
        },
        {
            "name": "UrbanNexus",
            "url": "https://github.com/pavankumarh14/UrbanNexus",
            "languages": "TypeScript, CSS, HTML",
            "service": "Frontend App",
            "owner": "Marcus Vance"
        },
        {
            "name": "MarketRadar",
            "url": "https://github.com/pavankumarh14/MarketRadar",
            "languages": "Python, R",
            "service": "Market Intelligence Service",
            "owner": "Elena Rostova"
        },
        {
            "name": "FunderAI",
            "url": "https://github.com/pavankumarh14/FunderAI",
            "languages": "Python, Next.js",
            "service": "Funding Platform",
            "owner": "Elena Rostova"
        },
        {
            "name": "CodeAtlas-AI",
            "url": "https://github.com/pavankumarh14/CodeAtlas-AI",
            "languages": "Python, TypeScript, CSS",
            "service": "Core Platform & Analytics",
            "owner": "Pavan Kumar H"
        },
        {
            "name": "payment-gateway",
            "url": "https://github.com/pavankumarh14/payment-gateway",
            "languages": "Python, FastAPI",
            "service": "Payment Gateway Service",
            "owner": "Maya Patel"
        }
    ]

    for repo in repos:
        svc_name = repo["service"]
        owner_name = repo["owner"]
        repo_node = {k: v for k, v in repo.items() if k not in ("service", "owner")}
        graph.add_node("Repository", repo_node)
        graph.add_relationship("Repository", repo["name"], "Service", svc_name, "IMPLEMENTS")
        graph.add_relationship("Engineer", owner_name, "Repository", repo["name"], "WORKED_ON")
        # Also link Pavan Kumar H as contributor to key repos
        if owner_name != "Pavan Kumar H":
            graph.add_relationship("Engineer", "Pavan Kumar H", "Repository", repo["name"], "WORKED_ON")
    logger.info("Seeded 11 Repositories and linked IMPLEMENTS & WORKED_ON.")

    # 5. Seed APIs for Services
    apis = [
        ("GET", "/api/v1/health/metrics", "Polls node telemetry and active cluster heartbeat.", "Health Monitoring Service"),
        ("POST", "/api/v1/health/checks/execute", "Triggers immediate synthetic health verification probe.", "Health Monitoring Service"),
        ("POST", "/api/v1/alerts/trigger", "Publishes an operational alert to on-call schedules.", "Alerting Service"),
        ("GET", "/api/v1/alerts/active", "Lists unresolved active alerts with severity levels.", "Alerting Service"),
        ("POST", "/api/v1/notifications/send", "Dispatches transactional emails or SMS broadcasts.", "Notification Service"),
        ("POST", "/api/v1/notifications/email/relay", "SMTP relay handler for outbound corporate email messages.", "Notification Service"),
        ("GET", "/api/v1/sprints/active/velocity", "Computes current sprint velocity and burndown forecast.", "Project Management Service"),
        ("POST", "/api/v1/qa/test-runs/trigger", "Dispatches headless Playwright end-to-end regression tests.", "QA Automation Service"),
        ("GET", "/api/v1/docs/search", "Executes semantic query across indexed service documentation.", "Documentation Service"),
        ("GET", "/api/v1/portal/user/profile", "Fetches authenticated user preferences and account status.", "Frontend App"),
        ("POST", "/api/v1/portal/auth/login", "Authenticates user session tokens with MFA challenge.", "Frontend App"),
        ("GET", "/api/v1/market/tickers/summary", "Yields consolidated ticker updates and sentiment scoring.", "Market Intelligence Service"),
        ("POST", "/api/v1/funding/campaigns/pledge", "Registers investor pledge towards active campaign round.", "Funding Platform"),
        ("POST", "/api/v1/payments/charge", "Initiates credit card authorization and gateway settlement.", "Payment Gateway Service"),
        ("GET", "/api/v1/payments/pool/status", "Inspects PostgreSQL database connection pool health.", "Payment Gateway Service")
    ]

    for method, path, desc, svc in apis:
        api_name = f"{method} {path}"
        graph.add_node("API", {
            "name": api_name,
            "method": method,
            "path": path,
            "description": desc,
            "service_name": svc
        })
        graph.add_relationship("API", api_name, "Service", svc, "EXPOSES")
    logger.info(f"Seeded {len(apis)} APIs.")

    # 6. Seed Requirements
    requirements = [
        {
            "req_id": "REQ-101",
            "title": "Real-time Telemetry Ingestion for DataHub",
            "description": "Stream cluster node metrics via WebSockets with < 500ms latency to Health Monitoring Service.",
            "priority": "High",
            "status": "Implemented",
            "service": "Health Monitoring Service",
            "engineer": "Pavan Kumar H"
        },
        {
            "req_id": "REQ-102",
            "title": "Smart Escalation Webhooks in PulseCommand",
            "description": "Auto-escalate alerts to on-call Slack channel if unacknowledged after 5 minutes.",
            "priority": "High",
            "status": "Implemented",
            "service": "Alerting Service",
            "engineer": "Sarah Chen"
        },
        {
            "req_id": "REQ-103",
            "title": "Freshservice Ticket Sync & Email Dispatch",
            "description": "Ensure Beacon Notification Service reliably relays transactional ticket emails without dropped SMTP connections.",
            "priority": "Critical",
            "status": "In Progress",
            "service": "Notification Service",
            "engineer": "Maya Patel"
        },
        {
            "req_id": "REQ-104",
            "title": "Automated Sprint Burndown Forecast",
            "description": "Calculate story point trajectory based on historical velocity in SprintPilot.",
            "priority": "Medium",
            "status": "Implemented",
            "service": "Project Management Service",
            "engineer": "Marcus Vance"
        },
        {
            "req_id": "REQ-105",
            "title": "Playwright CI Pipeline Timeout Safeguard",
            "description": "Implement circuit breaker and 60-second timeout per browser test in EndToEndPlayWrightAutomationTool.",
            "priority": "High",
            "status": "In Progress",
            "service": "QA Automation Service",
            "engineer": "Alex Rivera"
        },
        {
            "req_id": "REQ-106",
            "title": "Instant Markdown Runbook Search",
            "description": "Semantic vector search for engineering playbooks and architectural documentation in DocAnchor.",
            "priority": "Medium",
            "status": "Implemented",
            "service": "Documentation Service",
            "engineer": "Pavan Kumar H"
        },
        {
            "req_id": "REQ-107",
            "title": "Frontend App Resilient Error Boundary",
            "description": "Catch unhandled react rendering errors and render friendly fallback page instead of 500 error in UrbanNexus.",
            "priority": "High",
            "status": "Proposed",
            "service": "Frontend App",
            "engineer": "Marcus Vance"
        },
        {
            "req_id": "REQ-108",
            "title": "Payment Gateway Connection Pool Resiliency",
            "description": "Increase maximum pool size to 100 connections and add connection leak detector to prevent pool exhaustion.",
            "priority": "Critical",
            "status": "In Progress",
            "service": "Payment Gateway Service",
            "engineer": "Pavan Kumar H"
        },
        {
            "req_id": "REQ-109",
            "title": "Market Radar Historical Trends Caching",
            "description": "Cache computed ticker alpha signals in Redis for 10 minutes to minimize API rate limits.",
            "priority": "Medium",
            "status": "Implemented",
            "service": "Market Intelligence Service",
            "engineer": "Elena Rostova"
        }
    ]

    for req in requirements:
        svc_name = req["service"]
        eng_name = req["engineer"]
        req_node = {k: v for k, v in req.items() if k not in ("service", "engineer")}
        graph.add_node("Requirement", req_node)
        graph.add_relationship("Requirement", req["req_id"], "Service", svc_name, "AFFECTS")
        graph.add_relationship("Engineer", eng_name, "Requirement", req["req_id"], "CREATED")

        vector_store.add_texts(
            texts=[f"Requirement {req['req_id']}: {req['title']}. Details: {req['description']}. Target Service: {svc_name}"],
            metadatas=[{"type": "Requirement", "id": req["req_id"], "origin": "real"}],
            ids=[f"req-{req['req_id'].lower()}"]
        )
    logger.info(f"Seeded {len(requirements)} Requirements.")

    # 7. Seed Service Dependencies
    service_dependencies = [
        ("Frontend App", "Payment Gateway Service"),
        ("Frontend App", "Notification Service"),
        ("Frontend App", "Documentation Service"),
        ("Frontend App", "Market Intelligence Service"),
        ("Health Monitoring Service", "Alerting Service"),
        ("Alerting Service", "Notification Service"),
        ("QA Automation Service", "Frontend App"),
        ("QA Automation Service", "Health Monitoring Service"),
        ("Project Management Service", "Notification Service"),
        ("Funding Platform", "Payment Gateway Service"),
        ("Funding Platform", "Market Intelligence Service"),
        ("Core Platform & Analytics", "Health Monitoring Service"),
        ("Core Platform & Analytics", "Documentation Service")
    ]

    for src, tgt in service_dependencies:
        graph.add_relationship("Service", src, "Service", tgt, "DEPENDS_ON")
    logger.info(f"Seeded {len(service_dependencies)} Service Dependencies.")

    # 8. Seed Runbooks & Technical Documentation
    runbooks = [
        {
            "title": "Payment Gateway Connection Pool Runbook",
            "type": "Runbook",
            "content": "Steps to resolve database connection exhaustion: 1. Check active client connections in PostgreSQL. 2. Scale max_connections. 3. Restart idle pool threads. 4. Verify checkout endpoint latencies.",
            "service": "Payment Gateway Service"
        },
        {
            "title": "Beacon Email & Alert Relay Troubleshooting",
            "type": "Runbook",
            "content": "When users report 'cannot send email' or delayed notifications: 1. Inspect SMTP queue depth in Beacon. 2. Check Freshservice webhook connectivity. 3. Verify rate limits on email relay gateway.",
            "service": "Notification Service"
        },
        {
            "title": "DataHub Cluster Telemetry Failure Guide",
            "type": "Runbook",
            "content": "Troubleshooting missing health alerts: 1. Restart telemetry daemon. 2. Inspect PulseCommand ingestion latency. 3. Verify node agent socket connectivity.",
            "service": "Health Monitoring Service"
        },
        {
            "title": "Playwright QA Automation Triage Playbook",
            "type": "Runbook",
            "content": "Handling CI test timeouts: 1. Check headless Chromium memory consumption. 2. Verify staging environment URL availability. 3. Re-run failed spec with trace viewer enabled.",
            "service": "QA Automation Service"
        }
    ]

    for doc in runbooks:
        node_label = doc["type"]
        graph.add_node(node_label, {"title": doc["title"], "content": doc["content"]})
        graph.add_relationship(node_label, doc["title"], "Service", doc["service"], "DOCUMENTED_BY")

        vector_store.add_texts(
            texts=[f"{doc['type']}: {doc['title']}. Content: {doc['content']}. Service: {doc['service']}"],
            metadatas=[{"type": doc["type"], "title": doc["title"], "origin": "real"}],
            ids=[f"doc-{doc['title'].lower().replace(' ', '-')[:30]}"]
        )
    logger.info("Seeded 4 Runbooks & Engineering Documents.")

    logger.info("Custom Real Architecture seeded successfully into Neo4j!")
    return {
        "status": "success",
        "teams": len(teams),
        "engineers": len(engineers),
        "services": len(services),
        "repositories": len(repos),
        "apis": len(apis),
        "requirements": len(requirements),
        "runbooks": len(runbooks),
        "message": "Custom architecture mapped to Pavan Kumar H's GitHub repositories populated successfully!"
    }
