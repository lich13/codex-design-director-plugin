#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_VERSION_FILE = ROOT / "references" / "upstream-version.json"
FRONTEND_VERSION_FILE = ROOT / "references" / "frontend-design" / "upstream-version.json"


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result


def validate() -> None:
    skill = ROOT / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise SystemExit("SKILL.md frontmatter is not closed")
    frontmatter = text[4:end]
    keys = {
        line.split(":", 1)[0].strip()
        for line in frontmatter.splitlines()
        if line.strip() and ":" in line
    }
    if keys != {"name", "description"}:
        raise SystemExit(f"SKILL.md frontmatter must contain only name and description, got: {sorted(keys)}")
    if "name: design-md" not in frontmatter:
        raise SystemExit("SKILL.md name must be design-md")
    if not (ROOT / "agents" / "openai.yaml").exists():
        raise SystemExit("Missing agents/openai.yaml")

    design_files = list((ROOT / "references" / "design-md").glob("*/DESIGN.md"))
    if not design_files:
        raise SystemExit("No bundled DESIGN.md files found")

    version = json.loads(DESIGN_VERSION_FILE.read_text(encoding="utf-8"))
    if version.get("design_md_count") != len(design_files):
        raise SystemExit(
            f"upstream-version.json count mismatch: {version.get('design_md_count')} != {len(design_files)}"
        )

    frontend_skill = ROOT / "references" / "frontend-design" / "SKILL.md"
    frontend_version = json.loads(FRONTEND_VERSION_FILE.read_text(encoding="utf-8"))
    frontend_text = frontend_skill.read_text(encoding="utf-8")
    if "name: frontend-design" not in frontend_text:
        raise SystemExit("frontend-design reference must contain name: frontend-design")
    if frontend_version.get("source_path") != "plugins/frontend-design/skills/frontend-design/SKILL.md":
        raise SystemExit("frontend-design upstream-version.json has the wrong source_path")

    run([sys.executable, "-m", "py_compile", *[str(path) for path in sorted((ROOT / "scripts").glob("*.py"))]])


def git_has_changes() -> bool:
    result = run(["git", "status", "--porcelain"], check=False)
    return bool(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Check upstream, update bundled DESIGN.md references, validate, and optionally commit/push.")
    parser.add_argument("--commit", action="store_true", help="commit changes when upstream updates")
    parser.add_argument("--push", action="store_true", help="push committed changes")
    parser.add_argument("--message", default="Update bundled design references", help="commit message")
    args = parser.parse_args()

    updates = []
    for label, script in (
        ("DESIGN.md references", "update_upstream.py"),
        ("frontend-design reference", "update_frontend_design.py"),
    ):
        check = run([sys.executable, str(ROOT / "scripts" / script), "--check"], check=False)
        if check.returncode == 0:
            print(f"{label}: already up to date.")
            continue
        if check.returncode != 2:
            sys.stderr.write(check.stdout)
            sys.stderr.write(check.stderr)
            return check.returncode
        run([sys.executable, str(ROOT / "scripts" / script)])
        updates.append(label)

    validate()

    if updates:
        print("Updated upstream references: " + ", ".join(updates))
    else:
        print("No upstream update available; validation passed.")

    if args.commit and git_has_changes():
        run([
            "git",
            "add",
            "references/design-md",
            "references/upstream-license.txt",
            "references/upstream-readme.md",
            "references/upstream-version.json",
            "references/frontend-design",
        ])
        run(["git", "commit", "-m", args.message])
    elif args.commit:
        print("No git changes to commit.")

    if args.push:
        branch = run(["git", "branch", "--show-current"]).stdout.strip()
        if not branch:
            raise SystemExit("Cannot push: no current git branch")
        run(["git", "push", "-u", "origin", branch])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
