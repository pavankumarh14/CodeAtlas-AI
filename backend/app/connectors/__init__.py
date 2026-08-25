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

def get_mcp_adapters() -> Dict[str, BaseMCPAdapter]:
    return {
        "github": GitHubMCPAdapter(),
        "jira": JiraMCPAdapter(),
        "confluence": ConfluenceMCPAdapter(),
        "slack": SlackMCPAdapter(),
        "freshservice": FreshserviceMCPAdapter(),
        "freshdesk": FreshdeskMCPAdapter()
    }
