---
name: popular-web-designs
description: Use real website-inspired HTML/CSS design templates such as Stripe, Linear, Vercel, Claude, Notion, Apple, Supabase, Raycast, and Sentry. Use when the user asks for a known visual style or wants Codex to borrow a professional product/marketing design language.
---

# Popular Web Designs

Use this skill when the user asks for a page, component, dashboard, or artifact styled after a known website or product.

This is the Codex-adapted wrapper. The upstream Hermes source is bundled at `../../references/popular-web-designs/SKILL.md`; the active templates are in `../../references/popular-web-designs/templates/*.md`.

## Core Rules

- Use templates as visual vocabulary, not brand ownership.
- Do not copy logos, screenshots, proprietary copy, or paid fonts.
- Pick one template as the primary direction.
- Use a second template only for a narrow reason, such as table density or typography contrast.
- Prefer the existing repo's implementation primitives over pasting standalone CSS when working in a real project.
- For standalone HTML artifacts, use the template's colors, typography substitutions, component rules, spacing, and shadows directly.

## Workflow

1. Choose the template.
   - If the user names a style, load the matching `../../references/popular-web-designs/templates/<slug>.md`.
   - If the user describes a product category, select from the catalog below.

2. Load only the chosen template.
   - Do not load every template.
   - Extract practical tokens: colors, fonts, type scale, spacing, radius, shadows, component styles, responsive behavior.

3. Apply to the requested deliverable.
   - Existing repo: map tokens into the local theme/components.
   - Standalone HTML: build self-contained CSS and HTML.
   - Project `DESIGN.md`: use `../design-md/SKILL.md` instead of this skill.

4. Verify visually.
   - Check desktop and mobile.
   - Fix text overflow, contrast, layout overlap, and responsive clipping.

## Catalog Guide

- Developer tools and dashboards: `linear.app`, `vercel`, `supabase`, `sentry`, `raycast`, `cursor`, `warp`.
- AI and model products: `claude`, `cohere`, `elevenlabs`, `mistral.ai`, `replicate`, `runwayml`, `together.ai`.
- Marketing and landing pages: `stripe`, `apple`, `framer`, `airbnb`, `notion`, `webflow`, `spotify`.
- Documentation and content: `mintlify`, `notion`, `sanity`, `mongodb`, `vercel`.
- Data-dense surfaces: `sentry`, `kraken`, `cohere`, `clickhouse`, `linear.app`.
- Fintech and trust-heavy pages: `stripe`, `coinbase`, `wise`, `revolut`, `kraken`.
- Terminal or agent aesthetics: `ollama`, `opencode.ai`, `voltagent`, `warp`, `x.ai`.

## Template Files

Templates live at `../../references/popular-web-designs/templates/<slug>.md`. Examples:

- `../../references/popular-web-designs/templates/stripe.md`
- `../../references/popular-web-designs/templates/linear.app.md`
- `../../references/popular-web-designs/templates/vercel.md`
- `../../references/popular-web-designs/templates/claude.md`
- `../../references/popular-web-designs/templates/notion.md`
- `../../references/popular-web-designs/templates/supabase.md`
- `../../references/popular-web-designs/templates/raycast.md`
- `../../references/popular-web-designs/templates/sentry.md`

## Bundled Upstream

- `../../references/popular-web-designs/SKILL.md`: original Hermes Agent `popular-web-designs` skill.
- `../../references/upstreams/hermes-agent.json`: source commit, template count, and update metadata.
