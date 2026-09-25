# CodeAtlas AI — Hackathon Submission

**Team Name:** `<TEAM NAME>` (Pavan Kumar H)

**Selected Track:** **Track 2 — Platform Agent Skills & Knowledge**

CodeAtlas is a library of reusable agent skills (8 specialized agents, one orchestrator). The agents share a living engineering knowledge graph and plug into external systems through a common MCP-style adapter interface. Freshservice is the live integration: it is connected through the Freshworks developer platform (REST v2 API and Workflow Automator).

## Solution

CodeAtlas AI is a living knowledge graph of an engineering organisation: its services, owners, dependencies, repositories and past incidents, with 8 AI agents that reason over it. When a ticket or change is raised in Freshservice, the agents automatically work out the affected service, the recent code change most likely to have caused the problem, and the blast radius. They route the ticket to the right team and post an explainable diagnosis back into Freshservice before anyone opens it.

## Links

| Item | Link |
| --- | --- |
| GitHub Repository | https://github.com/pavankumarh14/CodeAtlas-AI |
| PPT / Presentation | https://github.com/pavankumarh14/CodeAtlas-AI/blob/main/docs/CodeAtlas-AI-Pitch-Deck.pptx |
| Demo Video | `<DEMO VIDEO URL>` |
| Deployment / Live Product | `<RENDER URL>` (optional; one-service deploy via `render.yaml`) |

## How Freshworks is integrated

CodeAtlas connects to a live Freshservice tenant in both directions.

**Freshservice → CodeAtlas (automatic triggers)**
- A **Workflow Automator** workflow on *Ticket is raised* sends the ticket ID to CodeAtlas through a **Web Request** node.
- A second workflow on *Change is created* sends the change ID the same way.
- No clicks are needed. Every run appears in Freshservice's Execution Logs.

**CodeAtlas reads from Freshservice (REST v2)**
- **Tickets and Changes:** subject and description are the input to the agents.
- **Solutions (KB) articles:** searched and cited in every diagnosis.
- **Groups:** imported as Team nodes in the knowledge graph and used for routing.
- **Sync:** imports tickets into the graph as Incident nodes linked to the services they affect, so past incidents inform new diagnoses.

**CodeAtlas writes back to Freshservice (REST v2)**
- **Incident diagnosis note** (private) on the ticket: affected service, suspected cause, the recent GitHub commit or config change most likely responsible (secrets redacted), related incidents, recommended fixes, KB articles and an escalation path naming the change author.
- **Auto-routing:** sets the ticket's group (e.g. *connection pool exhausted* → Database Team). It only does this when the ticket is unassigned, and the note says why.
- **Change impact note** on the change: a 3-agent pipeline (Requirement Impact → Ontology Mentor → Expert Discovery) posts affected services, downstream blast radius, risk, recommended steps and suggested CAB reviewers.

**Inside CodeAtlas**
- A dedicated **Freshservice Integration** page tests the connection and syncs tickets. It runs AI Diagnose on any ticket and shows a live trace of each agent step.
- The **Agent Activity Log** records every Freshservice-triggered run.

**Adapter layer**
- Freshservice sits behind the same pluggable MCP-style adapter interface as the GitHub, Jira, Confluence, Slack and Freshdesk connectors.
- CodeAtlas uses the live Freshservice adapter when an API key is configured and falls back to mock data otherwise. The other five connectors use mock data for now.

**Not yet integrated**
- **CMDB relationship sync** is designed, but the trial plan does not include CMDB.
- **Official Freshworks MCP server** and **FDK sidebar app** are planned for Phase 2.

Architecture diagrams: [docs/architecture.md](architecture.md)
