#!/usr/bin/env python3
"""Validate Design Director plugin manifests, skills, scripts, and references."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
REFERENCES = PLUGIN_ROOT / "references"
MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path} is not valid JSON: {exc}")


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"missing file: {display(path)}")


def require_dir(path: Path) -> None:
    if not path.is_dir():
        fail(f"missing directory: {display(path)}")


def display(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def frontmatter_name(path: Path) -> str:
    require_file(path)
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail(f"missing YAML frontmatter: {display(path)}")
    name_match = re.search(r"^name:\s*([A-Za-z0-9_.-]+)\s*$", match.group(1), re.M)
    if not name_match:
        fail(f"missing frontmatter name: {display(path)}")
    if not re.search(r"^description:\s*.+$", match.group(1), re.M):
        fail(f"missing frontmatter description: {display(path)}")
    return name_match.group(1)


def validate_plugin_manifest() -> None:
    manifest = read_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
    if manifest.get("name") != "design-director":
        fail("plugin.json name must be design-director")
    if not re.match(r"^\d+\.\d+\.\d+$", str(manifest.get("version", ""))):
        fail("plugin.json version must be semver")
    if manifest.get("skills") != "./skills/":
        fail("plugin.json skills must be ./skills/")
    if "mcpServers" in manifest:
        fail("mcpServers should be omitted until this plugin actually ships an MCP server")
    interface = manifest.get("interface") or {}
    prompts = interface.get("defaultPrompt") or []
    if len(prompts) > 3:
        fail("interface.defaultPrompt must have at most 3 entries")
    for prompt in prompts:
        if len(prompt) > 128:
            fail(f"defaultPrompt entry exceeds 128 characters: {prompt}")


def validate_marketplace() -> None:
    if not MARKETPLACE.exists():
        print("Skipping marketplace validation; running from plugin cache without repository root.")
        return
    marketplace = read_json(MARKETPLACE)
    if marketplace.get("name") != "lich13-design":
        fail("marketplace name must be lich13-design")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        fail("marketplace plugins must be a list")
    entries = [entry for entry in plugins if entry.get("name") == "design-director"]
    if len(entries) != 1:
        fail("marketplace must contain exactly one design-director entry")
    entry = entries[0]
    if entry.get("source") != {"source": "local", "path": "./plugins/design-director"}:
        fail("marketplace source must point to ./plugins/design-director")
    policy = entry.get("policy") or {}
    if policy.get("installation") not in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}:
        fail("marketplace policy.installation is invalid")
    if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
        fail("marketplace policy.authentication is invalid")
    if not entry.get("category"):
        fail("marketplace entry category is required")


def validate_skills() -> None:
    expected = {
        "design-director": PLUGIN_ROOT / "skills" / "design-director" / "SKILL.md",
        "design-md": PLUGIN_ROOT / "skills" / "design-md" / "SKILL.md",
        "claude-design": PLUGIN_ROOT / "skills" / "claude-design" / "SKILL.md",
        "popular-web-designs": PLUGIN_ROOT / "skills" / "popular-web-designs" / "SKILL.md",
    }
    for expected_name, path in expected.items():
        actual = frontmatter_name(path)
        if actual != expected_name:
            fail(f"{display(path)} frontmatter name is {actual}, expected {expected_name}")

    stale_reference_patterns = [
        "../design-md/references/",
        "../popular-web-designs/templates/",
        "../claude-design/references/",
        "../popular-web-designs/references/",
        "../frontend-design/SKILL.md",
        "references/hermes/",
        "`templates/",
    ]
    for path in expected.values():
        text = path.read_text(encoding="utf-8")
        for pattern in stale_reference_patterns:
            if pattern in text:
                fail(f"{display(path)} contains stale reference path: {pattern}")


def validate_references() -> None:
    require_dir(REFERENCES / "design-md")
    require_file(REFERENCES / "frontend-design" / "SKILL.md")
    require_file(REFERENCES / "claude-design" / "SKILL.md")
    require_file(REFERENCES / "popular-web-designs" / "SKILL.md")
    require_dir(REFERENCES / "popular-web-designs" / "templates")
    require_file(PLUGIN_ROOT / "licenses" / "VoltAgent-awesome-design-md-MIT.txt")
    require_file(PLUGIN_ROOT / "licenses" / "NousResearch-hermes-agent-MIT.txt")

    if frontmatter_name(REFERENCES / "frontend-design" / "SKILL.md") != "frontend-design":
        fail("frontend-design reference has unexpected name")
    frontmatter_name(REFERENCES / "claude-design" / "SKILL.md")
    frontmatter_name(REFERENCES / "popular-web-designs" / "SKILL.md")

    design_count = len(list((REFERENCES / "design-md").glob("*/DESIGN.md")))
    if design_count < 20:
        fail(f"too few DESIGN.md references: {design_count}")
    design_meta = read_json(REFERENCES / "upstreams" / "awesome-design-md.json")
    if design_meta.get("design_md_count") != design_count:
        fail(f"awesome-design-md count mismatch: metadata={design_meta.get('design_md_count')} actual={design_count}")

    template_count = len(list((REFERENCES / "popular-web-designs" / "templates").glob("*.md")))
    if template_count < 20:
        fail(f"too few popular web design templates: {template_count}")
    hermes_meta = read_json(REFERENCES / "upstreams" / "hermes-agent.json")
    if hermes_meta.get("popular_template_count") != template_count:
        fail(f"popular template count mismatch: metadata={hermes_meta.get('popular_template_count')} actual={template_count}")

    frontend_meta = read_json(REFERENCES / "upstreams" / "frontend-design.json")
    if frontend_meta.get("source_path") != "plugins/frontend-design/skills/frontend-design/SKILL.md":
        fail("frontend-design metadata source_path mismatch")

    empty_dirs = [path for path in REFERENCES.rglob("*") if path.is_dir() and not any(path.iterdir())]
    if empty_dirs:
        fail("empty reference directories: " + ", ".join(display(path) for path in empty_dirs))


def validate_scripts() -> None:
    scripts = sorted((PLUGIN_ROOT / "scripts").glob("*.py"))
    if not scripts:
        fail("no Python scripts found")
    cmd = [sys.executable, "-m", "py_compile", *[str(path) for path in scripts]]
    subprocess.run(cmd, check=True)
    picker = PLUGIN_ROOT / "scripts" / "pick-design-direction.py"
    output = subprocess.check_output(
        [sys.executable, str(picker), "--deliverable", "app", "data dense SaaS operations dashboard"],
        text=True,
    )
    picked = json.loads(output)
    if not picked.get("primary_direction"):
        fail("pick-design-direction.py did not return a primary_direction")


def main() -> int:
    validate_plugin_manifest()
    validate_marketplace()
    validate_skills()
    validate_references()
    validate_scripts()
    print("Design Director plugin validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
