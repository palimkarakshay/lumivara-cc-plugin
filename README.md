# guardrails — a Claude Code plugin

Turn your standing rules into **machine-enforced** blocks. A `PreToolUse` hook denies Bash commands (and `git commit`s containing secrets) that match configurable rules — so a forbidden action is stopped automatically, **even under bypass-permissions mode** (hooks are a separate gate from the permission prompt).

Standing rules enforced by discipline get violated eventually. A hook makes them automatic.

## What it does
- **Config-driven rules** — `hooks/guardrails.config.json` holds `{name, pattern (regex), message}` entries; a Bash command whose (lowercased) text matches a `pattern` is denied. Ships with **example** rules you adapt:
  - block an expensive LLM SKU (cost guardrail), protect a named instance from `stop`, refuse `0.0.0.0` binds, refuse cross-arch installs.
- **Secret scanner** — denies a `git commit` whose staged diff contains secret markers (API keys, private keys).
- **Fail-open** — any error → the command is allowed (never wedges a session).
- **Deny-log** — every block is appended to `~/.local/state/guardrail-denies.log` (`$GUARDRAILS_LOG`).
- **Overrides** — append `# GUARDRAIL_OK` to a command to bypass a false positive; `--allow-secrets` for the commit scanner.

## Commands
- `/guardrail-status` — list rules + self-test.
- `/add-guardrail` — turn a plain-English "never run X" into a rule.

## Install
```
/plugin marketplace add palimkarakshay/lumivara-cc-plugin
/plugin install guardrails@lumivara
```
Then edit `hooks/guardrails.config.json` (or point `$GUARDRAILS_CONFIG` at your own file) with rules for your project. Run `/guardrail-status` to verify.

## Quick test
```bash
# DENY (matches the example LLM-cost rule):
echo '{"tool_name":"Bash","tool_input":{"command":"gemini -m gemini-2.5-pro hi"}}' | python3 hooks/guardrails.py
# ALLOW:
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | python3 hooks/guardrails.py
```

## Use at user level (without the plugin)
Copy `hooks/guardrails.py` + `guardrails.config.json` somewhere, then add to `~/.claude/settings.json`:
```json
{ "hooks": { "PreToolUse": [ { "matcher": "Bash",
  "hooks": [ { "type": "command", "command": "python3 /path/to/guardrails.py", "timeout": 10 } ] } ] } }
```

MIT licensed. Python 3, standard library only.
