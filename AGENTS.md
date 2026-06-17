# guardrails (Claude Code plugin)

**What:** config-driven PreToolUse guardrails for Claude Code + commands to view/add rules. Public MIT (palimkarakshay).
**Stack:** no build — a python3 hook (stdlib only) + JSON config + markdown commands.

## Layout
- `.claude-plugin/{plugin.json,marketplace.json}` — plugin name `guardrails`, marketplace `lumivara`.
- `hooks/hooks.json` → `hooks/guardrails.py` (engine) + `hooks/guardrails.config.json` (**edit this** — rules).
- `commands/{guardrail-status,add-guardrail}.md`.

## Verify
- `python3 -c "import json;[json.load(open(f)) for f in ['.claude-plugin/plugin.json','.claude-plugin/marketplace.json','hooks/hooks.json','hooks/guardrails.config.json']]"`
- Pipe a DENY + an ALLOW PreToolUse JSON through `hooks/guardrails.py` (see README).

## Gotchas
- Rules match the LOWERCASED command; keep patterns NARROW (false positives erode trust). `# GUARDRAIL_OK` overrides; `--allow-secrets` skips the commit scan.
- Fail-open by design (missing/invalid config or any error → allow).
- This is the GENERIC public version; an operator's live config is private and project-specific.
