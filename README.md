# CodeAtlas AI 🧠🌐

> **"The Living Engineering Ontology and Knowledge Graph Platform"**
>
> A complete, high-fidelity proof-of-concept (POC) that maps, reasons about, and explains engineering systems, team ownerships, active incidents, and feature requirement impacts. Built for platform agent skills and knowledge hackathons.

---

## 🚀 Key Features

1. **Living Engineering Ontology**: Maps object entities like `BusinessCapability`, `Service`, `Repository`, `API`, `Engineer`, `Team`, `Requirement`, `Incident`, `Document`, and `Runbook`.
2. **Hybrid Intelligence Data Layer**: Resolves queries by combining graph traversals (Neo4j) with vector search queries (ChromaDB).
3. **Zero-Dependency Fallback Mode**: Instantly test-run the entire application without needing local docker or external databases. If Neo4j or ChromaDB are unreachable, the system automatically hot-swaps to in-memory Python graph structures and text similarity vectors pre-seeded with our rich mock datasets.
4. **Orchestrated Multi-Agent Pipeline**: Coordinate tasks across 7 specialized reusable agents:
   - **Ontology Mentor**: Teaches engineers how services and capabilities operate.
   - **Requirement Impact**: Evaluates repository, API, and service blast radius for a new feature.
   - **Expert Discovery**: Profiling owners, git contributors, and subject matter experts.
   - **Incident Context**: Troubleshoots incidents using historical failures and Confluence runbooks.
   - **Architecture Storyteller**: Narrates end-to-end data flows and service interactions.
   - **Knowledge Gap**: Scans the codebase for missing ownerships, documentation, or runbooks.
   - **Architectural Blast Radius**: Simulates down-time impacts on business capabilities.
5. **Pluggable MCP Adapters**: Features Mock MCP connectors for **GitHub, Jira, Confluence, Slack, Freshservice, and Freshdesk** to retrieve external operational contexts.
6. **Premium Next.js Frontend**: High-fidelity dark mode dashboard with an interactive React Flow graph visualization featuring dynamic blast-radius highlighting and query tracing.

---

## 🛠️ Tech Stack

* **Frontend**: Next.js 15, TypeScript, TailwindCSS v4, React Flow, Lucide Icons.
* **Backend**: FastAPI, Python 3.10+, OpenAI SDK.
* **Databases**: Neo4j (Graph), ChromaDB (Vector) — *both feature hot-swappable in-memory Python fallback equivalents*.

---

## 🗂️ Project Structure

```
/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── config.py         # Environmental configurations
│   │   ├── ontology/         # Ontology Pydantic models
│   │   ├── graph/            # Neo4j & In-Memory Graph drivers
│   │   ├── vectorstore/      # ChromaDB & TF Cosine Similarity drivers
│   │   ├── agents/           # Specialized Agents & Orchestrator pipeline
│   │   ├── connectors/       # Pluggable MCP adapters
│   │   ├── data/             # Seeding engine & generators
│   │   └── main.py           # FastAPI server routes
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Next.js Frontend Client
│   ├── src/app/
│   │   ├── page.tsx          # Home Dashboard metrics
│   │   ├── analyzer/page.tsx # Multi-Agent Requirement impact analyzer
│   │   ├── graph/page.tsx    # Interactive React Flow canvas
│   │   ├── experts/page.tsx  # SME Finder
│   │   ├── incidents/page.tsx# Incident diagnosis room
│   │   ├── gaps/page.tsx     # Code compliance audit center
│   │   ├── freshservice/page.tsx # Freshservice sync, AI diagnosis + live agent trace
│   │   ├── logs/page.tsx     # Agent activity ledger
│   │   ├── globals.css       # Global styles
│   │   └── layout.tsx        # Sidebar shells
│   ├── Dockerfile
│   └── package.json
├── docs/                     # Architecture diagrams, pitch deck, business case
├── docker-compose.yml        # Orchestration profile
├── .env                      # Local environment configuration
└── README.md                 # Documentation
```

---

## 🏃 Local Setup & Run

### Deploy to Render (one service)

This repository includes a root `Dockerfile` and `render.yaml` that build the Next.js UI as static files and serve it from the same FastAPI container as the API. There is no separate frontend deployment or cross-origin configuration to manage.

1. Push this repository to GitHub.
2. In Render, choose **New + → Blueprint** and select the repository. Render detects `render.yaml`.
3. Add `OPENAI_API_KEY` in the Render environment settings if you want live model responses; it is optional because the app has a seeded in-memory fallback.
4. Deploy and open the single Render URL. The UI uses relative `/api/v1/...` calls, so it automatically talks to that same service.

The free deployment runs with `FORCE_FALLBACK=true`, so it needs no Neo4j or Chroma instance. Runtime data is in memory and resets after a service restart.

### Option A: Direct Local Setup (Fastest & Zero-Dependency)

Since Docker is sometimes not available on GUI macOS tools, you can run the services directly in terminal processes. The backend automatically switches into **In-Memory Fallback Mode** (`FORCE_FALLBACK=true` in `.env`), allowing instant trials.

#### 1. Start FastAPI Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip3 install -r requirements.txt

# Start reload server
python3 -m uvicorn app.main:app --port 8000 --reload
```

The backend server starts on `http://localhost:8000`.

#### 2. Start Next.js Frontend

Open a new terminal window:

```bash
# Navigate to frontend
cd frontend

# Install package dependencies
npm install

# Start next dev server
npm run dev
```

The frontend client starts on `http://localhost:3000`. Open your browser to [http://localhost:3000](http://localhost:3000).

---

### Option B: Docker Compose

If you have Docker installed and running:

```bash
# Run containers
docker-compose up --build
```

This spins up:
1. **CodeAtlas AI** (the UI and API together) on [http://localhost:8000](http://localhost:8000).
2. **Neo4j** Console on [http://localhost:7474](http://localhost:7474) (Credentials: `neo4j/password`).

---

## 🎫 Freshservice Integration

CodeAtlas uses the Freshservice REST v2 API to read tickets, changes, groups and the knowledge base, and to write diagnoses, change-impact notes and group assignments back. Freshservice knows *what broke, who reported it and who is on call*; CodeAtlas adds *how the system is wired, what changed recently and who wrote the code*.

Architecture and sequence diagrams: [docs/architecture.md](docs/architecture.md).

| Where | What it does |
| --- | --- |
| **Freshservice Integration page** (`/freshservice`) | Tests the connection, **Sync Tickets to Graph**, lists synced tickets and runs **AI Diagnose** (brain icon) with a live agent trace, routing result and note status. |
| **Sync** (`POST /api/v1/freshworks/sync`) | Imports support groups as `Team` nodes and tickets as `Incident` nodes (`FS-<id>`). Each ticket is linked `IMPACTS → Service` when its text matches a known service and `ESCALATED_TO → Team` when it has a group, and is indexed in the vector store. |
| **Incident Context Agent** (Incident Room, Analyzer) | Searches live tickets and Freshservice Solutions (KB) articles, plus recent GitHub releases, commits and config diffs (secrets redacted) for the matched service's repositories, and cites them in the diagnosis. |
| **AI Diagnose** (`POST /api/v1/freshworks/diagnose`) | Diagnoses one ticket, **auto-routes** it to the best-matching Freshservice group, and posts a private note with affected service, suspected cause, recent changes, related incidents, fixes, KB articles, routing reason and escalation path. |
| **Webhook** (`POST /api/v1/freshworks/webhook`) | The same diagnosis, triggered by a Workflow Automator *Trigger Webhook* action. Skips tickets that already carry a CodeAtlas note. |
| **Change impact** (`POST /api/v1/freshworks/changes/analyze`) | Runs the multi-agent pipeline (Requirement Impact → Ontology Mentor → Expert Discovery) on a Freshservice Change, adds the downstream **blast radius** from the graph, and posts affected services, repositories, APIs, risk, recommended steps and suggested CAB reviewers as a note on the change. |

All endpoints accept numeric IDs or Freshservice display IDs (`"INC-103"`, `"CHN-6"`), so Workflow Automator placeholders can be used as-is.

Setup: set `FRESHSERVICE_DOMAIN`, `FRESHSERVICE_API_KEY` and (optionally) `FRESHSERVICE_WORKSPACE_ID`, `GITHUB_TOKEN` and `GITHUB_CHANGE_WINDOW_DAYS` in `.env` and restart the backend. Without an API key the agents fall back to the mocked Freshservice connector.

### Auto-routing

During diagnosis CodeAtlas picks a Freshservice group from the ticket text and the affected service (e.g. *connection pool exhausted* → **Database Team**, *VPN / DNS* → **Network Team**), falling back to **Incident Team**. It **only assigns tickets that have no group**, so an agent's choice is never overridden, and the reason is written into the note. The keyword map is `GROUP_KEYWORDS` in `backend/app/connectors/freshservice.py`.

### Automate with Workflow Automator

First expose the backend publicly. Freshservice cannot reach `localhost`, so use the Render URL or a tunnel such as `ngrok http 8000`. Then in Freshservice go to **Admin → Automation & Productivity → Workflow Automator**.

**New tickets → diagnosis + routing**

1. **Tickets → Event Based Workflows → Create**. Event: **Ticket is Raised** (optionally add a condition, e.g. **Type is Incident**).
2. Add a **Web Request** node: `POST https://<your-host>/api/v1/freshworks/diagnose`, No Auth, body:
   ```json
   { "ticket_id": "{{ticket.id}}", "post_note": true }
   ```
   Alternatively use **Trigger Webhook** to `https://<your-host>/api/v1/freshworks/webhook` with `{ "ticket_id": "{{ticket.id_numeric}}" }`; if `FRESHSERVICE_WEBHOOK_SECRET` is set, add the header `X-CodeAtlas-Secret: <secret>`.
3. **Activate**.

**New changes → blast radius**

1. **Changes → Event Based Workflows → Create**. Event: **Change is created**.
2. Add a **Web Request** node: `POST https://<your-host>/api/v1/freshworks/changes/analyze`, No Auth, body:
   ```json
   { "change_id": "{{change.id}}", "post_note": true }
   ```
3. **Test Web Request**, then **Activate**.

Check runs under **Workflow Automator → Execution Logs**. If a tunnel restarts, its URL changes: update the endpoint in both workflows, and type it on a single line (a pasted line break causes an *invalid host* error).

### How each CodeAtlas module maps to Freshservice

| CodeAtlas page | Freshservice module | Status |
| --- | --- | --- |
| Freshservice Integration · Incident Room | Tickets, Solutions (KB), Groups | Live: diagnosis note + auto-routing |
| Requirement Analyzer · Knowledge Graph · Expert Finder | Changes | Live: blast-radius note with CAB reviewers |
| Agent Activity Log | Private notes | Live: every AI decision is traceable from the ticket |
| Knowledge Graph | CMDB relationships | Designed: needs a Freshservice plan that includes CMDB |
| Knowledge Gaps | Problems, Solutions (KB) | Phase 2: recurring incidents → Problem, KB drafts |

---

## 📊 Demo Scenarios to Try

1. **Seed the database**: Click **Reset & Seed DB** in the bottom-left sidebar of the frontend. This clears databases and populates exactly 20 services, 25 engineers, 5 teams, 50 requirements, 30 incidents, and 100+ dependency relationships.
2. **Run Multi-Agent Analyzer**: Navigate to the **Requirement Analyzer** and run the default query: *"Add WhatsApp notifications for order updates"*. Watch the agent cooperative trace execute in real-time, handing off from the Impact Agent → Ontology Agent → Expert Discovery, ending with a synthesized implementation plan.
3. **Trace Blast Radius**: Navigate to the **Knowledge Graph**, select a service node (e.g. *Checkout Service*), and click **Blast Radius** or **Dependencies** in the side drawer. Watch the React Flow canvas dynamically fade out unrelated nodes and highlight downstream impact paths in red.
4. **Scan Knowledge Gaps**: Navigate to **Knowledge Gaps** to see the Compliance Agent scan microservices for missing runbooks, owners, or files and assign a project risk rating.
5. **Diagnose Outages**: Go to the **Incident Room**, select an active incident (e.g., *INC-212 Stripe Gateway Timeout*), and click **Diagnose Incident**. The Incident Agent will suggest fixes, trace impacted upstream files, and load Confluence runbooks.
6. **Auto-diagnose a live Freshservice ticket**: With the ticket workflow active, raise a ticket such as *"Database connection timeout on Payment Service, connection pool exhausted after this morning's deploy"*. Within seconds it is assigned to **Database Team** and carries a private CodeAtlas note. Open **Freshservice Integration** and click the brain icon to watch the agent trace.
7. **Assess a Freshservice Change**: With the change workflow active, create a change such as *"Upgrade SMTP relay config for Notification Service"*. A note appears on the change with affected services, downstream blast radius, risk and suggested CAB reviewers; the same dependents light up under **Knowledge Graph → Blast Radius**.
