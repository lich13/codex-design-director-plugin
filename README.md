# Codex Design Director

Codex Design Director packages curated frontend design references as a Codex plugin.

It combines:

- `design-director`: routing skill that chooses the right design workflow and visual reference.
- `design-md`: project-level `DESIGN.md` directions from `VoltAgent/awesome-design-md`.
- `claude-design`: Codex-adapted one-off artifact workflow, with upstream Hermes source preserved.
- `popular-web-designs`: Codex-adapted real website-inspired HTML/CSS templates from Hermes.
- `frontend-design`: frontend execution guidance from Anthropic Claude Code.

## Install

```bash
codex plugin marketplace add lich13/codex-design-md-skill
```

If the marketplace already exists:

```bash
codex plugin marketplace upgrade lich13-design
```

The plugin is installed from:

```text
plugins/design-director/
```

## Verify Locally

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/design-director/.codex-plugin/plugin.json >/dev/null
plugins/design-director/scripts/validate-references.py
plugins/design-director/scripts/list-design-sources.py
plugins/design-director/scripts/pick-design-direction.py --deliverable design.md "data dense SaaS ops dashboard"
```

After installing or upgrading the marketplace:

```bash
rg -n 'design-director|popular-web-designs|claude-design' ~/.codex/plugins/cache/lich13-design
```

This plugin does not define an MCP server; it exposes skills and bundled references.

## Upstream Sources

- `VoltAgent/awesome-design-md`: bundled `DESIGN.md` references, MIT.
- `NousResearch/hermes-agent`: upstream `claude-design` and `popular-web-designs`, MIT.
- `anthropics/claude-code`: upstream `frontend-design` skill metadata.

Source metadata and licenses are stored under:

```text
plugins/design-director/references/upstreams/
plugins/design-director/licenses/
```

## Update References

```bash
plugins/design-director/scripts/sync-upstreams.py
plugins/design-director/scripts/validate-references.py
```

GitHub Actions runs the same sync and validation flow on a schedule.

## Brand Safety

Bundled references are visual direction only. Do not copy protected logos, screenshots, proprietary copy, paid fonts, or private assets unless the user supplies rights.
