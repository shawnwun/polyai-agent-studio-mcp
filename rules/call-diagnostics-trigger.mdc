---
alwaysApply: true
---

# Call Diagnostics — Auto-Trigger

Whenever the user pastes a **call SID** (patterns below), **immediately** run
`call-diagnostics` (or `python scripts/get_call_diagnostics.py`) to fetch the
call logs. Do not ask — just do it.

## Call SID patterns

- `AS_CHAT_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `KAxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `OUT-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `TESTING_CHAT_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Any UUID that looks like a conversation identifier

## Quick command

```bash
python scripts/get_call_diagnostics.py <call_sid> \
  --account-id <account> --project-id <project> [--region us-1]
```

Determine `account-id` and `project-id` from the workspace context
(look for `project.json` or the directory path
`agents/<team>/<account-id>/<project-id>/`).
Default region is `us-1`; other options: `uk-1`, `euw-1`.
