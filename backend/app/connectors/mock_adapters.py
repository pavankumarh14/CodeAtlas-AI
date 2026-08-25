from typing import List, Dict, Any
from .base import BaseMCPAdapter
import logging

logger = logging.getLogger(__name__)

class GitHubMCPAdapter(BaseMCPAdapter):
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "GitHub MCP Connector",
            "type": "VCS",
            "capabilities": ["search_repositories", "fetch_pull_requests", "list_commits"]
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        # Mock search results for PRs / Repositories
        logger.info(f"GitHub search query: {query}")
        mock_data = [
            {
                "id": "PR-401",
                "title": "feat: Add payment authorization retry logic",
                "repo": "payment-api",
                "author": "john.doe",
                "status": "merged",
                "updated_at": "2026-08-20T10:00:00Z"
            },
            {
                "id": "PR-402",
                "title": "fix: checkout cart loading performance issue",
                "repo": "checkout-api",
                "author": "sarah.smith",
                "status": "open",
                "updated_at": "2026-08-24T15:30:00Z"
            }
        ]
        return [item for item in mock_data if query.lower() in item["title"].lower() or query.lower() in item["repo"].lower()]

    def fetch(self, item_id: str) -> Dict[str, Any]:
        return {
            "id": item_id,
            "title": "feat: Add payment authorization retry logic" if item_id == "PR-401" else "fix: checkout cart loading performance issue",
            "repo": "payment-api" if item_id == "PR-401" else "checkout-api",
            "author": "john.doe" if item_id == "PR-401" else "sarah.smith",
            "status": "merged" if item_id == "PR-401" else "open",
            "diff": "@@ -12,4 +12,12 @@\n+ retry_count = 0\n+ while retry_count < 3:\n+     try:\n+         return call_payment_gateway(payload)\n+     except GatewayTimeout:\n+         retry_count += 1",
            "comments": [{"author": "alex.architect", "body": "Make sure to add backoff."}]
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("title"),
            "type": "Document",
            "content": f"GitHub PR {raw_data.get('id')} in {raw_data.get('repo')} by {raw_data.get('author')}. Status: {raw_data.get('status')}.\nDiff:\n{raw_data.get('diff')}",
            "url": f"https://github.com/org/{raw_data.get('repo')}/pull/{raw_data.get('id')}"
        }


class JiraMCPAdapter(BaseMCPAdapter):
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Jira MCP Connector",
            "type": "IssueTracker",
            "capabilities": ["search_issues", "fetch_issue", "transition_issue"]
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Jira search query: {query}")
        mock_data = [
            {
                "id": "REQ-65",
                "summary": "Implement WhatsApp Notifications for Order Status",
                "assignee": "emma.jones",
                "priority": "High",
                "status": "In Progress"
            },
            {
                "id": "REQ-120",
                "summary": "Migrate payment tokens database to new schema",
                "assignee": "john.doe",
                "priority": "Critical",
                "status": "To Do"
            }
        ]
        return [item for item in mock_data if query.lower() in item["summary"].lower() or query.lower() in item["id"].lower()]

    def fetch(self, item_id: str) -> Dict[str, Any]:
        return {
            "id": item_id,
            "summary": "Implement WhatsApp Notifications for Order Status" if item_id == "REQ-65" else "Migrate payment tokens database to new schema",
            "description": "We need to send real-time order status updates via WhatsApp to improve delivery success rates. Depends on notifications-service and whatsapp-gateway-api.",
            "assignee": "emma.jones" if item_id == "REQ-65" else "john.doe",
            "reporter": "david.product",
            "priority": "High" if item_id == "REQ-65" else "Critical",
            "status": "In Progress" if item_id == "REQ-65" else "To Do",
            "subtasks": ["Create API schemas", "Implement webhooks in order-service"]
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": f"{raw_data.get('id')}: {raw_data.get('summary')}",
            "type": "Requirement",
            "content": f"Jira Issue: {raw_data.get('summary')}\nStatus: {raw_data.get('status')}\nAssignee: {raw_data.get('assignee')}\nDescription: {raw_data.get('description')}",
            "url": f"https://jira.company.com/browse/{raw_data.get('id')}"
        }


class ConfluenceMCPAdapter(BaseMCPAdapter):
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Confluence MCP Connector",
            "type": "Documentation",
            "capabilities": ["search_pages", "fetch_page"]
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Confluence search query: {query}")
        mock_data = [
            {
                "id": "CONF-901",
                "title": "Payment gateway integrations runbook",
                "space": "ENGINEERING",
                "last_modified": "2026-07-15T09:00:00Z"
            },
            {
                "id": "CONF-902",
                "title": "Checkout latency mitigation guidelines",
                "space": "OPS",
                "last_modified": "2026-08-22T11:45:00Z"
            }
        ]
        return [item for item in mock_data if query.lower() in item["title"].lower()]

    def fetch(self, item_id: str) -> Dict[str, Any]:
        is_payment = item_id == "CONF-901"
        return {
            "id": item_id,
            "title": "Payment gateway integrations runbook" if is_payment else "Checkout latency mitigation guidelines",
            "space": "ENGINEERING" if is_payment else "OPS",
            "body": "Step 1: Check Stripe/Adyen status pages.\nStep 2: Inspect checkout-api service logs for GatewayTimeout.\nStep 3: Toggle circuit breaker in payment-service config panel." if is_payment else "Step 1: Inspect Redis cache hit rates.\nStep 2: Scale up replica pods of inventory-db.\nStep 3: Check database connection pool exhaustion in checkout-api.",
            "author": "alex.architect" if is_payment else "sam.reliability"
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("title"),
            "type": "Document",
            "content": f"Confluence Wiki Page ({raw_data.get('space')} space):\n{raw_data.get('body')}",
            "url": f"https://confluence.company.com/display/{raw_data.get('space')}/{raw_data.get('title').replace(' ', '+')}"
        }


class SlackMCPAdapter(BaseMCPAdapter):
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Slack MCP Connector",
            "type": "Communication",
            "capabilities": ["search_messages", "list_channels"]
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Slack search query: {query}")
        mock_data = [
            {
                "channel": "ops-alerts",
                "user": "alertmanager-bot",
                "text": "CRITICAL - checkout-api latency is above 2000ms. Affected business capability: Commerce Checkout.",
                "timestamp": "2026-08-25T10:15:00Z"
            },
            {
                "channel": "dev-commerce",
                "user": "alex.architect",
                "text": "It seems Stripe API is returning 504 Gateway Timeout. I am switching the circuit breaker.",
                "timestamp": "2026-08-25T10:20:00Z"
            }
        ]
        return [item for item in mock_data if query.lower() in item["text"].lower()]

    def fetch(self, item_id: str) -> Dict[str, Any]:
        # Return context around a message
        return {
            "channel": "dev-commerce",
            "conversation": [
                {"user": "alertmanager-bot", "text": "checkout-api latency is high."},
                {"user": "alex.architect", "text": "It seems Stripe API is returning 504. Switching circuit breaker."},
                {"user": "sam.reliability", "text": "Thanks Alex, circuit breaker flipped, latency returning to baseline."}
            ]
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        conv_text = "\n".join([f"[{msg.get('user')}]: {msg.get('text')}" for msg in raw_data.get("conversation", [])])
        return {
            "title": f"Slack conversation in #{raw_data.get('channel')}",
            "type": "Document",
            "content": f"Slack Chat Context:\n{conv_text}",
            "url": f"https://slack.com/archives/{raw_data.get('channel')}"
        }


class FreshserviceMCPAdapter(BaseMCPAdapter):
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Freshservice MCP Connector",
            "type": "ITSM",
            "capabilities": ["search_tickets", "fetch_incident"]
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Freshservice query: {query}")
        mock_data = [
            {
                "id": "INC-101",
                "subject": "Checkout failure during peak hours",
                "impact": "High",
                "state": "Resolved"
            },
            {
                "id": "INC-212",
                "subject": "Payment API Gateway Timeout",
                "impact": "Critical",
                "state": "Active"
            }
        ]
        return [item for item in mock_data if query.lower() in item["subject"].lower() or query.lower() in item["id"].lower()]

    def fetch(self, item_id: str) -> Dict[str, Any]:
        is_101 = item_id == "INC-101"
        return {
            "id": item_id,
            "subject": "Checkout failure during peak hours" if is_101 else "Payment API Gateway Timeout",
            "impact": "High" if is_101 else "Critical",
            "state": "Resolved" if is_101 else "Active",
            "urgency": "High",
            "details": "Users were receiving 500 Internal Server Error when completing checkouts. Root cause was db connection pool exhaustion in database inventory-db." if is_101 else "Stripe API response times exceeded 5000ms causing checkout-api threads to pile up and exhaust memory.",
            "notes": "Added cache layers to inventory-db query" if is_101 else "Contacting Stripe account representative."
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": f"{raw_data.get('id')}: {raw_data.get('subject')}",
            "type": "Incident",
            "content": f"Freshservice Incident: {raw_data.get('subject')}\nImpact: {raw_data.get('impact')}\nState: {raw_data.get('state')}\nDetails: {raw_data.get('details')}",
            "url": f"https://freshservice.company.com/itil/tickets/{raw_data.get('id')}"
        }


class FreshdeskMCPAdapter(BaseMCPAdapter):
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Freshdesk MCP Connector",
            "type": "CustomerSupport",
            "capabilities": ["search_tickets", "fetch_ticket"]
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Freshdesk query: {query}")
        mock_data = [
            {
                "id": "TICKET-12",
                "subject": "Charged twice for my checkout order",
                "status": "Open",
                "customer": "alice.consumer@gmail.com"
            }
        ]
        return [item for item in mock_data if query.lower() in item["subject"].lower()]

    def fetch(self, item_id: str) -> Dict[str, Any]:
        return {
            "id": item_id,
            "subject": "Charged twice for my checkout order",
            "status": "Open",
            "customer": "alice.consumer@gmail.com",
            "description": "I clicked 'Checkout' and the page hung. I clicked it again, and now my credit card shows two charges for the same order.",
            "agent": "support.alex"
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": f"{raw_data.get('id')}: {raw_data.get('subject')}",
            "type": "Document",
            "content": f"Freshdesk Customer Ticket: {raw_data.get('subject')}\nFrom: {raw_data.get('customer')}\nProblem: {raw_data.get('description')}",
            "url": f"https://freshdesk.company.com/support/tickets/{raw_data.get('id')}"
        }
