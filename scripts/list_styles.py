#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = ROOT / "references" / "design-md"


def load_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^description:\s*(.*)$", text, re.MULTILINE)
    if not match:
        return ""

    description = match.group(1).strip()
    if description in {"|", ">"}:
        lines = []
        capture = False
        for line in text.splitlines():
            if capture:
                if line and not line.startswith((" ", "\t")):
                    break
                lines.append(line.strip())
            elif line.startswith("description:"):
                capture = True
        description = " ".join(part for part in lines if part)

    return description.strip().strip('"').strip("'")


def main() -> int:
    parser = argparse.ArgumentParser(description="List bundled DESIGN.md styles.")
    parser.add_argument("--search", help="case-insensitive search over slug and description")
    args = parser.parse_args()

    if not DESIGN_DIR.exists():
        raise SystemExit(f"Missing design directory: {DESIGN_DIR}")

    query = args.search.lower() if args.search else None
    rows = []
    for design_file in sorted(DESIGN_DIR.glob("*/DESIGN.md")):
        slug = design_file.parent.name
        description = load_description(design_file)
        haystack = f"{slug} {description}".lower()
        if query and query not in haystack:
            continue
        rows.append((slug, description))

    if not rows:
        return 1

    width = max(len(slug) for slug, _ in rows)
    for slug, description in rows:
        if len(description) > 180:
            description = description[:177].rstrip() + "..."
        print(f"{slug.ljust(width)}  {description}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
