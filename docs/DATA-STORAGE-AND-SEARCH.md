# CodeAtlas AI: Storage, Search and Memory (actual vs. planned)

This page separates **what the running demo actually uses** from **what the code supports** and **what is planned**, so nothing is overstated.

## 1. At a glance

| Layer | Used in the demo | Supported in code, not active | Planned |
|---|---|---|---|
| Knowledge graph | **Neo4j 5** (local, Neo4j Desktop) | In-memory graph fallback | Freshservice CMDB as a source |
| Search index | **In-memory keyword index** (TF cosine, word overlap) | **ChromaDB** with embeddings (driver written, package not installed) | Embedding search as the default |
| LLM | **Gemini `gemini-2.5-flash`** via OpenAI-compatible API | OpenAI models; rule-based fallback with no key | Private or self-hosted model option |
| Live external data | **GitHub REST** and **Freshservice REST v2**, fetched per request | — | Freshworks MCP server |
| App memory | **Python lists and dicts in the backend process** | — | Persistent store (e.g. Postgres/Redis) |

**The short version for judges:** Neo4j is real and persistent. Search is keyword-based, not semantic, in this build. ChromaDB is a supported drop-in but not running. GitHub and Freshservice data is live and not stored.

## 2. Neo4j: the knowledge graph (actual)

| Item | Detail |
|---|---|
| What it stores | Services, repositories, APIs, teams, engineers, requirements, runbooks, incidents, and the relationships between them (84 nodes, 106 relationships) |
| Where | `neo4j://127.0.0.1:7687`, set in `.env` (`NEO4J_URI`) |
| Code | [`backend/app/graph/neo4j_driver.py`](../backend/app/graph/neo4j_driver.py) |
| Persistence | ✅ Survives backend restarts |
| How data is written | `MERGE` on a key per label, so re-seeding or re-syncing updates nodes and never duplicates them |
| Who writes | *Seed Real Architecture*, Freshservice Sync, every ticket diagnosis (upserts the ticket as an `Incident`), Repository Intake |
| What it's used for | Dependency traversal (blast radius, upstream causes), ownership and escalation paths, repo lookup for GitHub changes, related incidents, expert lookup |

**Why a graph database:** the core questions are relationship traversals, such as "what depends on this service, two hops out?". Those are single queries in a graph and awkward joins in a table.

**Fallback:** if Neo4j is unreachable, or `FORCE_FALLBACK=true`, the app switches to an in-memory graph ([`in_memory_driver.py`](../backend/app/graph/in_memory_driver.py)). The app still runs, but **all graph data is lost on restart**. The log then says `Falling back to In-Memory Graph Driver`. In the demo, `FORCE_FALLBACK=false` and Neo4j is running.

Full schema and mappings: [KNOWLEDGE-GRAPH.md](KNOWLEDGE-GRAPH.md).

## 3. Search: in-memory keyword index (actual) vs. ChromaDB (supported)

### What actually runs

| Item | Detail |
|---|---|
| Code | [`backend/app/vectorstore/in_memory_driver.py`](../backend/app/vectorstore/in_memory_driver.py) |
| Method | Lower-cases and splits text into words, counts term frequency, ranks by **cosine similarity of word counts** |
| Meaning | It matches **shared words**, not meaning. "SMTP down" finds text containing "SMTP"; it won't find "mail relay outage" unless the words overlap |
| What's indexed | Service descriptions, requirements, runbooks, Freshservice tickets, and files from Repository Intake / ZIP uploads |
| Persistence | ❌ **Emptied on every backend restart.** Click **Seed Real Architecture** to rebuild it |

### Which agents use it

| Agent | Searches for |
|---|---|
| Incident Context | Similar past incidents and runbooks (top 5) |
| Requirement Impact | Related requirements and services (top 3) |
| Ontology Mentor | Docs about the selected service (top 2) |
| Document Q&A | Chunks from uploaded or imported files only (top 8) |

### ChromaDB (supported, not active)

- A driver exists: [`chroma_driver.py`](../backend/app/vectorstore/chroma_driver.py). It uses `chromadb.PersistentClient` in `./chroma_db`, and Chroma's default embedding model gives **true semantic search**.
- At startup the app **tries ChromaDB first**. The `chromadb` package **is not installed** and is not in `requirements.txt`, so it logs a warning and uses the in-memory index.
- Both stores implement the same interface (`add_texts`, `similarity_search`), so no agent code changes are needed to switch.
- **To enable:** `pip install chromadb`, then restart and re-seed. The first run downloads an embedding model.

**Caveat:** some agent trace messages say "semantic search" (e.g. Document Q&A). In this build that search is keyword-based. Say "search" rather than "semantic search" in the demo.

## 4. Live data: fetched, not stored (actual)

| Source | What's fetched | When | Stored? |
|---|---|---|---|
| **GitHub REST API** | Recent releases, commits, config-file diffs (secrets masked), linked PRs/issues for the repo that implements the matched service | Per diagnosis | ❌ Cached in memory for **2 minutes** only (`CACHE_SECONDS = 120` in [`github_changes.py`](../backend/app/connectors/github_changes.py)) |
| **Freshservice REST v2** | Ticket/change details, KB (Solutions) articles, related tickets, groups | Per diagnosis / sync | Tickets and groups are **written to Neo4j**; KB articles are not stored |
| **Gemini** | LLM reasoning over the gathered evidence | Per agent call | ❌ Not stored |

**GitHub rate limit:** without `GITHUB_TOKEN`, GitHub allows 60 requests/hour, and one diagnosis uses roughly 10–20. When the limit runs out, the "recent change" evidence quietly disappears from notes. **`GITHUB_TOKEN` is not currently set in `.env`.** Add a read-only token before the demo.

## 5. Application memory (actual)

These live only in the backend process:

| Data | Where | Survives restart? |
|---|---|---|
| Agent Activity Log | `activity_log` list in [`main.py`](../backend/app/main.py) | ❌ |
| Search index | In-memory store (section 3) | ❌ |
| GitHub response cache | `_cache` dict, 2-minute TTL | ❌ |
| Agent "memory" between runs | **None.** Each run starts fresh and reads the graph, search index and live APIs | n/a |

The agents have **no conversational or long-term memory of their own**. Everything they "know" comes from Neo4j, the search index and live API calls on each run. Anything persistent about past incidents lives in Neo4j as `Incident` nodes.

## 6. What survives a restart

| After a backend restart | State |
|---|---|
| Neo4j graph (services, repos, teams, incidents…) | ✅ Intact |
| Freshservice notes, routing and group assignments | ✅ Intact (stored in Freshservice) |
| Search index | ❌ Empty until **Seed Real Architecture** is clicked |
| Agent Activity Log | ❌ Empty |
| GitHub cache | ❌ Empty (refilled on the next diagnosis) |

`AUTO_SEED=false` in `.env`, so the app never re-seeds on its own. Seeding is always the explicit **Seed Real Architecture** click.

## 7. Configuration flags

| Flag (`.env`) | Current value | Effect |
|---|---|---|
| `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` | `neo4j://127.0.0.1:7687` / set / set | Neo4j connection |
| `FORCE_FALLBACK` | `false` | `true` forces in-memory graph and search (no Neo4j or Chroma) |
| `AUTO_SEED` | `false` | `true` seeds sample data at startup if the graph is empty |
| `GEMINI_API_KEY` | set | Enables LLM reasoning; without it agents use rule-based answers |
| `GITHUB_TOKEN` | **not set** | Raises the GitHub rate limit from 60 to 5,000 requests/hour |

## 8. How to describe it to judges

> "The knowledge graph is Neo4j, and it's persistent. That's where services, owners, dependencies and incidents live, and blast radius is a graph traversal. GitHub commits and Freshservice KB articles are fetched live on each diagnosis, not stored. Retrieval in this build is a lightweight in-memory keyword index; ChromaDB with real embeddings is already wired behind the same interface and is a one-package switch. The agents don't have hidden memory. Everything they conclude is traceable to the graph, a commit or a KB article."

## 9. Likely questions

**"Is it RAG?"** Yes, in the plain sense: agents retrieve evidence (graph traversal, keyword search, live GitHub/Freshservice data) and the LLM reasons over it. The retrieval step is keyword-based, not embedding-based, in this build.

**"Why not embeddings now?"** For zero-setup local runs and predictable results. The graph does most of the precise work, since service matching, dependencies and ownership are structured lookups, not fuzzy search. Embeddings would mainly improve finding similar past incidents with different wording.

**"What happens if Neo4j goes down?"** The app keeps running on the in-memory graph, but data isn't persisted until Neo4j is back.

**"Where would this go in production?"** Neo4j (or Neo4j Aura) for the graph, ChromaDB or a managed vector database for search, a persistent store for the activity log, and the Freshservice CMDB plus repo manifests as the source of the service layer.
