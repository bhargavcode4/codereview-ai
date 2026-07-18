import requests

from . import config

API_BASE = "https://api.github.com"


def _headers():
    return {
        "Authorization": f"Bearer {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_pr_files(owner: str, repo: str, pr_number: int):
    """Return changed files with their unified diff ('patch') text."""
    url = f"{API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files"
    files, page = [], 1
    while True:
        resp = requests.get(url, headers=_headers(), params={"per_page": 100, "page": page})
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        files.extend(batch)
        page += 1

    # Files with no textual patch (binary, too large, renamed-only) are skipped.
    return [
        {"filename": f["filename"], "status": f["status"], "patch": f.get("patch", "")}
        for f in files
        if f.get("patch")
    ]


def get_pr_head_sha(owner: str, repo: str, pr_number: int) -> str:
    url = f"{API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()
    return resp.json()["head"]["sha"]


def post_review(owner: str, repo: str, pr_number: int, comments: list, summary_body: str):
    """
    Post one PR review containing inline comments.
    comments: list of {"path": str, "line": int, "side": "RIGHT", "body": str}
    """
    commit_id = get_pr_head_sha(owner, repo, pr_number)
    url = f"{API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    payload = {
        "commit_id": commit_id,
        "body": summary_body,
        "event": "COMMENT",
        "comments": comments,
    }
    resp = requests.post(url, headers=_headers(), json=payload)

    if resp.status_code >= 300:
        # GitHub rejects comments whose "line" isn't part of the diff hunk.
        # Fall back to a summary-only comment so the run doesn't hard-fail.
        print(f"Inline review rejected ({resp.status_code}): {resp.text[:500]}")
        fallback = {
            "commit_id": commit_id,
            "body": summary_body + "\n\n_(Inline comments couldn't be placed; see summary above.)_",
            "event": "COMMENT",
        }
        resp = requests.post(url, headers=_headers(), json=fallback)
        resp.raise_for_status()

    return resp.json()
