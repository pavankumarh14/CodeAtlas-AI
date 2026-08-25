import logging
from ..graph import get_graph_driver
from ..vectorstore import get_vector_store

logger = logging.getLogger(__name__)

def seed_all_data():
    graph = get_graph_driver()
    vector_store = get_vector_store()

    logger.info("Clearing databases before seeding...")
    graph.clear()
    vector_store.clear()

    # 1. Seed 5 Teams
    teams = [
        {"name": "Commerce Team", "description": "Responsible for checkouts, baskets, and payments workflows."},
        {"name": "Logistics Team", "description": "Handles fulfillment, shipping, tracking, and warehousing."},
        {"name": "Identity Team", "description": "Manages user login, authorization, registration, and profiles."},
        {"name": "Notifications Team", "description": "Orchestrates transactional emails, SMS, and WhatsApp alerts."},
        {"name": "Core Platform Team", "description": "Maintains developer platforms, databases, cache layers, and base APIs."}
    ]
    for team in teams:
        graph.add_node("Team", team)
    logger.info("Seeded 5 Teams.")

    # 2. Seed 25 Engineers
    engineers = [
        {"name": "Sarah Smith", "email": "sarah.smith@company.com", "role": "Lead Engineer", "github": "sarahsmith-dev", "team": "Commerce Team"},
        {"name": "John Doe", "email": "john.doe@company.com", "role": "Senior Engineer", "github": "johndoe-code", "team": "Commerce Team"},
        {"name": "David Miller", "email": "david.miller@company.com", "role": "Engineer", "github": "davidm-dev", "team": "Commerce Team"},
        {"name": "Emma Jones", "email": "emma.jones@company.com", "role": "Engineer", "github": "emma-jones", "team": "Notifications Team"},
        {"name": "Alex Architect", "email": "alex.architect@company.com", "role": "Principal Architect", "github": "alex-arch", "team": "Core Platform Team"},
        {"name": "Sam Reliability", "email": "sam.reliability@company.com", "role": "Site Reliability Engineer", "github": "sam-sre", "team": "Core Platform Team"},
        {"name": "Michael Brown", "email": "michael.brown@company.com", "role": "Lead Engineer", "github": "michael-brown", "team": "Logistics Team"},
        {"name": "Jessica Davis", "email": "jessica.davis@company.com", "role": "Senior Engineer", "github": "jessica-code", "team": "Logistics Team"},
        {"name": "Daniel Wilson", "email": "daniel.wilson@company.com", "role": "Engineer", "github": "danielw", "team": "Logistics Team"},
        {"name": "James Taylor", "email": "james.taylor@company.com", "role": "Engineer", "github": "jamestaylor", "team": "Logistics Team"},
        {"name": "Emily Thomas", "email": "emily.thomas@company.com", "role": "Lead Engineer", "github": "emily-t", "team": "Identity Team"},
        {"name": "Matthew Jackson", "email": "matthew.jackson@company.com", "role": "Senior Engineer", "github": "matthew-j", "team": "Identity Team"},
        {"name": "Olivia White", "email": "olivia.white@company.com", "role": "Engineer", "github": "olivia-white", "team": "Identity Team"},
        {"name": "Andrew Harris", "email": "andrew.harris@company.com", "role": "Engineer", "github": "andrewh", "team": "Identity Team"},
        {"name": "Sophia Martin", "email": "sophia.martin@company.com", "role": "Engineer", "github": "sophia-m", "team": "Notifications Team"},
        {"name": "Joshua Garcia", "email": "joshua.garcia@company.com", "role": "Engineer", "github": "joshua-g", "team": "Notifications Team"},
        {"name": "Isabella Martinez", "email": "isabella.martinez@company.com", "role": "Engineer", "github": "isabella-m", "team": "Notifications Team"},
        {"name": "Christopher Clark", "email": "christopher.clark@company.com", "role": "Senior Engineer", "github": "chris-clark", "team": "Core Platform Team"},
        {"name": "Mia Rodriguez", "email": "mia.rodriguez@company.com", "role": "Engineer", "github": "mia-r", "team": "Core Platform Team"},
        {"name": "Ryan Lewis", "email": "ryan.lewis@company.com", "role": "Engineer", "github": "ryan-lewis", "team": "Core Platform Team"},
        {"name": "Charlotte Lee", "email": "charlotte.lee@company.com", "role": "Engineer", "github": "charlotte-lee", "team": "Commerce Team"},
        {"name": "Joseph Walker", "email": "joseph.walker@company.com", "role": "Engineer", "github": "josephw", "team": "Commerce Team"},
        {"name": "Abigail Hall", "email": "abigail.hall@company.com", "role": "Engineer", "github": "abigail-hall", "team": "Logistics Team"},
        {"name": "William Allen", "email": "william.allen@company.com", "role": "Engineer", "github": "william-allen", "team": "Logistics Team"},
        {"name": "Elizabeth Young", "email": "elizabeth.young@company.com", "role": "Engineer", "github": "elizabethy", "team": "Identity Team"}
    ]
    for eng in engineers:
        graph.add_node("Engineer", {k: v for k, v in eng.items() if k != "team"})
        # Link Engineer -> MEMBER_OF -> Team
        graph.add_relationship("Engineer", eng["name"], "Team", eng["team"], "MEMBER_OF")
    logger.info("Seeded 25 Engineers and Team membership relationships.")

    # 3. Seed 20 Services
    services = [
        {"name": "Checkout Service", "purpose": "Handles customer cart checkout transactions.", "capability": "Commerce", "failure_impact": "Blocks all orders and generates revenue loss.", "risk_level": "High"},
        {"name": "Payment Service", "purpose": "Coordinates secure credit card billing via external gateways.", "capability": "Commerce", "failure_impact": "Customers cannot pay for orders.", "risk_level": "High"},
        {"name": "Inventory Service", "purpose": "Tracks stock levels and product catalog availability.", "capability": "Commerce", "failure_impact": "Items could be oversold.", "risk_level": "Medium"},
        {"name": "Order Service", "purpose": "Manages order lifecycle from creation to delivery.", "capability": "Commerce", "failure_impact": "Orders are stuck in pending state.", "risk_level": "High"},
        {"name": "Cart Service", "purpose": "Saves customer baskets before checkout.", "capability": "Commerce", "failure_impact": "Users cannot add items to cart.", "risk_level": "Medium"},
        {"name": "Notifications Service", "purpose": "Triggers email, SMS, and WhatsApp status notifications.", "capability": "Notifications", "failure_impact": "Customers don't receive purchase confirmations.", "risk_level": "Medium"},
        {"name": "Auth Service", "purpose": "Provides user login token generation and signups.", "capability": "Identity", "failure_impact": "Users cannot sign in.", "risk_level": "High"},
        {"name": "User Service", "purpose": "Manages customer profile settings and shipping addresses.", "capability": "Identity", "failure_impact": "Addresses cannot be validated.", "risk_level": "Low"},
        {"name": "Catalog Service", "purpose": "Hosts inventory lookup directories.", "capability": "Commerce", "failure_impact": "Product search fails.", "risk_level": "Medium"},
        {"name": "Search Service", "purpose": "Indexes products for customer queries.", "capability": "Commerce", "failure_impact": "Product listings return empty.", "risk_level": "Medium"},
        {"name": "Shipping Service", "purpose": "Interfaces with USPS, FedEx, and DHL.", "capability": "Logistics", "failure_impact": "Shipping labels cannot be printed.", "risk_level": "High"},
        {"name": "Shipping Rate Service", "purpose": "Calculates package rates dynamically.", "capability": "Logistics", "failure_impact": "Cart shipping calculations fail.", "risk_level": "Low"},
        {"name": "Tracking Service", "purpose": "Monitors active package locations.", "capability": "Logistics", "failure_impact": "Tracking pages render errors.", "risk_level": "Low"},
        {"name": "Warehouse Service", "purpose": "Manages barcode scanning and stock fulfillment.", "capability": "Logistics", "failure_impact": "Warehouse items cannot be picked.", "risk_level": "High"},
        {"name": "Billing Service", "purpose": "Issues invoices and ledger entries.", "capability": "Commerce", "failure_impact": "Invoices are delayed.", "risk_level": "Low"},
        {"name": "Reporting Service", "purpose": "Prepares sales aggregations for business leads.", "capability": "Commerce", "failure_impact": "Sales dashboards are outdated.", "risk_level": "Low"},
        {"name": "Analytics Service", "purpose": "Tracks user clickstream events.", "capability": "Core Platform", "failure_impact": "Marketing analytics are missing.", "risk_level": "Low"},
        {"name": "Auditing Service", "purpose": "Maintains log trails for compliance.", "capability": "Core Platform", "failure_impact": "SLA reports are missing.", "risk_level": "Low"},
        {"name": "Recommendation Service", "purpose": "Generates recommended items on checkout pages.", "capability": "Commerce", "failure_impact": "Checkout pages load slower.", "risk_level": "Low"},
        {"name": "Reviews Service", "purpose": "Accepts customer feedback ratings.", "capability": "Commerce", "failure_impact": "Reviews do not load.", "risk_level": "Low"}
    ]
    
    # Map teams to services for ownership link
    service_team_map = {
        "Checkout Service": "Commerce Team",
        "Payment Service": "Commerce Team",
        "Inventory Service": "Commerce Team",
        "Order Service": "Commerce Team",
        "Cart Service": "Commerce Team",
        "Catalog Service": "Commerce Team",
        "Search Service": "Commerce Team",
        "Billing Service": "Commerce Team",
        "Reporting Service": "Commerce Team",
        "Recommendation Service": "Commerce Team",
        "Reviews Service": "Commerce Team",
        "Notifications Service": "Notifications Team",
        "Auth Service": "Identity Team",
        "User Service": "Identity Team",
        "Shipping Service": "Logistics Team",
        "Shipping Rate Service": "Logistics Team",
        "Tracking Service": "Logistics Team",
        "Warehouse Service": "Logistics Team",
        "Analytics Service": "Core Platform Team",
        "Auditing Service": "Core Platform Team"
    }

    for svc in services:
        graph.add_node("Service", svc)
        
        # Link Team -> OWNS -> Service
        tname = service_team_map.get(svc["name"])
        if tname:
            graph.add_relationship("Team", tname, "Service", svc["name"], "OWNS")
            
        # Add to vector store for semantic search
        vector_store.add_texts(
            texts=[f"Service Name: {svc['name']}. Purpose: {svc['purpose']}. Business Capability: {svc['capability']}. Risk Level: {svc['risk_level']}."],
            metadatas=[{"type": "Service", "name": svc["name"]}],
            ids=[f"service-{svc['name'].lower().replace(' ', '-')}"]
        )
    logger.info("Seeded 20 Services and Team-owns-Service relationships.")

    # 4. Seed 20 Repositories
    repos = [
        {"name": "checkout-api", "url": "git@github.com:org/checkout-api.git", "language": "TypeScript", "service": "Checkout Service"},
        {"name": "payment-gateway", "url": "git@github.com:org/payment-gateway.git", "language": "Python", "service": "Payment Service"},
        {"name": "inventory-service", "url": "git@github.com:org/inventory-service.git", "language": "Go", "service": "Inventory Service"},
        {"name": "order-processor", "url": "git@github.com:org/order-processor.git", "language": "TypeScript", "service": "Order Service"},
        {"name": "cart-api", "url": "git@github.com:org/cart-api.git", "language": "JavaScript", "service": "Cart Service"},
        {"name": "notifications-hub", "url": "git@github.com:org/notifications-hub.git", "language": "Python", "service": "Notifications Service"},
        {"name": "auth-server", "url": "git@github.com:org/auth-server.git", "language": "Go", "service": "Auth Service"},
        {"name": "user-profiles", "url": "git@github.com:org/user-profiles.git", "language": "Python", "service": "User Service"},
        {"name": "catalog-db-sync", "url": "git@github.com:org/catalog-db-sync.git", "language": "Go", "service": "Catalog Service"},
        {"name": "search-indexer", "url": "git@github.com:org/search-indexer.git", "language": "Scala", "service": "Search Service"},
        {"name": "shipping-orchestrator", "url": "git@github.com:org/shipping-orchestrator.git", "language": "Go", "service": "Shipping Service"},
        {"name": "rate-calculator", "url": "git@github.com:org/rate-calculator.git", "language": "Ruby", "service": "Shipping Rate Service"},
        {"name": "tracking-publisher", "url": "git@github.com:org/tracking-publisher.git", "language": "TypeScript", "service": "Tracking Service"},
        {"name": "warehouse-scanner", "url": "git@github.com:org/warehouse-scanner.git", "language": "Java", "service": "Warehouse Service"},
        {"name": "billing-ledger", "url": "git@github.com:org/billing-ledger.git", "language": "C#", "service": "Billing Service"},
        {"name": "reporting-aggregation", "url": "git@github.com:org/reporting-aggregation.git", "language": "Python", "service": "Reporting Service"},
        {"name": "analytics-collector", "url": "git@github.com:org/analytics-collector.git", "language": "JavaScript", "service": "Analytics Service"},
        {"name": "auditing-tracker", "url": "git@github.com:org/auditing-tracker.git", "language": "Go", "service": "Auditing Service"},
        {"name": "recommendation-ml", "url": "git@github.com:org/recommendation-ml.git", "language": "Python", "service": "Recommendation Service"},
        {"name": "reviews-api", "url": "git@github.com:org/reviews-api.git", "language": "TypeScript", "service": "Reviews Service"}
    ]
    for repo in repos:
        graph.add_node("Repository", {k: v for k, v in repo.items() if k != "service"})
        # Link Repository -> IMPLEMENTS -> Service
        graph.add_relationship("Repository", repo["name"], "Service", repo["service"], "IMPLEMENTS")
    logger.info("Seeded 20 Repositories.")

    # 5. Seed 50 APIs
    api_methods = ["GET", "POST", "PUT", "DELETE"]
    for i in range(1, 51):
        service_index = (i - 1) % len(services)
        svc_name = services[service_index]["name"]
        method = api_methods[i % 4]
        path = f"/api/v1/{svc_name.lower().split()[0]}/resource-{i}"
        api_data = {
            "path": path,
            "method": method,
            "description": f"Endpoint representing capability {i} under {svc_name}.",
            "service_name": svc_name
        }
        api_name = f"{method} {path}"
        api_data["name"] = api_name
        graph.add_node("API", api_data)
        # Link API -> EXPOSES -> Service
        graph.add_relationship("API", api_name, "Service", svc_name, "EXPOSES")
    logger.info("Seeded 50 APIs.")

    # 6. Seed 50 Requirements
    reqs_descriptions = [
        "Implement WhatsApp notifications for order delivery updates.",
        "Add credit card verification retry attempts to billing service.",
        "Support multi-currency checkout on Stripe payment-gateway.",
        "Optimize Redis cache hit-rates for catalog indexing pages.",
        "Secure profile API endpoints using JWT authentication validations.",
        "Enforce multi-factor authentication (MFA) sign-in flows.",
        "Track packaging box sizing allocations within logistics flows.",
        "Integrate FedEx delivery status real-time tracking webhooks.",
        "Calculate promotional coupons deductibles dynamically.",
        "Generate daily warehouse inventory audit reports.",
        "Aggregate system access events logging for compliance.",
        "Clean up inactive shopping baskets older than 30 days.",
        "Filter negative product reviews spam dynamically.",
        "Migrate customer address schema to ISO-3166 compliance.",
        "Scale recommendation ML vector query instances.",
        "Expose sales ledger billing API for tax auditing tools.",
        "Speed up shipping rate lookup times under 100ms.",
        "Add DHL express rate tiers to checkout cart rates.",
        "Deploy Elasticsearch clusters for Catalog search queries.",
        "Validate checkout zip codes via external census datasets."
    ]
    for i in range(1, 51):
        desc = reqs_descriptions[(i - 1) % len(reqs_descriptions)]
        svc_index = (i - 1) % len(services)
        svc_name = services[svc_index]["name"]
        eng_index = (i - 1) % len(engineers)
        eng_name = engineers[eng_index]["name"]
        
        req_id = f"REQ-{100 + i}"
        req_data = {
            "req_id": req_id,
            "title": f"Feature Requirement {req_id}: {desc.split('.')[0]}",
            "description": desc,
            "priority": "High" if i % 3 == 0 else "Medium",
            "status": "Implemented" if i < 20 else "In Progress" if i < 40 else "Proposed"
        }
        graph.add_node("Requirement", req_data)
        # Link Requirement -> AFFECTS -> Service
        graph.add_relationship("Requirement", req_id, "Service", svc_name, "AFFECTS")
        # Link Engineer -> CREATED -> Requirement
        graph.add_relationship("Engineer", eng_name, "Requirement", req_id, "CREATED")
        
        # Add to vector store for semantic search
        vector_store.add_texts(
            texts=[f"Requirement ID: {req_id}. Title: {req_data['title']}. Description: {req_data['description']}. Affected Service: {svc_name}."],
            metadatas=[{"type": "Requirement", "id": req_id}],
            ids=[f"req-{req_id.lower()}"]
        )
    logger.info("Seeded 50 Requirements.")

    # 7. Seed 30 Incidents
    incidents_list = [
        {"title": "Checkout latency increased by 1500ms", "severity": "Critical", "root_cause": "Inventory database locking connections."},
        {"title": "Payment failures spiked for Stripe checkout orders", "severity": "High", "root_cause": "Stripe Gateway returning 504 timeouts."},
        {"title": "Notifications queue deadlock", "severity": "Medium", "root_cause": "Broker connection pooling limit reached."},
        {"title": "USPS API return payload validation failure", "severity": "Medium", "root_cause": "USPS schema changed fields format."},
        {"title": "Auth token validations returning 401 unauthenticated", "severity": "High", "root_cause": "Signing certificate keys mismatch."},
        {"title": "Redis cluster out-of-memory error", "severity": "High", "root_cause": "Catalog cache keys lacked TTL eviction rules."},
        {"title": "Warehouse scanning barcode mismatch on loading docks", "severity": "Low", "root_cause": "Fulfillment printer misalignment."},
        {"title": "Reviews catalog failed to display score graphs", "severity": "Low", "root_cause": "Javascript asset load exception on client."}
    ]
    for i in range(1, 31):
        inc_template = incidents_list[(i - 1) % len(incidents_list)]
        svc_index = (i - 1) % len(services)
        svc_name = services[svc_index]["name"]
        
        inc_id = f"INC-{200 + i}"
        inc_data = {
            "inc_id": inc_id,
            "title": f"{inc_id}: {inc_template['title']}",
            "severity": inc_template["severity"],
            "status": "Resolved" if i < 25 else "Active",
            "root_cause": inc_template["root_cause"]
        }
        graph.add_node("Incident", inc_data)
        # Link Incident -> TRIGGERED_BY -> Service
        graph.add_relationship("Incident", inc_id, "Service", svc_name, "TRIGGERED_BY")
        
        # Add to vector store for semantic search
        vector_store.add_texts(
            texts=[f"Incident ID: {inc_id}. Title: {inc_data['title']}. Severity: {inc_data['severity']}. Root Cause: {inc_data['root_cause']}. Service Impacted: {svc_name}."],
            metadatas=[{"type": "Incident", "id": inc_id}],
            ids=[f"incident-{inc_id.lower()}"]
        )
    logger.info("Seeded 30 Incidents.")

    # 8. Seed 100+ Relationships (Service dependencies and other associations)
    # 8a. Service to Service Dependencies
    service_dependencies = [
        ("Checkout Service", "Payment Service"),
        ("Checkout Service", "Inventory Service"),
        ("Checkout Service", "Cart Service"),
        ("Checkout Service", "Notifications Service"),
        ("Payment Service", "Billing Service"),
        ("Order Service", "Checkout Service"),
        ("Order Service", "Shipping Service"),
        ("Order Service", "Notifications Service"),
        ("Shipping Service", "Shipping Rate Service"),
        ("Shipping Service", "Tracking Service"),
        ("Shipping Service", "Warehouse Service"),
        ("Catalog Service", "Inventory Service"),
        ("Search Service", "Catalog Service"),
        ("Recommendation Service", "Catalog Service"),
        ("Reviews Service", "Catalog Service"),
        ("Billing Service", "Auditing Service"),
        ("Reporting Service", "Billing Service"),
        ("Analytics Service", "Auditing Service")
    ]
    for src, tgt in service_dependencies:
        graph.add_relationship("Service", src, "Service", tgt, "DEPENDS_ON")
        
    # 8b. Add more links to ensure we exceed 100+ relationships
    # Let's link engineers to repositories they work on
    for i, eng in enumerate(engineers):
        repo_index = i % len(repos)
        repo_name = repos[repo_index]["name"]
        graph.add_relationship("Engineer", eng["name"], "Repository", repo_name, "WORKED_ON")
        
    # Link Runbooks and Documents
    docs_to_seed = [
        {"title": "Checkout Latency Runbook", "type": "Runbook", "content": "How to scale checkout API resources and flush cart cache keys.", "service": "Checkout Service"},
        {"title": "Stripe Billing Outage Guide", "type": "Runbook", "content": "How to toggle circuit breaker in payment-service console.", "service": "Payment Service"},
        {"title": "Warehouse Fulfillment SLA", "type": "Document", "content": "Defines packaging turnaround goals within 4 hours.", "service": "Warehouse Service"},
        {"title": "Customer Auth Verification Guide", "type": "Document", "content": "Onboarding details on OAuth token lifecycle setups.", "service": "Auth Service"}
    ]
    for doc in docs_to_seed:
        node_label = "Runbook" if doc["type"] == "Runbook" else "Document"
        doc_properties = {"title": doc["title"], "content": doc["content"]}
        graph.add_node(node_label, doc_properties)
        graph.add_relationship(node_label, doc["title"], "Service", doc["service"], "DOCUMENTED_BY")
        
        # Vector search seed
        vector_store.add_texts(
            texts=[f"Document: {doc['title']}. Content: {doc['content']}. Related Service: {doc['service']}"],
            metadatas=[{"type": doc["type"], "title": doc["title"]}],
            ids=[f"doc-{doc['title'].lower().replace(' ', '-')}"]
        )

    logger.info("Successfully completed seeding all CodeAtlas AI seed data.")
