#!/usr/bin/env python3
"""Sync Design Director bundled upstream references."""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = PLUGIN_ROOT / "references"
UPSTREAMS = REFERENCES / "upstreams"
LICENSES = PLUGIN_ROOT / "licenses"

AWESOME_REPO = "https://github.com/VoltAgent/awesome-design-md.git"
HERMES_REPO = "https://github.com/NousResearch/hermes-agent.git"
FRONTEND_REPO = "anthropics/claude-code"
FRONTEND_SOURCE_PATH = "plugins/frontend-design/skills/frontend-design/SKILL.md"


def run(cmd: list[str], cwd: Path | None = None) -> str:
    last_message = ""
    for attempt in range(1, 4):
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        last_message = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        if attempt < 3:
            time.sleep(attempt)
    raise SystemExit(f"Command failed after 3 attempts: {' '.join(cmd)}\n{last_message}")


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_metadata(path: Path, data: dict, identity_keys: tuple[str, ...]) -> dict:
    current = read_json(path)
    unchanged = current and all(current.get(key) == data.get(key) for key in identity_keys)
    result = dict(data)
    result["updated_at"] = current.get("updated_at") if unchanged and current.get("updated_at") else timestamp()
    return result


def copytree_replace(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def guard_count_change(name: str, previous: int | None, current: int, allow_large_count_change: bool) -> None:
    if previous in (None, 0) or allow_large_count_change:
        return
    low = max(1, int(previous * 0.75))
    high = max(low, int(previous * 1.5))
    if current < low or current > high:
        raise SystemExit(
            f"{name} count changed unexpectedly: previous={previous} current={current}. "
            "Inspect upstream before rerunning with --allow-large-count-change."
        )


def ls_remote_head(repo: str, ref: str = "HEAD") -> str:
    output = run(["git", "ls-remote", repo, ref])
    sha = output.split()[0] if output else ""
    if not sha:
        raise SystemExit(f"No remote ref found for {repo} {ref}")
    return sha


def clone(repo: str, target: Path) -> None:
    run(["git", "clone", "--depth=1", repo, str(target)])


def sync_awesome_design_md(allow_large_count_change: bool) -> None:
    meta_path = UPSTREAMS / "awesome-design-md.json"
    legacy_meta_path = REFERENCES / "upstream-version.json"
    latest = ls_remote_head(AWESOME_REPO)
    current = read_json(meta_path).get("commit") or read_json(legacy_meta_path).get("commit")
    if current == latest and (REFERENCES / "design-md").exists() and (LICENSES / "VoltAgent-awesome-design-md-MIT.txt").exists():
        print(f"awesome-design-md already up to date: {latest}")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = Path(temp_dir) / "awesome-design-md"
        clone(AWESOME_REPO, repo_dir)
        latest = run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
        source_design_dir = repo_dir / "design-md"
        source_license = repo_dir / "LICENSE"
        if not source_design_dir.is_dir():
            raise SystemExit("awesome-design-md is missing design-md/")
        if not source_license.is_file():
            raise SystemExit("awesome-design-md is missing LICENSE")

        previous_count = read_json(meta_path).get("design_md_count") or read_json(legacy_meta_path).get("design_md_count")
        copytree_replace(source_design_dir, REFERENCES / "design-md")
        LICENSES.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_license, LICENSES / "VoltAgent-awesome-design-md-MIT.txt")
        shutil.copy2(source_license, REFERENCES / "upstream-license.txt")
        if (repo_dir / "README.md").exists():
            shutil.copy2(repo_dir / "README.md", REFERENCES / "upstream-readme.md")

        design_count = len(list((REFERENCES / "design-md").glob("*/DESIGN.md")))
        guard_count_change("DESIGN.md", previous_count, design_count, allow_large_count_change)
        metadata = {
            "name": "awesome-design-md",
            "repository": AWESOME_REPO,
            "ref": "HEAD",
            "commit": latest,
            "source_path": "design-md",
            "license": "MIT",
            "license_file": "licenses/VoltAgent-awesome-design-md-MIT.txt",
            "design_md_count": design_count,
        }
        write_json(meta_path, stable_metadata(meta_path, metadata, ("commit", "design_md_count", "repository", "source_path")))
        write_json(
            legacy_meta_path,
            stable_metadata(
                legacy_meta_path,
                {
                    "commit": latest,
                    "design_md_count": design_count,
                    "ref": "HEAD",
                    "repository": AWESOME_REPO,
                },
                ("commit", "design_md_count", "repository"),
            ),
        )
        print(f"updated awesome-design-md: {latest} ({design_count} styles)")


def sync_hermes_agent(allow_large_count_change: bool) -> None:
    meta_path = UPSTREAMS / "hermes-agent.json"
    latest = ls_remote_head(HERMES_REPO)
    current = read_json(meta_path).get("commit")
    target_claude_dir = REFERENCES / "claude-design"
    target_popular_dir = REFERENCES / "popular-web-designs"
    if (
        current == latest
        and (target_claude_dir / "SKILL.md").exists()
        and (target_popular_dir / "SKILL.md").exists()
        and (target_popular_dir / "templates").exists()
        and (LICENSES / "NousResearch-hermes-agent-MIT.txt").exists()
    ):
        print(f"hermes-agent already up to date: {latest}")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = Path(temp_dir) / "hermes-agent"
        clone(HERMES_REPO, repo_dir)
        latest = run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
        claude_skill = repo_dir / "skills" / "creative" / "claude-design" / "SKILL.md"
        popular_skill = repo_dir / "skills" / "creative" / "popular-web-designs" / "SKILL.md"
        templates = repo_dir / "skills" / "creative" / "popular-web-designs" / "templates"
        source_license = repo_dir / "LICENSE"
        for required in (claude_skill, popular_skill, source_license):
            if not required.is_file():
                raise SystemExit(f"hermes-agent missing required file: {required.relative_to(repo_dir)}")
        if not templates.is_dir():
            raise SystemExit("hermes-agent missing popular-web-designs templates/")

        previous_count = read_json(meta_path).get("popular_template_count")
        target_claude_dir.mkdir(parents=True, exist_ok=True)
        target_popular_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(claude_skill, target_claude_dir / "SKILL.md")
        shutil.copy2(popular_skill, target_popular_dir / "SKILL.md")
        copytree_replace(templates, target_popular_dir / "templates")
        LICENSES.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_license, LICENSES / "NousResearch-hermes-agent-MIT.txt")

        template_count = len(list((target_popular_dir / "templates").glob("*.md")))
        guard_count_change("popular-web-designs template", previous_count, template_count, allow_large_count_change)
        metadata = {
            "name": "hermes-agent",
            "repository": HERMES_REPO,
            "ref": "HEAD",
            "commit": latest,
            "claude_design_path": "skills/creative/claude-design/SKILL.md",
            "claude_design_blob": run(["git", "rev-parse", "HEAD:skills/creative/claude-design/SKILL.md"], cwd=repo_dir),
            "popular_web_designs_path": "skills/creative/popular-web-designs/SKILL.md",
            "popular_web_designs_blob": run(["git", "rev-parse", "HEAD:skills/creative/popular-web-designs/SKILL.md"], cwd=repo_dir),
            "popular_templates_path": "skills/creative/popular-web-designs/templates",
            "popular_templates_blob": run(["git", "rev-parse", "HEAD:skills/creative/popular-web-designs/templates"], cwd=repo_dir),
            "popular_template_count": template_count,
            "license": "MIT",
            "license_file": "licenses/NousResearch-hermes-agent-MIT.txt",
        }
        write_json(
            meta_path,
            stable_metadata(
                meta_path,
                metadata,
                (
                    "commit",
                    "claude_design_blob",
                    "popular_web_designs_blob",
                    "popular_templates_blob",
                    "popular_template_count",
                    "repository",
                ),
            ),
        )
        print(f"updated hermes-agent: {latest} ({template_count} templates)")


def github_json(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "design-director-sync",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    last_error = ""
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            last_error = str(exc)
            if attempt < 3:
                time.sleep(attempt)
    raise SystemExit(f"GitHub API request failed after 3 attempts: {url}\n{last_error}")


def sync_frontend_design() -> None:
    meta_path = UPSTREAMS / "frontend-design.json"
    legacy_meta_path = REFERENCES / "frontend-design" / "upstream-version.json"
    api_url = f"https://api.github.com/repos/{FRONTEND_REPO}/contents/{FRONTEND_SOURCE_PATH}?ref=main"
    data = github_json(api_url)
    latest = data.get("sha")
    if not latest:
        raise SystemExit("frontend-design API response did not include sha")
    current = read_json(meta_path).get("blob_sha") or read_json(legacy_meta_path).get("blob_sha")
    target = REFERENCES / "frontend-design" / "SKILL.md"
    if current == latest and target.exists():
        print(f"frontend-design already up to date: {latest}")
        return

    content = data.get("content")
    if not content:
        raise SystemExit("frontend-design API response did not include content")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(base64.b64decode(content))
    metadata = {
        "name": "frontend-design",
        "repository": f"https://github.com/{FRONTEND_REPO}.git",
        "ref": "main",
        "source_path": FRONTEND_SOURCE_PATH,
        "source_url": data.get("html_url"),
        "blob_sha": latest,
    }
    write_json(meta_path, stable_metadata(meta_path, metadata, ("blob_sha", "repository", "source_path", "source_url")))
    write_json(
        legacy_meta_path,
        stable_metadata(
            legacy_meta_path,
            {
                "blob_sha": latest,
                "ref": "main",
                "repository": metadata["repository"],
                "source_path": FRONTEND_SOURCE_PATH,
                "source_url": data.get("html_url"),
            },
            ("blob_sha", "repository", "source_path", "source_url"),
        ),
    )
    print(f"updated frontend-design: {latest}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-large-count-change",
        action="store_true",
        help="allow large upstream count changes after manual inspection",
    )
    args = parser.parse_args()

    UPSTREAMS.mkdir(parents=True, exist_ok=True)
    LICENSES.mkdir(parents=True, exist_ok=True)
    sync_awesome_design_md(args.allow_large_count_change)
    sync_hermes_agent(args.allow_large_count_change)
    sync_frontend_design()
    print("upstream sync complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
