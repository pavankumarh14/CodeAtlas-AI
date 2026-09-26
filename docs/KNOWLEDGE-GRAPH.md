# CodeAtlas AI: Knowledge Graph Mapping

Snapshot of the live Neo4j graph (84 nodes, 106 relationships) after **Seed Real Architecture** plus Freshservice sync.

## 1. In one paragraph

The graph links your **real GitHub repositories** and **real Freshservice tickets and groups** through a **hand-modelled service layer**. The seed script ([`seed_real.py`](../backend/app/data/seed_real.py)) defines:
- which repository implements which service;
- which team owns each service, and which engineers work on which repositories;
- how services depend on each other;
- the APIs, requirements and runbooks.

Nothing is read from inside the repositories at seed time. During a diagnosis, CodeAtlas follows the graph to a repository and fetches its **recent commits, releases and config diffs live from GitHub**.

## 2. Service ↔ repository mapping

| Service | Risk | GitHub repo | Repo exists? | Owning team | Engineers | Depends on (upstream) | Depended on by (blast radius) | APIs | Runbook | Req. | Freshservice tickets |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Payment Gateway Service | Critical | `payment-gateway` | ❌ **Not on GitHub** | Communications & Integrations | Maya Patel, Pavan | — | Frontend App, Funding Platform | 2 | Connection Pool Runbook | REQ-108 | FS-80 |
| Notification Service | Medium | `Beacon` | ✅ | Communications & Integrations | Maya Patel, Pavan | — | Alerting, Project Mgmt, Frontend App | 2 | Beacon Email & Alert Relay | REQ-103 | FS-21, FS-96 |
| Alerting Service | High | `PulseCommand-AI` | ✅ | Reliability & Observability | Sarah Chen, Pavan | Notification | Health Monitoring | 2 | — | REQ-102 | FS-95, FS-103 |
| Health Monitoring Service | High | `DataHub-Health-Guardian` | ✅ | Reliability & Observability | Pavan | Alerting | QA Automation, Core Platform | 2 | DataHub Telemetry Failure Guide | REQ-101 | — |
| Frontend App | High | `UrbanNexus` | ✅ | Product & Growth | Marcus Vance, Pavan | Payment Gateway, Notification, Documentation, Market Intelligence | QA Automation | 2 | — | REQ-107 | — |
| QA Automation Service | Medium | `EndToEndPlayWrightAutomationTool` | ✅ | DevOps & QA Automation | Alex Rivera, Pavan | Frontend App, Health Monitoring | — | 1 | Playwright Triage Playbook | REQ-105 | — |
| Project Management Service | Low | `SprintPilot` | ✅ | Product & Growth | Marcus Vance, Pavan | Notification | — | 1 | — | REQ-104 | — |
| Documentation Service | Low | `DocAnchor` | ✅ | Core Platform & Analytics | Pavan | — | Frontend App, Core Platform | 1 | — | REQ-106 | — |
| Market Intelligence Service | Low | `MarketRadar` | ✅ | Product & Growth | Elena Rostova, Pavan | — | Frontend App, Funding Platform | 1 | — | REQ-109 | — |
| Funding Platform | Medium | `FunderAI` | ✅ | Product & Growth | Elena Rostova, Pavan | Payment Gateway, Market Intelligence | — | 1 | — | — | — |
| Core Platform & Analytics | High | `CodeAtlas-AI` | ✅ | Core Platform & Analytics | Pavan | Health Monitoring, Documentation | — | 0 | — | — | — |

"Blast radius" lists direct dependents only; traversal continues hop by hop. For example, Notification Service → Alerting → Health Monitoring → QA Automation / Core Platform gives 6 services in total.

## 3. Freshservice tickets in the graph

| Incident node | Freshservice ticket | Linked service (`IMPACTS`) | Group (`ESCALATED_TO`) |
|---|---|---|---|
| FS-80 | Database connection pool exhausted on payment gateway | Payment Gateway Service | Database Team (set by CodeAtlas auto-routing) |
| FS-103 | Alert Service Down – Critical Monitoring Gap | Alerting Service | Software Team (set by CodeAtlas auto-routing) |
| FS-95 | Alerts are not being triggered after the latest deploy | Alerting Service | — |
| FS-96 | Emails and SMS notifications failing | Notification Service | — |
| FS-21 | What's wrong with my email? | Notification Service | — |
| FS-22 | Request for Andrea: Logitech Wireless Mouse | — (correctly unmapped: not an engineering incident) | — |
| FS-23 | Request for Andrea: Dell Monitor | — (correctly unmapped) | — |

Tickets are linked to a service by keyword scoring (`SERVICE_KEYWORDS` in [`freshservice.py`](../backend/app/connectors/freshservice.py)), e.g. *email, smtp, beacon* → Notification Service; *payment, connection pool* → Payment Gateway Service.

## 4. Where each piece of data comes from

| Data | Source | Real? | Stored in graph? |
|---|---|---|---|
| Repository names and URLs | Seed, matching your GitHub account | ✅ 10 of 11 exist | ✅ |
| Repository languages | Seed | ⚠️ Hand-typed; several differ from GitHub (Beacon is Python, not Go; MarketRadar and UrbanNexus are JavaScript) | ✅ |
| Commits, releases, config diffs, PR/issue links | GitHub REST API, fetched per diagnosis, cached 2 min | ✅ Real | ❌ Fetched live |
| Services, dependencies, APIs, requirements, runbooks | Seed | Illustrative | ✅ |
| 5 seed teams and 8 engineers | Seed | Pavan real; the other 7 illustrative | ✅ |
| 14 Freshservice groups | Freshservice sync | ✅ Real | ✅ as `Team` (source = Freshservice) |
| 7 tickets | Freshservice sync / diagnosis | ✅ Real | ✅ as `Incident` (`FS-<id>`) |
| KB articles, related tickets | Freshservice REST, per diagnosis | ✅ Real | ❌ Fetched live |
| Search index over services, requirements, runbooks, tickets | Built at seed/sync | Derived | ❌ In memory; lost on restart |

## 5. How data is written

All writes go through two idempotent functions in [`neo4j_driver.py`](../backend/app/graph/neo4j_driver.py):

- `add_node(label, props)` runs `MERGE` on the label's key and then `SET` properties. The key is `name` for most labels, `inc_id` for Incident, `req_id` for Requirement and `title` for Runbook.
- `add_relationship(...)` matches both ends by key and runs `MERGE` on the edge.

Re-seeding or re-syncing therefore updates nodes and never duplicates them. Writers:

| Writer | Writes |
|---|---|
| `seed_real_architecture()` | Clears the graph and the search index, then writes teams, engineers, services, repos, APIs, requirements, dependencies and runbooks |
| `sync_tickets_to_graph()` | Freshservice groups → `Team`; tickets → `Incident` via `upsert_ticket()` |
| `upsert_ticket()` (also on every diagnosis) | `Incident` node, plus `IMPACTS → Service` if matched and `ESCALATED_TO → Team` if the ticket has a group |
| Change analysis | Posts a note on the change; **does not write to the graph** |

## 6. Schema and how agents use it

| Relationship | Count | Used by |
|---|---|---|
| `(Service)-[:DEPENDS_ON]->(Service)` | 13 | Blast radius (reverse direction) and upstream root causes: Incident Context, change analysis |
| `(Team)-[:OWNS]->(Service)` | 11 | Escalation path level 1 |
| `(Repository)-[:IMPLEMENTS]->(Service)` | 11 | Choosing which GitHub repo to check for recent changes |
| `(Engineer)-[:WORKED_ON]->(Repository)` | 19 | Expert Finder, CAB reviewers |
| `(Engineer)-[:MEMBER_OF]->(Team)` | 8 | Ownership view |
| `(API)-[:EXPOSES]->(Service)` | 15 | Requirement and change impact |
| `(Requirement)-[:AFFECTS]->(Service)` · `(Engineer)-[:CREATED]->(Requirement)` | 9 · 9 | Requirement Analyzer, similar requirements |
| `(Runbook)-[:DOCUMENTED_BY]->(Service)` | 4 | Suggested fixes |
| `(Incident)-[:IMPACTS]->(Service)` | 5 | Related past incidents |
| `(Incident)-[:ESCALATED_TO]->(Team)` | 2 | Routing history |

## 7. How it appears on the Knowledge Graph page

- **Layout:** one column per type, left to right: Team (yellow) → Engineer (green) → **Service (blue)** → Repository (purple) → API (teal) → Requirement (pink) → **Incident (red)** → Runbook (light green).
- **Tabs:** Architecture (default) · Ownership · **Incidents** (the Freshservice view) · Requirements · Full Graph.
- **Click a service** to see its properties, plus **Dependencies** and **Blast Radius**.

## 8. Known issues

| Issue | Impact | Fix |
|---|---|---|
| `payment-gateway` repo doesn't exist on GitHub | Ticket FS-80's diagnosis can never show a recent code/config change | Create the repo with a config commit, or remap the service |
| Graph-page Blast Radius follows **all** incoming edges | Also highlights repos and APIs, not only dependent services; differs from the change note | Restrict traversal to `DEPENDS_ON` in `graph/page.tsx` |
| Seeded languages don't match GitHub | Minor credibility issue if a judge checks | Correct the values in `seed_real.py` |
| Search index is in memory | Empty after a backend restart | Click **Seed Real Architecture** after each restart |
| Graph page header reads "DASHBOARD" | Cosmetic | Set the page title |

## 9. Extending the graph with Freshservice modules

Checked against your tenant's API:

| Module | API on your plan | Proposed mapping |
|---|---|---|
| Tickets | ✅ Built | `Incident -IMPACTS→ Service`, `-ESCALATED_TO→ Team` |
| Problems | ✅ (1: *Unable to reach email server*) | `(Problem)-[:AFFECTS]->(Service)`, `(Incident)-[:INSTANCE_OF]->(Problem)` |
| Changes | ✅ (1: *Getting ES3 back up to speed*) | `(Change)-[:MODIFIES]->(Service)`, `(Change)-[:REVIEWED_BY]->(Engineer)` |
| Releases | ✅ (1: *Replacing Exchange Server 3*) | `(Release)-[:INCLUDES]->(Change)`, `(Release)-[:DEPLOYS]->(Service)` |
| Tasks | ✅ (none yet) | `(Task)-[:PART_OF]->(Incident\|Change)` |
| Projects | ✅ (2 samples) | `(Project)-[:DELIVERS]->(Requirement)` |
| Alerts | ❌ 404 | `(Alert)-[:FIRED_ON]->(Service)`, designed only |
| Assets / Applications | ❌ 403 (CMDB not in plan) | `(Asset)-[:HOSTS]->(Service)`, designed only |

Your tenant already has a linked chain: Problem #6 → Change #6 → Release #6, all about the email server. That maps to **Notification Service (Beacon)**. With these modules synced, email tickets FS-21 and FS-96 would be diagnosed as *"known problem #6, fix in change #6, release #6 planned"*.

## 10. What to tell judges

> "The repositories and their commit history are real and fetched live, and so are the Freshservice tickets and groups. The service layer on top (which repo is which service, owners, dependencies) is modelled by hand, because a real company's service catalogue isn't available to us. In production it would come from repo manifests, CODEOWNERS files or the Freshservice CMDB. The Repository Intake page shows the real import path."
