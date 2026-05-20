---
name: claude-design
description: Design one-off HTML artifacts, landing pages, decks, prototypes, option boards, and motion studies in Codex using a Claude Design-inspired CLI/API workflow.
---

# Claude Design

Use this skill for one-off design artifacts: landing pages, teaser pages, high-fidelity prototypes, HTML decks, component explorations, visual option boards, onboarding flows, dashboard concepts, and motion studies.

This is the Codex-adapted wrapper. The upstream Hermes source is bundled at `../../references/claude-design/SKILL.md` for provenance and deeper process guidance.

## Core Rules

- Start from context, not vibes. Read supplied docs, screenshots, existing repo files, brand assets, tokens, or prior mockups before designing.
- Default deliverable is a complete local HTML artifact only when the user did not ask for production code in an existing repo.
- If the user asks for implementation in a repo, use the repo's actual stack and component system.
- Pair with `../popular-web-designs/SKILL.md` when the user wants a known website style.
- Pair with `../design-md/SKILL.md` when the deliverable is a persistent `DESIGN.md` token spec.
- Avoid generic AI design tropes. Commit to a clear visual point of view tied to the product and audience.
- Do not copy protected logos, screenshots, proprietary copy, or paid fonts.

## Workflow

1. Understand the brief.
   - What is being designed?
   - Who is it for?
   - Is the deliverable standalone HTML, a repo implementation, a deck, or a prototype?

2. Gather context.
   - For repos, read theme files, tokens, global CSS, components, and representative pages.
   - For known-brand references, load one template from `../../references/popular-web-designs/templates/<slug>.md`.

3. Define the artifact system.
   - Colors, type, spacing, radii, shadows, motion posture, component treatment, and interaction rules.

4. Build.
   - Use a self-contained HTML file for standalone artifacts.
   - Use existing framework/components for repo work.
   - Preserve previous versions for major standalone revisions.

5. Verify.
   - Confirm files exist.
   - Run syntax/static checks when available.
   - Open in a browser when visual fidelity matters.
   - Check console errors, primary viewport, and mobile behavior when relevant.

6. Report briefly.
   - Exact file path.
   - What was created or changed.
   - Verification performed.
   - Any caveats or intentional deviations.

## When Not To Use

- Pure token-spec authoring: use `design-md`.
- A named website style without a broader design process: use `popular-web-designs`.
- A small existing UI bugfix where the project design system is already clear.

## Bundled Upstream

- `../../references/claude-design/SKILL.md`: original Hermes Agent `claude-design` skill.
- `../../references/upstreams/hermes-agent.json`: source commit and update metadata.
