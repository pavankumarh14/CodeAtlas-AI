import logging
import base64
import re
from typing import List, Dict, Any, Optional
import requests
from ..config import settings
from .base import BaseMCPAdapter

logger = logging.getLogger(__name__)

PRIORITY_MAP = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
STATUS_MAP = {2: "Active", 3: "Pending", 4: "Resolved", 5: "Closed"}

# Aliases used to link free-text ticket subjects to Service nodes in the ontology
SERVICE_KEYWORDS = {
    "Payment Gateway Service": ["payment", "gateway", "billing", "stripe", "connection pool", "pool exhausted"],
    "Notification Service": ["email", "smtp", "sms", "beacon", "notification", "alert delivery"],
    "Health Monitoring Service": ["health", "monitoring", "telemetry", "guardian", "datahub"],
    "Alerting Service": ["alerting", "alert", "pulse", "command", "pager", "escalation", "on-call", "oncall"],
    "QA Automation Service": ["qa", "automation", "playwright", "test", "pipeline timeout"],
    "Documentation Service": ["documentation", "docanchor", "doc anchor", "runbook", "stale results"],
    "Frontend App": ["frontend", "urbannexus", "urban nexus", "login page", "500 error"],
    "Project Management Service": ["sprint", "velocity", "pilot", "jira", "burndown"],
    "Market Intelligence Service": ["market", "radar", "market intelligence", "ticker"],
    "Funding Platform": ["funder", "funding", "investor pledge"]
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are", "was", "with", "my",
    "what", "whats", "wrong", "why", "how", "investigate", "details", "diagnose", "request", "this", "that", "it"
}


def match_service(text: str, service_names: List[str]) -> Optional[str]:
    """Map free text (ticket subject/description) to a known Service name, or None."""
    text = text.lower()
    known = set(service_names)
    # Score every service so the one with the most keyword hits wins, not the first listed
    scores = {
        svc: sum(1 for kw in keywords if kw in text)
        for svc, keywords in SERVICE_KEYWORDS.items() if svc in known
    }
    best = max(scores, key=scores.get, default=None)
    if best and scores[best] > 0:
        return best
    for svc_name in service_names:
        short = svc_name.lower().replace("service", "").strip()
        if svc_name.lower() in text or (len(short) > 4 and short in text):
            return svc_name
    return None


def _tokens(text: str) -> set:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2 and t not in STOPWORDS}


class FreshserviceLiveClient:
    """Official Freshservice REST v2 Client for CodeAtlas AI."""

    def __init__(self, domain: Optional[str] = None, api_key: Optional[str] = None, workspace_id: Optional[str] = None):
        self.domain = domain or settings.FRESHSERVICE_DOMAIN or "freshworks065.freshservice.com"
        # Strip protocol if present
        if "://" in self.domain:
            self.domain = self.domain.split("://")[1].rstrip("/")
        self.api_key = api_key or settings.FRESHSERVICE_API_KEY
        self.workspace_id = workspace_id or getattr(settings, "FRESHSERVICE_WORKSPACE_ID", "") or ""
        self.base_url = f"https://{self.domain}/api/v2"

        self.is_configured = bool(self.api_key and self.api_key.strip())

        if self.is_configured:
            # Freshworks HTTP Basic Auth: API_KEY as username, 'X' as password
            auth_bytes = f"{self.api_key.strip()}:X".encode("utf-8")
            self.headers = {
                "Authorization": f"Basic {base64.b64encode(auth_bytes).decode('utf-8')}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = {"Content-Type": "application/json"}

    def ticket_url(self, ticket_id: Any) -> str:
        return f"https://{self.domain}/helpdesk/tickets/{ticket_id}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """GET a v2 resource; returns parsed JSON or None on any failure."""
        if not self.is_configured:
            return None
        try:
            res = requests.get(f"{self.base_url}/{path}", headers=self.headers, params=params, timeout=10)
            if res.status_code == 200:
                return res.json()
            logger.warning(f"Freshservice GET {path} returned {res.status_code}: {res.text[:200]}")
        except Exception as e:
            logger.error(f"Freshservice GET {path} failed: {e}")
        return None

    def test_connection(self) -> Dict[str, Any]:
        """Verify API key and connectivity with Freshservice tenant."""
        if not self.is_configured:
            return {"status": "unconfigured", "message": "FRESHSERVICE_API_KEY is not set in .env"}
        try:
            url = f"{self.base_url}/tickets?per_page=1"
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                workspaces = self.get_assigned_workspaces()
                return {
                    "status": "connected",
                    "domain": self.domain,
                    "http_status": 200,
                    "workspaces": workspaces,
                    "configured_workspace": self.workspace_id,
                    "webhook_url": "/api/v1/freshworks/webhook"
                }
            elif res.status_code == 401:
                return {"status": "unauthorized", "message": "Invalid Freshservice API Key", "http_status": 401}
            else:
                return {"status": "error", "message": f"Freshservice returned HTTP {res.status_code}", "body": res.text}
        except Exception as e:
            logger.error(f"Error testing Freshservice connection: {e}")
            return {"status": "connection_error", "message": str(e)}

    def get_assigned_workspaces(self) -> List[int]:
        """Auto-discover workspaces assigned to the authenticated user."""
        data = self._get("agents/me")
        if data:
            return data.get("agent", {}).get("workspace_ids", [])
        return []

    def get_tickets(self, per_page: int = 30) -> List[Dict[str, Any]]:
        """Fetch real tickets/incidents from Freshservice across assigned workspaces."""
        if not self.is_configured:
            return []

        all_tickets: List[Dict[str, Any]] = []
        seen_ids = set()

        # Build workspace candidates list
        workspace_candidates: List[Optional[int]] = []
        if self.workspace_id:
            try:
                workspace_candidates.append(int(self.workspace_id))
            except ValueError:
                pass

        # Auto-discover workspaces from agent profile
        discovered = self.get_assigned_workspaces()
        for wid in discovered:
            if wid not in workspace_candidates:
                workspace_candidates.append(wid)

        # Fallback to querying without workspace_id
        if None not in workspace_candidates:
            workspace_candidates.append(None)

        for ws in workspace_candidates:
            params: Dict[str, Any] = {"per_page": per_page}
            if ws is not None:
                params["workspace_id"] = ws
            data = self._get("tickets", params)
            for t in (data or {}).get("tickets", []):
                tid = t.get("id")
                if tid and tid not in seen_ids:
                    seen_ids.add(tid)
                    all_tickets.append(t)

        return all_tickets

    def get_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Fetch details for a single ticket."""
        data = self._get(f"tickets/{ticket_id}")
        return data.get("ticket") if data else None

    def get_conversations(self, ticket_id: int) -> List[Dict[str, Any]]:
        """Fetch replies and notes on a ticket."""
        data = self._get(f"tickets/{ticket_id}/conversations")
        return data.get("conversations", []) if data else []

    def get_groups(self) -> List[Dict[str, Any]]:
        """Fetch agent groups (support teams) in the configured workspace."""
        params = {"per_page": 100}
        if self.workspace_id:
            params["workspace_id"] = self.workspace_id
        data = self._get("groups", params)
        return data.get("groups", []) if data else []

    def search_tickets(self, query: str, limit: int = 5, min_score: float = 0.2) -> List[Dict[str, Any]]:
        """Rank recent tickets by keyword overlap with the query (the filter API has no full-text search)."""
        query_tokens = _tokens(query)
        if not query_tokens:
            return []
        scored = []
        for t in self.get_tickets(per_page=100):
            overlap = query_tokens & _tokens(f"{t.get('subject', '')} {t.get('description_text', '')}")
            score = len(overlap) / len(query_tokens)
            if score >= min_score:
                scored.append((score, t))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [{**t, "match_score": round(score, 2)} for score, t in scored[:limit]]

    def search_solution_articles(self, term: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search the Freshservice knowledge base (Solutions) for runbook-style articles."""
        results: List[Dict[str, Any]] = []
        seen_titles = set()
        # The search endpoint matches whole terms, so try the most specific keywords individually
        for keyword in sorted(_tokens(term), key=len, reverse=True)[:4]:
            data = self._get("solutions/articles/search", {"search_term": keyword})
            for article in (data or {}).get("articles", []):
                if self.workspace_id and str(article.get("workspace_id")) != str(self.workspace_id):
                    continue
                if article.get("title") in seen_titles:
                    continue
                seen_titles.add(article.get("title"))
                results.append({
                    "id": article.get("id"),
                    "title": article.get("title"),
                    "summary": re.sub(r"(&nbsp;|\s)+", " ", article.get("description_text") or "").strip()[:300],
                    "url": f"https://{self.domain}/support/solutions/articles/{article.get('id')}"
                })
            if len(results) >= limit:
                break
        return results[:limit]

    def add_note_to_ticket(self, ticket_id: int, note_html: str, private: bool = True) -> bool:
        """Post a diagnosis note or triage response back into the Freshservice ticket."""
        if not self.is_configured:
            return False
        try:
            url = f"{self.base_url}/tickets/{ticket_id}/notes"
            payload = {
                "body": note_html,
                "private": private
            }
            res = requests.post(url, headers=self.headers, json=payload, timeout=10)
            if res.status_code in (200, 201):
                logger.info(f"Successfully posted note to Freshservice ticket #{ticket_id}")
                return True
            logger.error(f"Failed to post note to Freshservice ticket #{ticket_id}: {res.status_code} {res.text}")
            return False
        except Exception as e:
            logger.error(f"Exception posting note to Freshservice ticket: {e}")
            return False

    def upsert_ticket(self, ticket: Dict[str, Any], graph_driver, vector_store=None,
                      service_names: Optional[List[str]] = None, group_names: Optional[Dict[int, str]] = None) -> str:
        """Write one ticket into the graph (and vector index) as an Incident node. Returns its inc_id."""
        ticket_id = ticket.get("id")
        inc_id = f"FS-{ticket_id}"
        subject = ticket.get("subject", "Untitled Freshservice Ticket")
        description = ticket.get("description_text", "") or ""

        graph_driver.add_node("Incident", {
            "inc_id": inc_id,
            "title": f"{inc_id}: {subject}",
            "severity": PRIORITY_MAP.get(ticket.get("priority"), "Medium"),
            "status": STATUS_MAP.get(ticket.get("status"), "Active"),
            "ticket_type": ticket.get("type") or "Incident",
            "root_cause": description[:200] if description else "Imported from Freshservice",
            "source": "Freshservice",
            "url": self.ticket_url(ticket_id),
            "created_at": ticket.get("created_at", "")
        })

        if service_names is None:
            service_names = [s.get("properties", {}).get("name", "") for s in graph_driver.get_nodes("Service")]
        matched_service = match_service(f"{subject} {description}", [n for n in service_names if n])
        if matched_service:
            graph_driver.add_relationship("Incident", inc_id, "Service", matched_service, "IMPACTS")

        group_name = (group_names or {}).get(ticket.get("group_id"))
        if group_name:
            graph_driver.add_relationship("Incident", inc_id, "Team", group_name, "ESCALATED_TO")

        if vector_store is not None:
            vector_store.add_texts(
                texts=[f"Freshservice {ticket.get('type') or 'Incident'} {inc_id}: {subject}. {description[:1000]}"
                       + (f" Affected service: {matched_service}." if matched_service else "")],
                metadatas=[{"type": "Incident", "id": inc_id, "source": "Freshservice", "url": self.ticket_url(ticket_id)}],
                ids=[inc_id]
            )
        return inc_id

    def sync_tickets_to_graph(self, graph_driver, vector_store=None) -> Dict[str, Any]:
        """Import Freshservice groups as Teams and tickets as Incident nodes in the Knowledge Graph."""
        tickets = self.get_tickets(per_page=50)
        if not tickets:
            return {"synced": 0, "message": "No tickets retrieved from Freshservice."}

        group_names: Dict[int, str] = {}
        for g in self.get_groups():
            group_names[g["id"]] = g["name"]
            graph_driver.add_node("Team", {
                "name": g["name"],
                "description": g.get("description") or "",
                "source": "Freshservice"
            })

        service_names = []
        try:
            service_names = [s.get("properties", {}).get("name", "") for s in graph_driver.get_nodes("Service")]
        except Exception as e:
            logger.warning(f"Could not fetch services for linking: {e}")

        synced_count = 0
        for t in tickets:
            try:
                self.upsert_ticket(t, graph_driver, vector_store, service_names, group_names)
                synced_count += 1
            except Exception as e:
                logger.error(f"Failed to upsert Freshservice ticket {t.get('id')} to graph: {e}")

        return {
            "synced": synced_count,
            "groups": len(group_names),
            "domain": self.domain,
            "message": f"Successfully synced {synced_count} tickets and {len(group_names)} support groups from Freshservice into the Knowledge Graph!"
        }


class FreshserviceLiveMCPAdapter(BaseMCPAdapter):
    """MCP-style adapter backed by the live Freshservice REST v2 API."""

    def __init__(self, client: Optional[FreshserviceLiveClient] = None):
        self.client = client or FreshserviceLiveClient()

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Freshservice MCP Connector",
            "type": "ITSM",
            "mode": "live",
            "domain": self.client.domain,
            "capabilities": ["search_tickets", "fetch_incident", "search_solution_articles", "add_note"]
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        return [
            {
                "id": f"FS-{t['id']}",
                "subject": t.get("subject"),
                "impact": PRIORITY_MAP.get(t.get("priority"), "Medium"),
                "state": STATUS_MAP.get(t.get("status"), "Active"),
                "score": t.get("match_score", 0),
                "url": self.client.ticket_url(t["id"])
            }
            for t in self.client.search_tickets(query)
        ]

    def search_articles(self, query: str) -> List[Dict[str, Any]]:
        return self.client.search_solution_articles(query)

    def fetch(self, item_id: str) -> Dict[str, Any]:
        ticket_id = int(str(item_id).replace("FS-", ""))
        ticket = self.client.get_ticket(ticket_id) or {}
        notes = [re.sub(r"<[^>]+>", " ", c.get("body", "")) for c in self.client.get_conversations(ticket_id)]
        return {
            "id": f"FS-{ticket_id}",
            "subject": ticket.get("subject"),
            "impact": PRIORITY_MAP.get(ticket.get("priority"), "Medium"),
            "state": STATUS_MAP.get(ticket.get("status"), "Active"),
            "details": ticket.get("description_text", ""),
            "notes": " | ".join(n.strip() for n in notes if n.strip())[:1000]
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        ticket_id = str(raw_data.get("id", "")).replace("FS-", "")
        return {
            "title": f"{raw_data.get('id')}: {raw_data.get('subject')}",
            "type": "Incident",
            "content": f"Freshservice Incident: {raw_data.get('subject')}\nImpact: {raw_data.get('impact')}\nState: {raw_data.get('state')}\nDetails: {raw_data.get('details')}",
            "url": self.client.ticket_url(ticket_id)
        }
