#!/usr/bin/env python3
"""Pick one deterministic design direction for Design Director."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = PLUGIN_ROOT / "references"

ALIASES = {
    "linear": "linear.app",
    "linear.app": "linear.app",
    "vercel": "vercel",
    "stripe": "stripe",
    "supabase": "supabase",
    "raycast": "raycast",
    "sentry": "sentry",
    "claude": "claude",
    "notion": "notion",
    "apple": "apple",
    "airbnb": "airbnb",
    "framer": "framer",
    "shopify": "shopify",
    "spotify": "spotify",
    "the verge": "theverge",
    "theverge": "theverge",
    "wired": "wired",
    "hashicorp": "hashicorp",
    "mintlify": "mintlify",
    "resend": "resend",
    "clickhouse": "clickhouse",
    "revolut": "revolut",
    "wise": "wise",
    "coinbase": "coinbase",
    "kraken": "kraken",
    "cohere": "cohere",
    "mistral": "mistral.ai",
    "mistral.ai": "mistral.ai",
    "replicate": "replicate",
    "runway": "runwayml",
    "runwayml": "runwayml",
}

CATEGORY_RULES = [
    (
        "internal SaaS dashboard or operations UI",
        re.compile(r"\b(admin|dashboard|ops|operation|monitor|analytics|saas|crm|b2b|backoffice|data|后台|运维|数据密集)\b", re.I),
        ["linear.app", "supabase", "sentry", "clickhouse", "raycast", "resend"],
    ),
    (
        "developer documentation or infrastructure product",
        re.compile(r"\b(api|docs?|developer|sdk|cli|infra|cloud|database|devtool|开发者|文档)\b", re.I),
        ["mintlify", "hashicorp", "vercel", "supabase", "mongodb"],
    ),
    (
        "fintech or crypto product",
        re.compile(r"\b(payment|pay|billing|bank|finance|fintech|crypto|wallet|trading|交易|支付|金融)\b", re.I),
        ["stripe", "revolut", "wise", "coinbase", "kraken"],
    ),
    (
        "AI or model product",
        re.compile(r"\b(ai|llm|agent|model|inference|prompt|copilot|assistant|智能|模型)\b", re.I),
        ["claude", "cohere", "mistral.ai", "replicate", "together.ai"],
    ),
    (
        "marketing or startup landing page",
        re.compile(r"\b(landing|marketing|homepage|launch|startup|waitlist|hero|官网|落地页)\b", re.I),
        ["stripe", "framer", "vercel", "notion", "apple"],
    ),
    (
        "commerce or marketplace",
        re.compile(r"\b(shop|store|commerce|marketplace|checkout|retail|电商|商城)\b", re.I),
        ["shopify", "airbnb", "stripe"],
    ),
    (
        "editorial or content experience",
        re.compile(r"\b(editorial|news|magazine|blog|publishing|media|内容|博客)\b", re.I),
        ["theverge", "wired", "notion"],
    ),
    (
        "premium consumer or hardware brand",
        re.compile(r"\b(luxury|automotive|car|hardware|device|premium|portfolio|奢侈|汽车)\b", re.I),
        ["apple", "bmw", "ferrari", "nike"],
    ),
]


def available_design_slugs() -> set[str]:
    root = REFERENCES / "design-md"
    if not root.exists():
        return set()
    return {p.name for p in root.iterdir() if (p / "DESIGN.md").exists()}


def available_template_slugs() -> set[str]:
    root = REFERENCES / "popular-web-designs" / "templates"
    if not root.exists():
        return set()
    return {p.stem for p in root.glob("*.md")}


def first_available(candidates: list[str], available: set[str], fallback: str) -> str:
    for candidate in candidates:
        if candidate in available:
            return candidate
    return fallback if fallback in available else sorted(available)[0]


def explicit_style(text: str, available: set[str]) -> str | None:
    lowered = text.lower()
    for alias, slug in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in lowered and slug in available:
            return slug
    for slug in sorted(available, key=len, reverse=True):
        if slug.lower() in lowered:
            return slug
    return None


def choose_skill(deliverable: str, explicit: bool, template_exists: bool) -> str:
    deliverable_l = deliverable.lower()
    if "design.md" in deliverable_l or "spec" in deliverable_l or "tokens" in deliverable_l:
        return "design-md"
    if explicit and template_exists:
        return "popular-web-designs"
    if any(term in deliverable_l for term in ["html", "landing", "prototype", "artifact"]):
        return "claude-design"
    return "design-md"


def build_references(slug: str, primary_skill: str, templates: set[str], design_slugs: set[str]) -> list[str]:
    refs: list[str] = []
    if primary_skill == "popular-web-designs" and slug in templates:
        refs.append(f"references/popular-web-designs/templates/{slug}.md")
    if slug in design_slugs:
        refs.append(f"references/design-md/{slug}/DESIGN.md")
    refs.append("references/frontend-design/SKILL.md")
    return refs


def pick(brief: str, deliverable: str) -> dict:
    design_slugs = available_design_slugs()
    template_slugs = available_template_slugs()
    if not design_slugs:
        raise SystemExit("No DESIGN.md references found.")

    all_available = design_slugs | template_slugs
    named_direction = explicit_style(brief, all_available)
    reason = "explicit named visual direction"
    if named_direction is None:
        reason = "general product UI fallback"
        named_direction = first_available(["linear.app", "vercel", "stripe"], design_slugs, sorted(design_slugs)[0])
        for label, pattern, candidates in CATEGORY_RULES:
            if pattern.search(brief):
                named_direction = first_available(candidates, design_slugs, named_direction)
                reason = label
                break

    primary_skill = choose_skill(
        deliverable,
        reason == "explicit named visual direction",
        named_direction in template_slugs,
    )
    return {
        "primary_skill": primary_skill,
        "primary_direction": named_direction,
        "secondary_direction": None,
        "reason": reason,
        "references": build_references(named_direction, primary_skill, template_slugs, design_slugs),
        "risk_notes": [
            "Use the reference as visual direction only.",
            "Do not copy logos, screenshots, proprietary copy, or paid fonts.",
            "Keep one primary direction unless the user explicitly asks otherwise.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", nargs="*", help="product or UI description")
    parser.add_argument("--deliverable", default="app", help="app, design.md, html, landing, prototype, etc.")
    args = parser.parse_args()
    brief = " ".join(args.brief).strip()
    if not brief:
        raise SystemExit("Provide a product or UI description.")
    print(json.dumps(pick(brief, args.deliverable), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
