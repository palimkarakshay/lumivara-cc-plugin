---
description: Add a new guardrail rule from a plain-English description
---
The user will describe a command (or class of commands) they never want run. Turn it into a rule for `${CLAUDE_PLUGIN_ROOT}/hooks/guardrails.config.json`:
1. Pick a short kebab-case `name`.
2. Write a precise, case-insensitive regex `pattern` that matches the dangerous command. **Test it** against the user's example AND a safe near-miss so it doesn't over-match — narrow beats broad; false positives erode trust.
3. Write a clear `message` explaining why it's blocked and how to override (`# GUARDRAIL_OK`).
Show the proposed rule and the near-miss test result, get confirmation, then append it to the `rules` array (keep valid JSON). Suggest running `/guardrail-status` to self-test afterward.
