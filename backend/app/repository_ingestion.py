"""Safe, read-only inspection for public GitHub repositories."""
from typing import Any, Dict, List
from urllib.parse import urlparse
import re

import requests

GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "CodeAtlas-AI"}
MANIFEST_NAMES = {"package.json", "pyproject.toml", "requirements.txt", "go.mod", "pom.xml", "cargo.toml", "dockerfile", "docker-compose.yml"}
DOC_SUFFIXES = (".md", ".mdx", ".rst")


def parse_public_github_url(repository_url: str) -> tuple[str, str]:
    parsed = urlparse(repository_url.strip())
    if parsed.scheme != "https" or parsed.hostname not in {"github.com", "www.github.com"}:
        raise ValueError("Use a public HTTPS GitHub URL, for example https://github.com/owner/repository.")
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2 or not re.fullmatch(r"[A-Za-z0-9_.-]+", parts[0]) or not re.fullmatch(r"[A-Za-z0-9_.-]+", parts[1].removesuffix(".git")):
        raise ValueError("The GitHub URL must include an owner and repository name.")
    return parts[0], parts[1].removesuffix(".git")


def _github_get(path: str) -> Any:
    response = requests.get(f"{GITHUB_API}{path}", headers=HEADERS, timeout=15)
    if response.status_code == 404:
        raise ValueError("Repository not found. Confirm it is public and the URL is correct.")
    if response.status_code == 403:
        raise ValueError("GitHub temporarily rate-limited this public lookup. Please try again shortly.")
    response.raise_for_status()
    return response.json()


def inspect_public_repository(repository_url: str) -> Dict[str, Any]:
    owner, repository = parse_public_github_url(repository_url)
    metadata = _github_get(f"/repos/{owner}/{repository}")
    branch = metadata.get("default_branch", "main")
    tree = _github_get(f"/repos/{owner}/{repository}/git/trees/{branch}?recursive=1")
    paths = [entry["path"] for entry in tree.get("tree", []) if entry.get("type") == "blob"][:1000]

    manifests = [path for path in paths if path.rsplit("/", 1)[-1].lower() in MANIFEST_NAMES][:12]
    documents = [path for path in paths if path.lower().endswith(DOC_SUFFIXES)][:12]
    api_candidates = [path for path in paths if re.search(r"(^|/)(api|routes?|controllers?)(/|$)|/(route|controller)\.", path, re.IGNORECASE)][:12]
    languages = _github_get(f"/repos/{owner}/{repository}/languages")

    return {
        "repository": f"{owner}/{repository}",
        "url": metadata["html_url"],
        "description": metadata.get("description") or "No repository description provided.",
        "default_branch": branch,
        "languages": list(languages.keys())[:8],
        "files_scanned": len(paths),
        "tree_truncated": bool(tree.get("truncated")),
        "manifests": manifests,
        "documents": documents,
        "api_candidates": api_candidates,
    }
