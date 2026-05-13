#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_REPO = "https://github.com/VoltAgent/awesome-design-md.git"
ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"
DESIGN_DIR = REFERENCES / "design-md"
VERSION_FILE = REFERENCES / "upstream-version.json"
LICENSE_FILE = REFERENCES / "upstream-license.txt"
README_FILE = REFERENCES / "upstream-readme.md"


def run(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(f"Command failed: {' '.join(cmd)}\n{detail}")
    return result.stdout.strip()


def read_version() -> dict:
    if not VERSION_FILE.exists():
        return {}
    return json.loads(VERSION_FILE.read_text(encoding="utf-8"))


def remote_commit(repo: str, ref: str) -> str:
    output = run(["git", "ls-remote", repo, ref])
    if not output:
        raise SystemExit(f"No remote ref found: {repo} {ref}")
    return output.split()[0]


def write_version(repo: str, ref: str, commit: str, count: int) -> None:
    data = {
        "repository": repo,
        "ref": ref,
        "commit": commit,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "design_md_count": count,
    }
    VERSION_FILE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def replace_tree(source: Path, target: Path) -> None:
    backup = None
    if target.exists():
        backup = target.with_name(f".{target.name}.backup")
        if backup.exists():
            shutil.rmtree(backup)
        target.rename(backup)
    try:
        shutil.copytree(source, target)
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup and backup.exists():
            backup.rename(target)
        raise
    if backup and backup.exists():
        shutil.rmtree(backup)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update bundled DESIGN.md files from awesome-design-md.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"upstream repository, default: {DEFAULT_REPO}")
    parser.add_argument("--ref", default="HEAD", help="remote ref to track, default: HEAD")
    parser.add_argument("--check", action="store_true", help="only report whether an update is available")
    parser.add_argument("--force", action="store_true", help="refresh even when the commit is unchanged")
    args = parser.parse_args()

    current = read_version()
    current_commit = current.get("commit")
    latest_commit = remote_commit(args.repo, args.ref)

    if args.check:
        status = "up-to-date" if current_commit == latest_commit else "update-available"
        print(json.dumps({
            "status": status,
            "current_commit": current_commit,
            "latest_commit": latest_commit,
            "repository": args.repo,
            "ref": args.ref,
        }, indent=2, sort_keys=True))
        return 0 if status == "up-to-date" else 2

    if current_commit == latest_commit and not args.force:
        print(f"Already up to date at {latest_commit}")
        return 0

    with tempfile.TemporaryDirectory(prefix="design-md-upstream-") as temp:
        checkout = Path(temp) / "repo"
        run(["git", "clone", "--depth=1", args.repo, str(checkout)])
        if args.ref != "HEAD":
            run(["git", "checkout", args.ref], cwd=checkout)
        commit = run(["git", "rev-parse", "HEAD"], cwd=checkout)

        source_design = checkout / "design-md"
        if not source_design.exists():
            raise SystemExit(f"Upstream checkout has no design-md directory: {source_design}")

        replace_tree(source_design, DESIGN_DIR)
        if (checkout / "LICENSE").exists():
            shutil.copyfile(checkout / "LICENSE", LICENSE_FILE)
        if (checkout / "README.md").exists():
            shutil.copyfile(checkout / "README.md", README_FILE)

        count = len(list(DESIGN_DIR.glob("*/DESIGN.md")))
        write_version(args.repo, args.ref, commit, count)
        print(f"Updated DESIGN.md references to {commit} ({count} styles)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
