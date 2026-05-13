---
name: design-md
description: Apply curated DESIGN.md visual design directions to frontend projects. Use when the user asks to improve, restyle, redesign, modernize, polish, or choose a visual direction for a web/app frontend using DESIGN.md, awesome-design-md, Vercel/Linear/Stripe/Supabase/Raycast/etc. inspired styling, or project-level UI design guidance for Codex.
---

# Design MD

Use this skill to turn the bundled `awesome-design-md` design directions into practical frontend changes or a project-local `DESIGN.md`.

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

2. Choose or confirm a design direction.
   - If the user names a style slug such as `vercel`, `linear.app`, `stripe`, `supabase`, or `raycast`, use that style.
   - If the user describes the product but does not choose a style, run `scripts/list_styles.py` and choose a fit based on product category and UI density.
   - For SaaS dashboards and internal tools, prefer restrained product systems such as `linear.app`, `vercel`, `supabase`, `stripe`, `raycast`, `resend`, `sentry`, `clickhouse`, or `hashicorp`.
   - For consumer, editorial, or branded marketing pages, consider `apple`, `airbnb`, `nike`, `notion`, `spotify`, `theverge`, or `wired`.

3. Load only the needed reference.
   - Read `references/design-md/<slug>/DESIGN.md`.
   - Use the color, typography, spacing, component, layout, responsive, and do/don't sections as the design brief.
   - Do not load every bundled `DESIGN.md` into context.

4. Apply the direction.
   - Map colors to semantic tokens rather than scattering raw hex values through components.
   - Translate typography to available fonts or safe fallbacks; do not add paid/proprietary fonts unless the project already has them.
   - Keep component states complete: hover, focus, disabled, selected, loading, error, and responsive behavior where relevant.
   - Use real product/page content and existing data. Avoid generic marketing filler unless creating a placeholder prototype.

5. Optionally install a project-local `DESIGN.md`.
   - Use `scripts/apply_design_md.py <slug> <project-root>` to copy a selected design into the project root.
   - If a project `DESIGN.md` already exists, back it up or require `--force` only when replacing is intended.
   - Add a short `AGENTS.md` note instructing future Codex runs to read `DESIGN.md` before frontend visual work when useful.

6. Verify.
   - Run available lint/type/test commands when the frontend stack supports them.
   - Start the dev server for substantial visual work.
   - Inspect desktop and mobile renderings; fix overlap, clipping, unreadable contrast, broken responsive layout, and console errors.

## Bundled Resources

- `references/design-md/`: Local copy of the upstream style folders. Each style has a `DESIGN.md`; some also include a README.
- `references/upstream-version.json`: Current upstream repository, ref, commit, update time, and bundled style count.
- `references/upstream-license.txt`: MIT license from the upstream collection.
- `scripts/list_styles.py`: Lists available style slugs and short descriptions.
- `scripts/apply_design_md.py`: Copies a selected bundled `DESIGN.md` into a project root.
- `scripts/update_upstream.py`: Checks or refreshes bundled references from the upstream repository.
- `scripts/auto_update.py`: Updates, validates, commits, and pushes upstream reference changes for repository automation.
- `.github/workflows/sync-upstream.yml`: GitHub Actions workflow that runs the upstream sync on a schedule and by manual dispatch.

## Useful Commands

List available styles:

```bash
python3 /Users/gosu/.codex/skills/design-md/scripts/list_styles.py
```

Search styles:

```bash
python3 /Users/gosu/.codex/skills/design-md/scripts/list_styles.py --search dashboard
```

Install one style into the current project:

```bash
python3 /Users/gosu/.codex/skills/design-md/scripts/apply_design_md.py linear.app .
```

Check whether upstream has changed:

```bash
python3 /Users/gosu/.codex/skills/design-md/scripts/update_upstream.py --check
```

`--check` prints JSON and exits with code `2` when an update is available, so automation can distinguish "changed" from "failed".

Refresh the bundled style references from upstream:

```bash
python3 /Users/gosu/.codex/skills/design-md/scripts/update_upstream.py
```

Run the repository automation locally:

```bash
python3 /Users/gosu/.codex/skills/design-md/scripts/auto_update.py --commit --push
```

After updating upstream references, run:

```bash
python3 /Users/gosu/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/gosu/.codex/skills/design-md
python3 /Users/gosu/.codex/skills/design-md/scripts/list_styles.py | head
```
