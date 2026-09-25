from typing import Dict
from .base import BaseMCPAdapter
from .mock_adapters import (
    GitHubMCPAdapter,
    JiraMCPAdapter,
    ConfluenceMCPAdapter,
    SlackMCPAdapter,
    FreshserviceMCPAdapter,
    FreshdeskMCPAdapter
)
from .freshservice import FreshserviceLiveClient, FreshserviceLiveMCPAdapter

def get_mcp_adapters() -> Dict[str, BaseMCPAdapter]:
    freshservice_client = FreshserviceLiveClient()
    return {
        "github": GitHubMCPAdapter(),
        "jira": JiraMCPAdapter(),
        "confluence": ConfluenceMCPAdapter(),
        "slack": SlackMCPAdapter(),
        # Use the live tenant when an API key is configured, otherwise the mocked connector
        "freshservice": FreshserviceLiveMCPAdapter(freshservice_client) if freshservice_client.is_configured else FreshserviceMCPAdapter(),
        "freshdesk": FreshdeskMCPAdapter()
    }
