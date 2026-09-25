import logging
import base64
from typing import List, Dict, Any, Optional
import requests
from ..config import settings

logger = logging.getLogger(__name__)

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
                    "configured_workspace": self.workspace_id
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
        if not self.is_configured:
            return []
        try:
            res = requests.get(f"{self.base_url}/agents/me", headers=self.headers, timeout=10)
            if res.status_code == 200:
                agent = res.json().get("agent", {})
                return agent.get("workspace_ids", [])
        except Exception as e:
            logger.warning(f"Could not retrieve agent workspaces: {e}")
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
            try:
                params: Dict[str, Any] = {"per_page": per_page}
                if ws is not None:
                    params["workspace_id"] = ws

                res = requests.get(f"{self.base_url}/tickets", headers=self.headers, params=params, timeout=10)
                if res.status_code == 200:
                    tickets = res.json().get("tickets", [])
                    for t in tickets:
                        tid = t.get("id")
                        if tid and tid not in seen_ids:
                            seen_ids.add(tid)
                            all_tickets.append(t)
                else:
                    logger.warning(f"Freshservice fetch tickets returned {res.status_code} for workspace {ws}: {res.text}")
            except Exception as e:
                logger.error(f"Failed to fetch tickets from Freshservice (workspace {ws}): {e}")

        return all_tickets

    def get_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Fetch details for a single ticket."""
        if not self.is_configured:
            return None
        try:
            url = f"{self.base_url}/tickets/{ticket_id}"
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                return res.json().get("ticket")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch ticket {ticket_id}: {e}")
            return None

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

    def sync_tickets_to_graph(self, graph_driver) -> Dict[str, Any]:
        """Import real Freshservice tickets into the Knowledge Graph as Incident nodes."""
        tickets = self.get_tickets(per_page=50)
        if not tickets:
            return {"synced": 0, "message": "No tickets retrieved from Freshservice."}

        synced_count = 0
        priority_map = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
        status_map = {2: "Active", 3: "Pending", 4: "Resolved", 5: "Closed"}

        # Fetch existing services to link incidents
        services = []
        try:
            services = graph_driver.get_nodes("Service")
        except Exception as e:
            logger.warning(f"Could not fetch services for linking: {e}")

        for t in tickets:
            ticket_id = t.get("id")
            inc_id = f"FS-{ticket_id}"
            subject = t.get("subject", "Untitled Freshservice Ticket")
            priority = priority_map.get(t.get("priority"), "Medium")
            status = status_map.get(t.get("status"), "Active")
            description = t.get("description_text", "")
            ticket_url = f"https://{self.domain}/helpdesk/tickets/{ticket_id}"

            properties = {
                "inc_id": inc_id,
                "title": f"{inc_id}: {subject}",
                "severity": priority,
                "status": status,
                "root_cause": description[:200] if description else "Imported from Freshservice",
                "source": "Freshservice",
                "url": ticket_url,
                "created_at": t.get("created_at", "")
            }

            # Upsert into Knowledge Graph
            try:
                graph_driver.add_node("Incident", properties)
                synced_count += 1

                # Link to a matching service or primary service if available
                matched_service = None
                text_to_search = f"{subject} {description}".lower()

                keyword_map = {
                    "Payment Gateway Service": ["payment", "gateway", "billing", "stripe", "connection pool", "pool exhausted"],
                    "Notification Service": ["email", "smtp", "sms", "beacon", "notification", "alert delivery"],
                    "Health Monitoring Service": ["health", "monitoring", "telemetry", "guardian", "datahub"],
                    "Alerting Service": ["alerting", "pulse", "command", "pager", "escalation"],
                    "QA Automation Service": ["qa", "automation", "playwright", "test", "pipeline timeout"],
                    "Documentation Service": ["documentation", "docanchor", "doc anchor", "runbook", "stale results"],
                    "Frontend App": ["frontend", "urbannexus", "urban nexus", "login page", "500 error"],
                    "Project Management Service": ["sprint", "velocity", "pilot", "jira", "burndown"],
                    "Market Intelligence Service": ["market", "radar", "market intelligence", "ticker"],
                    "Funding Platform": ["funder", "funding", "investor pledge"]
                }

                # Check keyword alias map first
                for target_svc, keywords in keyword_map.items():
                    if any(kw in text_to_search for kw in keywords):
                        # Verify target service exists in services list
                        for s in services:
                            if s.get("properties", {}).get("name") == target_svc:
                                matched_service = target_svc
                                break
                    if matched_service:
                        break

                # Fallback to direct name matching
                if not matched_service:
                    for s in services:
                        svc_name = s.get("properties", {}).get("name", "")
                        if svc_name and (svc_name.lower() in text_to_search or (svc_name.lower().replace("service", "").strip() in text_to_search and len(svc_name) > 4)):
                            matched_service = svc_name
                            break

                if not matched_service and services:
                    matched_service = services[0].get("properties", {}).get("name")

                if matched_service:
                    try:
                        graph_driver.add_relationship(
                            source_label="Incident", source_name=inc_id,
                            target_label="Service", target_name=matched_service,
                            rel_type="IMPACTS"
                        )
                    except Exception as rel_err:
                        logger.warning(f"Could not link incident {inc_id} to service {matched_service}: {rel_err}")

            except Exception as e:
                logger.error(f"Failed to upsert Freshservice incident {inc_id} to graph: {e}")

        return {
            "synced": synced_count,
            "domain": self.domain,
            "message": f"Successfully synced {synced_count} real tickets from Freshservice into the Knowledge Graph!"
        }
