---
description: Show and self-test the active guardrail rules
---
Report the guardrails:
1. Read `${CLAUDE_PLUGIN_ROOT}/hooks/guardrails.config.json` and list each rule (`name` + what it blocks), plus whether the commit secret-scan is enabled.
2. Confirm a `PreToolUse` Bash hook points at `hooks/guardrails.py` (in this plugin and/or the user's `settings.json`).
3. Self-test: pipe one DENY sample (a command matching a rule) and one ALLOW sample (`ls`) as PreToolUse JSON through `hooks/guardrails.py`; confirm one denies and one allows.
Note that denials are appended to `~/.local/state/guardrail-denies.log`, and `# GUARDRAIL_OK` overrides a false positive.
