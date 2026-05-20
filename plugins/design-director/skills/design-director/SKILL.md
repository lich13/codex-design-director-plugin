---
name: design-director
description: Automatically choose the right frontend design workflow and reference set for Codex. Use when the user asks to build, redesign, modernize, polish, prototype, create a landing page, create a DESIGN.md, use Claude/Stripe/Linear/Vercel style, or otherwise wants Codex to decide an appropriate UI direction.
---

# Design Director

Use this skill as the routing layer for frontend visual work. It combines:

- `design-md`: persistent project-level `DESIGN.md` visual systems.
- `claude-design`: one-off HTML artifacts, prototypes, decks, and high-taste design workflow.
- `popular-web-designs`: ready-to-apply HTML/CSS design templates inspired by real websites.
- `frontend-design`: distinctive, production-grade frontend execution guidance.

## Core Rules

- Treat bundled references as visual direction, not brand ownership.
- Do not copy logos, trademarked marks, screenshots, proprietary copy, paid fonts, or private assets unless the user explicitly supplies rights.
- Pick one primary direction. Borrow a secondary direction only for a narrow reason, such as typography or density, and state that reason.
- Inspect the actual project before choosing when a repo is available: `AGENTS.md`, `DESIGN.md`, package files, theme files, CSS/Tailwind config, and representative pages/components.
- If a project already has `DESIGN.md`, treat it as authoritative unless the user explicitly asks to replace it.
- Prefer existing project components, tokens, routing, state, and data flow. Apply visual changes through the local design system first.
- Verify rendered frontend work with the normal dev server and browser checks when implementation changes are made.

## Routing

First classify the requested deliverable:

| User wants | Primary workflow | References to load |
|---|---|---|
| A persistent project design system or `DESIGN.md` | `design-md` | `../design-md/SKILL.md`, then one `../../references/design-md/<slug>/DESIGN.md` |
| A one-off HTML artifact, prototype, deck, option board, or motion study | `claude-design` | `../claude-design/SKILL.md`; optionally one `../../references/popular-web-designs/templates/<slug>.md` |
| A page that looks like Stripe, Linear, Vercel, Claude, Apple, Notion, etc. | `popular-web-designs` | `../popular-web-designs/SKILL.md`, then `../../references/popular-web-designs/templates/<slug>.md` |
| A real repo redesign, modernization, or polish pass | `design-md` plus `frontend-design` | Existing repo files, one DESIGN.md direction, `../../references/frontend-design/SKILL.md` |
| A new frontend app/dashboard/tool with no named style | Choose by product type | Use the matrix below |

## Direction Matrix

- SaaS dashboards and internal tools: prefer `linear.app`, `vercel`, `supabase`, `sentry`, `raycast`, `resend`, `clickhouse`, or `hashicorp`.
- Developer tools and docs: prefer `vercel`, `mintlify`, `supabase`, `mongodb`, `cursor`, `warp`, or `opencode.ai`.
- AI products: prefer `claude`, `cohere`, `elevenlabs`, `mistral.ai`, `replicate`, `runwayml`, or `together.ai`.
- Marketing and landing pages: prefer `stripe`, `apple`, `framer`, `airbnb`, `notion`, `webflow`, or `spotify`.
- Data-dense or operational surfaces: prefer `sentry`, `clickhouse`, `kraken`, `cohere`, or `linear.app`.
- Premium consumer or luxury pages: prefer `apple`, `bmw`, `spotify`, `airbnb`, or `superhuman`.
- Terminal, agent, or automation products: prefer `ollama`, `opencode.ai`, `voltagent`, `warp`, or `x.ai`.
- Claude-style requests: use `claude` from `design-md` or `popular-web-designs`, depending on whether the output is a spec or an HTML artifact.

If the user names a style slug, use that slug unless it clearly conflicts with the product or legal constraints.

## Workflow

1. Inspect the project or brief.
   - For repos, read the visual and framework files before selecting a direction.
   - For standalone artifacts, identify audience, output format, content, and fidelity.

2. Choose the smallest set of references.
   - Load this skill first.
   - Load one primary child skill.
   - Load only one style reference unless a secondary reference is necessary.

3. State the selected direction briefly when useful.
   - Include product-type fit and any tradeoff.
   - Avoid long design essays unless the user asked for one.

4. Apply through the correct workflow.
   - `DESIGN.md`: use `design-md`.
   - Standalone HTML or prototype: use `claude-design`.
   - Named brand-like style: use `popular-web-designs`.
   - Existing repo implementation: use existing stack plus `frontend-design`.

5. Verify.
   - Run lint/type/test/build commands when available.
   - Start the dev server for substantial frontend changes.
   - Inspect desktop and mobile renderings.
   - Fix overlap, clipping, unreadable contrast, broken responsive layout, and console errors.

## Helper Scripts

This plugin includes deterministic helper scripts:

- `../../scripts/list-design-sources.py`: list bundled DESIGN.md styles and popular templates.
- `../../scripts/pick-design-direction.py`: suggest a primary workflow and direction from a product description.
- `../../scripts/validate-references.py`: validate plugin manifests and bundled reference counts.

Scripts are helpers only. The final design decision must respect the user's brief and the actual repo.

## Bundled Sources

- `../../references/design-md/`: DESIGN.md files from `VoltAgent/awesome-design-md`.
- `../../references/popular-web-designs/templates/`: HTML/CSS-oriented templates from `NousResearch/hermes-agent`.
- `../../references/claude-design/SKILL.md`: upstream Hermes `claude-design` source.
- `../../references/popular-web-designs/SKILL.md`: upstream Hermes `popular-web-designs` source.
- `../../references/frontend-design/SKILL.md`: frontend execution guidance from Anthropic Claude Code.

## Stop Rules

Stop before editing if:

- A requested source has unclear licensing.
- The user asks to copy a protected logo, screenshot, paid font, or proprietary copy.
- The project has an existing `DESIGN.md` and the user did not ask to replace it.
- The requested style cannot be mapped to a bundled source and guessing would materially affect the outcome.
- The verification environment cannot run and visual correctness is central to the task.
