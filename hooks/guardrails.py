#!/usr/bin/env python3
"""Claude Code PreToolUse guardrails — machine-enforce your project's standing rules.

Denies Bash commands (and git commits containing secrets) that match configurable rules, so a
forbidden action is stopped automatically — even under bypass-permissions mode (hooks are a
separate gate from the permission prompt).

Fail-OPEN by design: any parse/exec error -> ALLOW (never wedges a session).

Rules live in `guardrails.config.json` next to this script (override path with $GUARDRAILS_CONFIG).
Each rule: {"name", "pattern" (Python regex, matched against the LOWERCASED command), "message"}.
Plus an optional git-commit secret scanner (scans `git diff --cached`).

Overrides: append `# GUARDRAIL_OK` to a command to bypass a false positive; `--allow-secrets` for
the commit scanner. Denials are appended to $GUARDRAILS_LOG (default ~/.local/state/guardrail-denies.log).
"""
import sys, os, json, re, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.environ.get("GUARDRAILS_CONFIG", os.path.join(HERE, "guardrails.config.json"))


def allow():
    sys.exit(0)


def log_deny(name, cmd):
    try:
        p = os.path.expanduser(os.environ.get("GUARDRAILS_LOG", "~/.local/state/guardrail-denies.log"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a") as f:
            f.write("%sZ\t%s\t%s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                                       name, (cmd or "")[:200].replace("\n", " ")))
    except Exception:
        pass


def deny(name, message, cmd):
    log_deny(name, cmd)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "⛔ guardrail [%s] — %s" % (name, message),
    }}))
    sys.exit(0)


try:
    data = json.load(sys.stdin)
except Exception:
    allow()

if data.get("tool_name") != "Bash":
    allow()
cmd = (data.get("tool_input") or {}).get("command", "") or ""
if "GUARDRAIL_OK" in cmd:
    allow()
low = cmd.lower()

try:
    cfg = json.load(open(CONFIG))
except Exception:
    allow()  # no/invalid config -> nothing to enforce, fail open

for rule in cfg.get("rules", []):
    try:
        if re.search(rule["pattern"], low):
            deny(rule.get("name", "rule"), rule.get("message", "blocked by a guardrail rule"), cmd)
    except (re.error, KeyError):
        continue

ss = cfg.get("secret_scan", {})
if ss.get("enabled") and re.search(r"\bgit\b.*\bcommit\b", low) and "--allow-secrets" not in low:
    cwd = data.get("cwd") or os.getcwd()
    try:
        diff = subprocess.run(["git", "diff", "--cached", "--no-color"], cwd=cwd,
                              capture_output=True, text=True, timeout=8).stdout
    except Exception:
        diff = ""
    pat = ss.get("pattern",
                 r"(sk-[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|"
                 r"xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|AIza[0-9A-Za-z_-]{30,})")
    m = re.search(pat, diff)
    if m:
        deny("no-secrets-in-commits",
             "staged changes contain a secret-like value (%s...). Remove it, or override with --allow-secrets." % m.group(0)[:10],
             cmd)

allow()
