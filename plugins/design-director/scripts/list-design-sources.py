#!/usr/bin/env python3
"""List bundled design references for the Design Director plugin."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = PLUGIN_ROOT / "references"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def design_md_sources() -> list[dict]:
    root = REFERENCES / "design-md"
    if not root.exists():
        return []
    sources: list[dict] = []
    for item in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        design_file = item / "DESIGN.md"
        if item.is_dir() and design_file.exists():
            sources.append(
                {
                    "slug": item.name,
                    "design_md": str(design_file.relative_to(PLUGIN_ROOT)),
                    "readme": str((item / "README.md").relative_to(PLUGIN_ROOT))
                    if (item / "README.md").exists()
                    else None,
                }
            )
    return sources


def popular_templates() -> list[dict]:
    root = REFERENCES / "popular-web-designs" / "templates"
    if not root.exists():
        return []
    return [
        {
            "slug": path.stem,
            "template": str(path.relative_to(PLUGIN_ROOT)),
        }
        for path in sorted(root.glob("*.md"), key=lambda p: p.name.lower())
    ]


def upstreams() -> dict:
    root = REFERENCES / "upstreams"
    if not root.exists():
        return {}
    return {
        path.stem: read_json(path)
        for path in sorted(root.glob("*.json"), key=lambda p: p.name)
    }


def build_catalog() -> dict:
    design_md = design_md_sources()
    templates = popular_templates()
    return {
        "plugin": "design-director",
        "design_md_count": len(design_md),
        "popular_template_count": len(templates),
        "design_md": design_md,
        "popular_web_designs": templates,
        "upstreams": upstreams(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    catalog = build_catalog()
    if args.json:
        print(json.dumps(catalog, indent=2, sort_keys=True))
        return 0

    print("Design Director sources")
    print(f"- DESIGN.md styles: {catalog['design_md_count']}")
    print(f"- Popular templates: {catalog['popular_template_count']}")
    print()
    print("DESIGN.md slugs:")
    for source in catalog["design_md"]:
        print(f"- {source['slug']}")
    if catalog["popular_web_designs"]:
        print()
        print("Popular template slugs:")
        for source in catalog["popular_web_designs"]:
            print(f"- {source['slug']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
