# CodeAtlas AI — Business Case
*The Great Agent Hackathon · Build Great Products with a Great Business Case*

> Numbers marked **(assumption)** are working estimates for the pitch, not measured data. Validate or adjust them before presenting.

---

## 1. Initiative Overview

**Initiative:** CodeAtlas AI, an engineering knowledge graph and AI agents for Freshservice
**Tagline:** *"The Living Engineering Ontology and Knowledge Graph Platform"*
**Owner:** Pavan Kumar H, *\<your role / team\>*

---

## 2. Problem Statement

When an incident lands in Freshservice, the ticket says *what* broke ("Database connection pool exhausted on payment gateway"). It doesn't say *which service* that is, *who owns it*, *what it depends on*, *what happened last time*, or *which runbook to follow*.

That knowledge is spread across GitHub, Jira, Confluence, Slack, ticket history and people's heads. Service-desk agents and on-call engineers spend the first part of every incident hunting for context. They escalate to the wrong team, or repeat fixes that someone already found.

The same gap slows new engineers ("how does this system fit together?") and tech leads judging the impact of a change ("what breaks if we touch this?").

**The problem isn't finding information. It's understanding how the pieces of information relate.**

---

## 3. Why Now

- **Freshworks opened the door.** Freshservice and Freshdesk now offer official MCP servers (Freshdesk MCP has been generally available since Sep 2026), alongside REST v2 and Workflow Automator webhooks. AI agents can finally read *and act on* live tickets through supported interfaces.
- **LLMs are cheap and good enough** to turn a graph of services, owners and incidents into a readable diagnosis, as long as they're grounded in real data rather than guessing.
- **Engineering systems keep getting more fragmented** (microservices, many tools). Spreadsheet service catalogues and tribal knowledge don't scale, and every minute of slower incident resolution costs revenue and customer trust.

---

## 4. Competitive Landscape

| Alternative | Strength | Gap |
| --- | --- | --- |
| **ServiceNow (CMDB / Service Graph + Now Assist)** | Deep ITSM + CMDB in one suite | Heavy, costly, long rollouts; the CMDB needs constant manual upkeep |
| **Developer portals (e.g. Backstage, Atlassian Compass)** | Good service catalogue and ownership records | Not connected to live ITSM incidents; they don't diagnose or act on tickets |
| **Built-in helpdesk AI (e.g. ticket summaries / copilots)** | Summarises and replies within one ticket | Only sees ticket text, not the engineering system: no dependencies, owners or blast radius |
| **Do nothing (Slack pings, wikis, "ask Alex")** | Free, familiar | Slow, inconsistent, depends on a few people |

**Our edge:** CodeAtlas combines a *living graph of the engineering system* with *agents that act inside Freshservice*. A new ticket gets a diagnosis note (likely service, dependencies, similar incidents, knowledge-base articles, escalation path) posted automatically, and nobody has to leave the service desk.

---

## 5. Proposed Solution

**What it does:** CodeAtlas builds a living map (an *ontology*) of the engineering organisation: services, repositories, APIs, teams, engineers, requirements, incidents and runbooks, plus how they connect (OWNS, DEPENDS_ON, IMPACTS, ESCALATED_TO…). Specialised AI agents reason over that map to answer:
*What should I change? What breaks? Who should be involved? What happened before?*

**Freshworks adoption (built and working today):**
- **Freshservice REST v2:** live tickets, support groups and Solutions (knowledge-base) articles are synced into the graph and made searchable.
- **Freshservice MCP-style connector:** the Incident agent searches the live tenant and the KB while it reasons.
- **Knowledge-to-action:** "AI Diagnose" posts a private note back onto the Freshservice ticket.
- **Workflow Automator webhook:** *Ticket is Raised → Trigger Webhook → CodeAtlas diagnoses → note posted*, with no clicks. Tickets that already carry a CodeAtlas note are skipped, so it can't loop on itself.

**AI and agentic design:** 8 specialised agents coordinated by an orchestrator that passes context between them (e.g. *Requirement Impact → Ontology Mentor → Expert Discovery → Implementation Plan*). Every answer comes with an execution trace and an explainability panel (nodes traversed, documents consulted, confidence). Answers combine **graph traversal + vector (semantic) search + LLM reasoning**, and fall back to rule-based answers when no LLM is available.

**MVP (Phase 1 — this demo):**
- Freshservice incidents → graph → auto-diagnosis note
- Requirement impact analysis, expert finder, blast-radius simulation, knowledge-gap scan
- Interactive graph explorer
- Repository intake from GitHub URLs or ZIP files, including Excel/CSV sheets

**Later phases:**
- Live GitHub / Jira / Confluence / Slack connectors (mocked today)
- Freshdesk: link customer tickets to the engineering incidents behind them
- Native FDK sidebar app on the Freshservice ticket view
- Freshservice changes: auto-generated risk and blast-radius assessment for change approvals (CAB)
- Stale-documentation alerts, and graph updates from every resolved ticket

---

## 6. Target Customers

- **Primary:** mid-size software and digital companies (200–2,000 employees) that run IT/engineering incidents in **Freshservice** and have 20+ microservices and several engineering teams.
- **Secondary:** Freshservice MSPs, who support many client environments and need fast context on unfamiliar systems.

**Users:** service-desk agents, on-call/SRE engineers, tech leads and architects, new engineers onboarding.

---

## 7. Value Proposition

Every incident arrives in Freshservice **already diagnosed**: likely service, dependencies, similar past incidents, runbook and escalation path. Teams resolve faster and escalate to the right owner first time. The same knowledge graph answers "what breaks if we change this?" before the change ships.

---

## 8. Pricing & Packaging

- **Paid add-on for Freshservice Pro and Enterprise:** *$8 per agent/month* **(assumption)**, via the Freshworks Marketplace
- **Free tier:** graph explorer + manual diagnosis for up to 25 tickets/month, to drive adoption
- **30-day free trial** of automatic diagnosis (webhook)
- Later: an Enterprise tier with extra connectors (GitHub, Jira, Confluence, Slack) and change-risk assessment

---

## 9. Go-to-Market Plan

- **Freshworks Marketplace listing**, plus an in-product banner for eligible Freshservice admins
- **"Connect in 5 minutes" onboarding:** paste an API key, click Sync, see your graph
- **Email campaign** to Freshservice Pro/Enterprise admins offering the 30-day trial
- **Demo video:** "a ticket diagnoses itself", showing a new ticket getting a CodeAtlas note automatically
- **Design partners:** 3–5 Freshservice customers for case studies (target: measured drop in resolution time, MTTR)

---

## 10. Costs & Resources

- **Team:** 3 engineers (backend/AI, frontend, integrations) + 1 designer (part-time) + PM support **(assumption)**
- **Timeline:** about 3 months from this prototype to a production MVP (auth, multi-tenant setup, Marketplace review)
- **Estimated cost:** about $90,000–$110,000 including salaries, LLM API usage and hosting **(assumption)**
- **Running cost:** LLM calls per diagnosed ticket are cents; a rule-based mode keeps costs predictable
- *(Optional)* **Illustrative ARR:** 100 customers × 30 agents × $8 × 12 ≈ **$288K** **(assumption)**

---

## 11. Expected Benefits & Success Metrics

| Metric | Target (6 months after launch) |
| --- | --- |
| **MTTR** (mean time to resolve) for diagnosed incidents | −25% vs. non-diagnosed baseline **(assumption)** |
| **Auto-diagnosis coverage:** % of new incidents that get a CodeAtlas note | ≥ 80% |
| **Correct first escalation:** % of tickets resolved by the first team they were routed to | +20% |
| **Adoption:** trial → paid conversion | ≥ 20% |

---

## 12. Risks & Assumptions

- **Diagnosis quality depends on graph quality.** If services and owners aren't mapped, notes are generic. *Mitigation:* the Knowledge Gap agent flags missing owners, runbooks and docs, and ticket-to-service matching improves as more data is synced.
- **Trust and data privacy.** Customers may hesitate to send ticket data to an LLM. *Mitigation:* notes are private (agents only), a rule-based mode needs no LLM, and hosting and data residency are configurable.
- **Assumption:** customers will pay for an add-on on top of Freshservice's built-in AI. *Validate with design partners before pricing is final.*
- **Technical:** API rate limits and plan restrictions. For example, asset/CMDB endpoints need higher Freshservice plans; we already degrade gracefully.

---
---

# Slide Deck Outline (10 slides, ~5 minutes)

| # | Slide | Content |
| --- | --- | --- |
| 1 | **Title** | CodeAtlas AI, tagline, your name |
| 2 | **Problem** | A real ticket ("DB connection pool exhausted on payment gateway") plus the 5 unanswered questions: which service, who owns it, what depends on it, happened before?, which runbook? |
| 3 | **Why Now** | Freshworks MCP + REST + Workflow Automator; LLMs grounded in graphs; fragmentation |
| 4 | **Competition** | The table from §4, ending on "Our edge" |
| 5 | **Solution** | Architecture: Freshservice ⇄ Connectors → Knowledge Graph + Vector store → 8 Agents → Note back into Freshservice |
| 6 | **Live Demo** | (switch to app, see script below) |
| 7 | **Who & Why** | Target customers + value proposition |
| 8 | **Business Model** | Pricing, GTM, cost, illustrative ARR |
| 9 | **Success Metrics** | MTTR, coverage, correct first escalation, conversion |
| 10 | **Risks & Roadmap** | Risks + mitigations; Phase 2 roadmap |

---

# Demo Script (~5 minutes) — http://localhost:8000

**Before you start (checklist):**
- [ ] Replace the leaked Gemini key in `.env` and restart the backend. Without a key the agents still work in rule-based mode, but LLM answers read better.
- [ ] Freshservice status shows **Connected** on the dashboard.
- [ ] Create one fresh test ticket in Freshservice (e.g. *"Payment gateway timeouts during checkout"*) that hasn't been diagnosed yet.
- [ ] Have the Freshservice ticket open in a second browser tab.

| Time | Step | What to say |
| --- | --- | --- |
| 0:00 | **Dashboard.** Show stats, then the *Freshservice Integration* panel → **Test Connection** | "CodeAtlas is connected to a live Freshservice tenant." |
| 0:40 | Click **Sync Tickets to Graph** | "Tickets become Incident nodes, support groups become Teams, and each ticket is linked to the service it affects." |
| 1:20 | **Knowledge Graph.** Open a service (e.g. *Payment Gateway Service*) → **Blast Radius** | "This is the living ontology: owners, repos, dependencies and incidents. Blast radius shows what breaks if this service goes down." |
| 2:10 | Back on the dashboard → **AI Diagnose** (🧠) on the new ticket | "The Incident agent searches the graph, similar tickets and the Freshservice knowledge base…" |
| 2:50 | Switch to the Freshservice tab → refresh the ticket | "…and posts a private diagnosis note straight into Freshservice: cause, dependencies, related incidents, fixes and escalation path. Knowledge to action." |
| 3:30 | Explain the **webhook** (show the Workflow Automator rule or README) | "In production this runs automatically on *Ticket is Raised*. No clicks." |
| 4:00 | **Requirement Analyzer** → *"Add WhatsApp notifications for order updates"* | "The same graph answers engineering questions: agents hand off and produce an impact analysis and implementation plan, with a full trace." |
| 4:40 | Open the **explainability** panel | "Every answer shows which nodes and documents it used. No black box." |

**Backup plan:** if the network or Freshservice fails, use the **Incident Room** with a custom query (e.g. *"payment gateway connection pool error"*). It uses already-synced data.

---

# Reviewer Q&A: Built vs. Planned (be upfront)

| Component | Status |
| --- | --- |
| Freshservice tickets, groups, KB search, note posting, webhook | **Live** (REST v2) |
| Knowledge graph (Neo4j with in-memory fallback), vector search, 8 agents, orchestrator, explainability | **Built** |
| GitHub public-repo import, ZIP/Excel/CSV intake | **Built** |
| GitHub PR / Jira / Confluence / Slack / Freshdesk connectors | **Mocked** (same adapter interface; Phase 2) |
| Freshservice agents & assets (CMDB) | Blocked by the trial plan/role (403); planned |
| FDK sidebar app / official MCP server wiring | Phase 2 |
