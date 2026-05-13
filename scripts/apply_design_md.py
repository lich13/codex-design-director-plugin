#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = ROOT / "references" / "design-md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy a bundled DESIGN.md into a project root.")
    parser.add_argument("slug", help="style slug, for example vercel, linear.app, stripe")
    parser.add_argument("project_root", help="target project root")
    parser.add_argument("--force", action="store_true", help="replace an existing DESIGN.md")
    args = parser.parse_args()

    source = DESIGN_DIR / args.slug / "DESIGN.md"
    if not source.exists():
        available = ", ".join(path.parent.name for path in sorted(DESIGN_DIR.glob("*/DESIGN.md")))
        raise SystemExit(f"Unknown style '{args.slug}'. Available styles: {available}")

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        raise SystemExit(f"Project root is not a directory: {project_root}")

    target = project_root / "DESIGN.md"
    if target.exists() and not args.force:
        raise SystemExit(f"{target} already exists. Re-run with --force to replace it.")

    shutil.copyfile(source, target)
    print(f"Installed {args.slug} DESIGN.md -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
