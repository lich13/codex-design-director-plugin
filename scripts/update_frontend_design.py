#!/usr/bin/env python3
import argparse
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_REPO = "anthropics/claude-code"
DEFAULT_REF = "main"
SOURCE_PATH = "plugins/frontend-design/skills/frontend-design/SKILL.md"
ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "references" / "frontend-design"
TARGET_FILE = FRONTEND_DIR / "SKILL.md"
VERSION_FILE = FRONTEND_DIR / "upstream-version.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def github_json(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "codex-design-md-skill-updater",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub request failed: {url}\n{exc.code} {detail}") from exc


def fetch_skill(repo: str, ref: str) -> tuple[str, str, str]:
    path = urllib.parse.quote(SOURCE_PATH, safe="/")
    encoded_ref = urllib.parse.quote(ref, safe="")
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={encoded_ref}"
    data = github_json(url)
    if data.get("encoding") != "base64":
        raise SystemExit(f"Unexpected GitHub content encoding: {data.get('encoding')}")
    text = base64.b64decode(data["content"]).decode("utf-8")
    return text, data["sha"], data["html_url"]


def write_version(repo: str, ref: str, blob_sha: str, source_url: str) -> None:
    data = {
        "repository": f"https://github.com/{repo}.git",
        "ref": ref,
        "source_path": SOURCE_PATH,
        "source_url": source_url,
        "blob_sha": blob_sha,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    VERSION_FILE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update bundled Anthropic frontend-design skill.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repository, default: {DEFAULT_REPO}")
    parser.add_argument("--ref", default=DEFAULT_REF, help=f"remote ref to track, default: {DEFAULT_REF}")
    parser.add_argument("--check", action="store_true", help="only report whether an update is available")
    parser.add_argument("--force", action="store_true", help="refresh even when the blob sha is unchanged")
    args = parser.parse_args()

    current = read_json(VERSION_FILE)
    text, latest_blob_sha, source_url = fetch_skill(args.repo, args.ref)
    current_blob_sha = current.get("blob_sha")

    if args.check:
        status = "up-to-date" if current_blob_sha == latest_blob_sha else "update-available"
        print(json.dumps({
            "status": status,
            "current_blob_sha": current_blob_sha,
            "latest_blob_sha": latest_blob_sha,
            "repository": f"https://github.com/{args.repo}.git",
            "ref": args.ref,
            "source_path": SOURCE_PATH,
        }, indent=2, sort_keys=True))
        return 0 if status == "up-to-date" else 2

    if current_blob_sha == latest_blob_sha and not args.force:
        print(f"frontend-design already up to date at {latest_blob_sha}")
        return 0

    FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_FILE.write_text(text, encoding="utf-8")
    write_version(args.repo, args.ref, latest_blob_sha, source_url)
    print(f"Updated frontend-design reference to {latest_blob_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
