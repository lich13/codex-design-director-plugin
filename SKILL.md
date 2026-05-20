---
name: design-md
description: Apply curated DESIGN.md visual directions and frontend-design execution guidance to frontend projects. Use when the user asks to build, improve, restyle, redesign, modernize, polish, or choose a visual direction for a web/app frontend using DESIGN.md, awesome-design-md, Claude, Vercel, Linear, Stripe, Supabase, Raycast, or similar product-style references.
---

# Design MD

Use this skill to turn bundled `awesome-design-md` directions and the bundled `frontend-design` execution guide into practical frontend changes or a project-local `DESIGN.md`.

## Core Rules

- Treat bundled files as visual direction, not brand ownership. Do not copy logos, trademarked marks, product screenshots, or proprietary copy unless the user explicitly supplies assets and rights.
- Adapt the selected direction into the project's existing design system first: theme tokens, Tailwind config, CSS variables, component primitives, shadcn config, or local UI helpers.
- Prefer the project's existing components, routing, state, data fetching, and business logic. Make visual-layer changes unless the user asks for broader work.
- Do not combine many style files blindly. Pick one primary direction and optionally borrow a narrow secondary idea only when it clearly fits.
- Verify rendered UI after meaningful frontend changes. Use the app's normal dev server and browser checks for desktop and mobile.

## Workflow

1. Inspect the project shape.
   - Read `AGENTS.md`, existing `DESIGN.md`, package files, theme files, Tailwind/CSS config, and representative components/pages.
   - If an existing project `DESIGN.md` exists, treat it as authoritative unless the user asks to replace it.

2. Load execution guidance for frontend implementation.
   - For build, redesign, modernization, polish, or visually driven frontend work, read `references/frontend-design/SKILL.md`.
   - Use it as execution guidance for distinctive, production-grade frontend decisions; keep this skill's core rules and the project constraints as higher-priority boundaries.

3. Choose or confirm a design direction.
   - If the user names a style slug such as `vercel`, `linear.app`, `stripe`, `supabase`, or `raycast`, use that style.
   - If the user asks for Claude style, use the `claude` style.
   - If the user describes the product but does not choose a style, inspect the folders under `references/design-md/` and choose a fit based on product category and UI density.
   - For SaaS dashboards and internal tools, prefer restrained product systems such as `linear.app`, `vercel`, `supabase`, `stripe`, `raycast`, `resend`, `sentry`, `clickhouse`, or `hashicorp`.
   - For consumer, editorial, or branded marketing pages, consider `apple`, `airbnb`, `nike`, `notion`, `spotify`, `theverge`, or `wired`.

4. Load only the needed style reference.
   - Read `references/design-md/<slug>/DESIGN.md`.
   - Use the color, typography, spacing, component, layout, responsive, and do/don't sections as the design brief.
   - Do not load every bundled `DESIGN.md` into context.

5. Apply the direction.
   - Map colors to semantic tokens rather than scattering raw hex values through components.
   - Translate typography to available fonts or safe fallbacks; do not add paid/proprietary fonts unless the project already has them.
   - Keep component states complete: hover, focus, disabled, selected, loading, error, and responsive behavior where relevant.
   - Use real product/page content and existing data. Avoid generic marketing filler unless creating a placeholder prototype.

6. Optionally install a project-local `DESIGN.md`.
   - Copy `references/design-md/<slug>/DESIGN.md` into the project root as `DESIGN.md`.
   - If a project `DESIGN.md` already exists, back it up or require `--force` only when replacing is intended.
   - Add a short `AGENTS.md` note instructing future Codex runs to read `DESIGN.md` before frontend visual work when useful.

7. Verify.
   - Run available lint/type/test commands when the frontend stack supports them.
   - Start the dev server for substantial visual work.
   - Inspect desktop and mobile renderings; fix overlap, clipping, unreadable contrast, broken responsive layout, and console errors.

## Bundled Resources

- `references/design-md/`: Local copy of the upstream style folders. Each style has a `DESIGN.md`; some also include a README.
- `references/upstream-version.json`: Current upstream repository, ref, commit, update time, and bundled style count.
- `references/upstream-license.txt`: MIT license from the upstream collection.
- `references/frontend-design/SKILL.md`: Anthropic's `frontend-design` execution guidance.
- `references/frontend-design/upstream-version.json`: Current upstream path, ref, update time, and blob SHA for `frontend-design`.
- `plugins/design-director/`: Codex plugin form of this skill. It adds `design-director`, `claude-design`, `popular-web-designs`, and plugin-local references.
- `.agents/plugins/marketplace.json`: Codex marketplace entry for the `design-director` plugin.
- `.github/workflows/sync-upstreams.yml`: GitHub Actions workflow for `awesome-design-md`, `frontend-design`, and Hermes design skills.
- `.github/workflows/validate-plugin.yml`: GitHub Actions workflow for plugin and reference validation.
Upstream reference maintenance is handled by GitHub Actions and the plugin scripts under `plugins/design-director/scripts/`.
