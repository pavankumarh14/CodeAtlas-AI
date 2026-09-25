# CodeAtlas AI — Demo Script & Presenter Guide

Total run time: about 7 minutes of demo plus Q&A. Sections 1 and 2 are for you before going on stage. Section 3 is the talk track. Sections 4–6 are for questions about what is real.

---

## 1. Pre-demo checklist (do in this order, 30 minutes before)

| # | Step | Why it matters |
| --- | --- | --- |
| 1 | Add `GITHUB_TOKEN=<read-only token>` to `.env` | Without it GitHub allows only **60 requests/hour**, and one diagnosis uses roughly 10–20. When the limit runs out, the "recent change" evidence silently disappears from notes. |
| 2 | Start Neo4j (Desktop or `docker compose up neo4j`) | The graph lives here. |
| 3 | Start backend: `cd backend && source venv/bin/activate && python -m uvicorn app.main:app --port 8000` | Check the log shows `Successfully connected to Neo4j` and 8 agents initialised with Gemini. |
| 4 | Start frontend: `cd frontend && npm run dev` → http://localhost:3000 | |
| 5 | Start `ngrok http 8000`, copy the URL | Freshservice can't reach `localhost`. |
| 6 | Paste the ngrok URL into **both** Workflow Automator Web Request nodes (ticket and change), on one line, no spaces | The free ngrok URL changes every restart. A pasted line break causes "invalid host". |
| 7 | In CodeAtlas, sidebar → **Seed Real Architecture** | **Required after every backend restart.** The vector store is in memory and empty after a restart. This reloads the graph and the vector index, then syncs Freshservice tickets. |
| 8 | Freshservice Integration page → **Test Connection** → Connected | |
| 9 | Dry run: raise one throwaway ticket and check the note arrives | Warms the LLM and GitHub cache and proves the tunnel works. |
| 10 | Open tabs: Freshservice tickets list, Freshservice changes list, CodeAtlas Freshservice Integration page, CodeAtlas Knowledge Graph | |

**Do not click "Load Generic Demo" or "Wipe / Clear DB" before the demo.** They replace or erase the real architecture.

---

## 2. What to say in one breath (30s opener)

> "A Freshservice ticket tells you *what* broke. It doesn't tell you which service, who owns it, what changed yesterday, or what else breaks with it. That context lives in GitHub, runbooks and people's heads. CodeAtlas keeps a living knowledge graph of the engineering system, and eight AI agents use it to diagnose, route and assess every ticket and change **inside Freshservice, automatically**."

---

## 3. Demo talk track

### Step 1 — The problem (30s)
**Show:** the Freshservice ticket list.
**Say:** "Our tenant's tickets arrive unassigned and without engineering context. An L1 agent has to guess."

### Step 2 — Raise a ticket, watch it get diagnosed and routed (2 min) ⭐ main moment
**Do:** create a ticket in Freshservice:
- Subject: `Database connection timeout on Payment Service`
- Description: `Connection pool exhausted after this morning's deploy. Checkout requests failing.`
- Priority: High

**Then:** Workflow Automator → Execution Logs shows the run succeeded. Open the ticket and refresh.

**Point at:**
1. **Group = Database Team.** "Nobody assigned this. CodeAtlas did, and only because it was unassigned. It never overrides a human."
2. **The private note:** affected service, suspected cause, recent GitHub commits and config changes (secrets masked), related incidents, KB article, routing reason, escalation path.

**What happened underneath (say briefly):**
- Freshservice called our API with the ticket ID.
- The **Incident Context Agent**:
  - matched the text to *Payment Gateway Service* in the graph;
  - found its upstream dependencies, owning team and repository;
  - pulled recent commits from the **real GitHub repo**;
  - searched Freshservice tickets and the KB;
  - had Gemini reason over all of that evidence.
- CodeAtlas then set the group and posted the note through the Freshservice REST API.

### Step 3 — Show the reasoning (1 min)
**Do:** CodeAtlas → **Freshservice Integration** → **Sync Now** → click the 🧠 on the same ticket.
**Show:** the live agent trace (each step as it runs), then the result card with the Routing line.
**Then:** **Agent Activity Log**, where every Freshservice-triggered run is recorded.
**Say:** "Every AI decision is explainable: which data it looked at and why it chose that answer."

### Step 4 — Raise a change, get the blast radius (1.5 min)
**Do:** in Freshservice create a Change: `Upgrade SMTP relay config for Notification Service`.
**Show:** refresh the change to see the **CodeAtlas AI Change Impact Analysis** note. It lists affected services, downstream blast radius, repositories, APIs, risk, recommended steps and suggested CAB reviewers.
**Say:** "Here three agents hand off in sequence. The **Requirement Impact** agent maps what's touched. The **Ontology Mentor** profiles the service. **Expert Discovery** finds the reviewers. The blast radius comes straight from the dependency graph."

### Step 5 — See the same answer in the graph (1 min)
**Do:** CodeAtlas → **Knowledge Graph** → click *Notification Service* → **Blast Radius**.
**Show:** the same downstream services highlighted.
**Say:** "The note isn't the LLM guessing. It's the graph, and you can inspect it."

### Step 6 — Close (30s)
**Say:** "Two live Freshservice flows, zero clicks for the agent, and the diagnosis is explainable. Next steps are an FDK sidebar app, CMDB sync on plans that include it, and live Jira, Confluence and Slack connectors."

**If something fails live:** the 🧠 button in CodeAtlas runs the identical diagnosis and posts the identical note, so keep going. If Gemini fails, agents fall back to a rule-based answer (it still posts a note, just less fluent).

---

## 4. What is stored where

| Data | Where it lives | Survives a backend restart? | Real or mocked |
| --- | --- | --- | --- |
| Services, repositories, APIs, teams, engineers, requirements, runbooks, dependencies | **Neo4j** (`neo4j://127.0.0.1:7687`) | ✅ Yes | **Hand-authored seed** (`backend/app/data/seed_real.py`) mapped to 11 of your **real public GitHub repos**. Service names, dependencies and 7 of the 8 engineers are illustrative. |
| Freshservice tickets (as `Incident` nodes `FS-<id>`) and groups (as `Team` nodes) | **Neo4j**, written by Sync and by every diagnosis | ✅ Yes | **Real**, from the live tenant |
| Search index (tickets, services, requirements, runbooks, uploaded docs) | **In-memory Python list** in the backend process | ❌ **No, emptied on restart.** Re-run *Seed Real Architecture*. | Built from the data above |
| Agent Activity Log | **In-memory list** in the backend process | ❌ No | Real runs |
| Diagnosis notes, change notes, group assignments | **Freshservice** | ✅ Yes (in Freshservice) | Real, written back via REST |
| Recent releases, commits, config diffs, PR/issue links | **Not stored.** Fetched live from GitHub, cached for 2 minutes | n/a | **Real** GitHub API |
| KB articles, related tickets | **Not stored.** Fetched live from Freshservice per diagnosis | n/a | **Real** |
| LLM reasoning | **Not stored.** Gemini (`gemini-2.5-flash`) via its OpenAI-compatible API | n/a | Real model call; rule-based fallback if no key |

**Notes on the storage choices:**
- **Neo4j** holds relationships (depends on, owns, impacts), and blast radius is a graph traversal. That's why it's a graph database and not a table.
- The **in-memory fallbacks** exist so the app can run with zero setup. If Neo4j is unreachable (or `FORCE_FALLBACK=true`), the graph also moves to memory, and all data is lost on restart.
- **ChromaDB** is supported but not installed here, so search uses the in-memory store.

---

## 5. What is real vs. mocked vs. designed

**Live and real**
- Freshservice REST v2: tickets, changes, groups, KB search, private notes, ticket group assignment.
- Freshservice Workflow Automator: *Ticket is raised* and *Change is created* → Web Request → CodeAtlas.
- GitHub REST: releases, commits, config-file diffs (secrets redacted), linked PRs and issues for repos in the graph.
- Gemini LLM reasoning for all 8 agents.
- Neo4j graph traversal: dependencies, blast radius, ownership.

**Mocked (hard-coded sample data, same adapter interface as the live Freshservice adapter)**
- Jira adapter: sample requirements, used by the Requirement Impact agent.
- Confluence adapter: sample runbooks, used by the Incident Context agent.
- GitHub *adapter* PR search: sample PRs, used by the Requirement Impact agent. The real GitHub changes above come from a separate client.
- Slack and Freshdesk adapters: registered, not yet called by any agent.
- *Load Generic Demo* dataset: a fictional 20-service company, for trying the app without your repos.

**Designed, not built**
- CMDB relationship sync (the trial plan returns "CMDB not supported in your plan").
- FDK sidebar app and the official Freshworks MCP server (Phase 2).
- On-call-aware escalation (the API works, but the tenant has no schedules).

---

## 6. Likely judge questions — straight answers

**"Is the search semantic / embeddings?"**
Not in this build. The in-memory index uses word-overlap similarity (TF cosine). The graph and the LLM do the reasoning. ChromaDB (real embeddings) is a drop-in swap already supported in code.

**"Is routing done by AI?"**
No, deliberately. Routing uses transparent keyword rules per Freshservice group, because an automatic assignment must be predictable and explainable. The agents do the diagnosis; the rules do the assignment, and the note states the reason. It never overrides an existing group.

**"What if the LLM is wrong or down?"**
Every note cites its evidence (commits, KB articles, graph dependencies), so an agent can verify it. Without an LLM, agents fall back to rule-based answers. Notes are **private**, so customers never see an unverified diagnosis.

**"Where does the architecture come from? Is it real?"**
The repositories are real public GitHub repos and their commits are fetched live. The services, dependencies and most engineers were hand-authored to represent a realistic organisation, because we don't have a real company's service catalogue. In production this would come from repo manifests, CMDB and ownership files. The Repository Intake page already imports repos and ZIPs.

**"Do the multi-agent handoffs adapt dynamically?"**
The change pipeline is a fixed sequence (Impact → Ontology → Expert), chosen for reliability. Other requests are routed by the orchestrator to the best single agent.

**"Why a Web Request and not the Freshworks MCP server?"**
Workflow Automator is event-driven: it pushes each new ticket or change to us, with no polling. The MCP server suits an assistant pulling data on demand. Wiring it is on the roadmap, and our adapter interface is already MCP-shaped.

**"How do you avoid loops or duplicate notes?"**
The webhook endpoint skips tickets that already carry a CodeAtlas note, and routing only acts on unassigned tickets.

**"Is ticket data sent to the LLM?"**
Yes: subject, description and retrieved context go to Gemini. Secrets in config diffs are masked first. A deployment could use a private or self-hosted model, or the rule-based mode.
