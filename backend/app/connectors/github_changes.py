import datetime
import logging
import re
import time
from typing import Any, Dict, List, Optional

import requests

from ..config import settings

logger = logging.getLogger(__name__)

API = "https://api.github.com"
CONFIG_SUFFIXES = (".yaml", ".yml", ".json", ".toml", ".ini", ".env", ".properties", ".cfg", ".conf")
NOT_CONFIG = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock")
ISSUE_REF = re.compile(r"(?:(fixes|closes|resolves|refs?)\s+)?#(\d+)", re.IGNORECASE)
TICKET_KEY = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")

_cache: Dict[str, Any] = {}
CACHE_SECONDS = 120


def parse_repo(url: str) -> Optional[str]:
    """'https://github.com/owner/repo(.git)' -> 'owner/repo'."""
    match = re.search(r"github\.com[/:]([^/\s]+)/([^/\s#?]+?)(?:\.git)?/?$", url or "")
    return f"{match.group(1)}/{match.group(2)}" if match else None


def is_config_file(path: str) -> bool:
    name = path.rsplit("/", 1)[-1].lower()
    if name in NOT_CONFIG:
        return False
    return name.endswith(CONFIG_SUFFIXES) or name.startswith(".env") or "config" in path.lower() or "settings" in name


SENSITIVE_KEY = re.compile(r"(key|secret|token|passw|pwd|credential|auth|private)", re.IGNORECASE)
KEY_VALUE = re.compile(r"^([+-]\s*[\"']?)([\w.\-]+)([\"']?\s*[:=]\s*)(.+)$")


def _redact(line: str, mask_all: bool) -> str:
    """Mask config values so secrets never reach a ticket note; keep key names so the change stays readable."""
    match = KEY_VALUE.match(line)
    if match and (mask_all or SENSITIVE_KEY.search(match.group(2))):
        return f"{match.group(1)}{match.group(2)}{match.group(3)}●●●● (redacted)"
    return line


def _diff_lines(patch: str, path: str = "", limit: int = 8) -> List[str]:
    mask_all = path.rsplit("/", 1)[-1].lower().startswith(".env")
    lines = [l for l in (patch or "").splitlines() if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    return [_redact(l, mask_all)[:160] for l in lines[:limit]]


class GitHubChangeClient:
    """Reads recent releases, commits, pull requests and issues for a repository."""

    def __init__(self, token: Optional[str] = None):
        token = token if token is not None else settings.GITHUB_TOKEN
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token.strip()}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            res = requests.get(f"{API}/{path}", headers=self.headers, params=params, timeout=8)
            if res.status_code == 200:
                return res.json()
            if res.status_code == 403 and res.headers.get("X-RateLimit-Remaining") == "0":
                logger.warning("GitHub API rate limit reached; set GITHUB_TOKEN in .env to raise it.")
            elif res.status_code != 404:
                logger.warning(f"GitHub GET {path} returned {res.status_code}")
        except Exception as e:
            logger.error(f"GitHub GET {path} failed: {e}")
        return None

    def latest_release(self, repo: str) -> Optional[Dict[str, Any]]:
        release = self._get(f"repos/{repo}/releases/latest")
        if not release:
            return None
        return {
            "tag": release.get("tag_name"),
            "name": release.get("name") or release.get("tag_name"),
            "published_at": release.get("published_at"),
            "author": (release.get("author") or {}).get("login"),
            "url": release.get("html_url"),
        }

    def _issue(self, repo: str, number: int) -> Optional[Dict[str, Any]]:
        issue = self._get(f"repos/{repo}/issues/{number}")
        if not issue or issue.get("pull_request"):
            return None
        return {"number": number, "title": issue.get("title"), "url": issue.get("html_url"),
                "author": (issue.get("user") or {}).get("login")}

    def recent_changes(self, repo_url: str, days: Optional[int] = None, max_commits: int = 8) -> Optional[Dict[str, Any]]:
        """Summarise what shipped to a repo recently: release, commits, config diffs, linked PRs/issues/tickets."""
        repo = parse_repo(repo_url)
        if not repo:
            return None
        days = days or settings.GITHUB_CHANGE_WINDOW_DAYS
        cache_key = f"{repo}:{days}"
        cached = _cache.get(cache_key)
        if cached and time.time() - cached[0] < CACHE_SECONDS:
            return cached[1]

        since = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        release = self.latest_release(repo)
        commits = self._get(f"repos/{repo}/commits", {"since": since, "per_page": max_commits}) or []

        changes = []
        seen_prs = set()
        for c in commits:
            sha = c["sha"]
            detail = self._get(f"repos/{repo}/commits/{sha}") or {}
            message = c["commit"]["message"]
            files = detail.get("files", [])
            prs = self._get(f"repos/{repo}/commits/{sha}/pulls") or []
            pr = prs[0] if prs else None

            # Collect ticket references from the commit message and the PR body
            ref_text = " ".join([message, (pr or {}).get("title") or "", (pr or {}).get("body") or ""])
            issue_numbers = sorted({int(n) for _, n in ISSUE_REF.findall(ref_text)} - ({pr["number"]} if pr else set()))
            issues = [i for i in (self._issue(repo, n) for n in issue_numbers[:3]) if i]

            released_in = None
            if release and release.get("published_at") and c["commit"]["committer"]["date"] <= release["published_at"]:
                released_in = release["tag"]

            change = {
                "sha": sha[:7],
                "url": c.get("html_url"),
                "author": (c.get("author") or {}).get("login") or c["commit"]["author"]["name"],
                "date": c["commit"]["author"]["date"],
                "message": message.split("\n")[0][:160],
                "released_in": released_in,
                "files_changed": [f["filename"] for f in files][:10],
                "config_changes": [
                    {"file": f["filename"], "diff": _diff_lines(f.get("patch", ""), f["filename"])}
                    for f in files if is_config_file(f["filename"])
                ],
                "pull_request": {
                    "number": pr["number"], "title": pr.get("title"), "url": pr.get("html_url"),
                    "author": (pr.get("user") or {}).get("login"),
                    "merged_by": (pr.get("merged_by") or {}).get("login") if pr.get("merged_by") else None,
                } if pr else None,
                "issues": issues,
                "ticket_keys": sorted(set(TICKET_KEY.findall(ref_text)))[:5],
            }
            # A merge commit and its squashed commits can point to the same PR; keep the richest one
            if pr and pr["number"] in seen_prs and not change["config_changes"]:
                continue
            if pr:
                seen_prs.add(pr["number"])
            changes.append(change)

        summary = {"repository": repo, "url": f"https://github.com/{repo}", "window_days": days,
                   "release": release, "changes": changes}
        _cache[cache_key] = (time.time(), summary)
        return summary


def describe_change(change: Dict[str, Any]) -> str:
    """One-line human summary used in suspected cause and ticket notes."""
    what = f"{change['config_changes'][0]['file']} changed" if change.get("config_changes") else f"'{change['message']}'"
    parts = [f"{what} by {change['author']} ({change['sha']}, {change['date'][:10]})"]
    if change.get("pull_request"):
        parts.append(f"PR #{change['pull_request']['number']}")
    if change.get("issues"):
        parts.append("for " + ", ".join(f"issue #{i['number']} '{i['title']}'" for i in change["issues"]))
    if change.get("ticket_keys"):
        parts.append("ref " + ", ".join(change["ticket_keys"]))
    if change.get("released_in"):
        parts.append(f"shipped in {change['released_in']}")
    return " · ".join(parts)
