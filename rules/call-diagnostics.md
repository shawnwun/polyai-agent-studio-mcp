---
description: Detailed documentation for the call diagnostics script — usage, options, output format, and debugging workflow
---

# Call Diagnostics Script

## Overview

[get_call_diagnostics.py](mdc:scripts/get_call_diagnostics.py) fetches comprehensive
call diagnostics from PolyAI conversations via the Jupiter API and formats them as
markdown (or JSON) for debugging and analysis.

## Location

```
scripts/get_call_diagnostics.py
```

Installed as a CLI entry point: `call-diagnostics`

## Usage

```bash
# Via entry point
call-diagnostics <call_sid> --account-id <account> --project-id <project>

# Via python
python scripts/get_call_diagnostics.py <call_sid> --account-id <account> --project-id <project>
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `call_sid` | Conversation ID (required positional arg) | — |
| `--account-id` | Account ID (e.g. `pge-us`). Prompts if omitted. | — |
| `--project-id` | Project ID (e.g. `PROJECT-852ddc1d`). Prompts if omitted. | — |
| `--region` | `us-1`, `uk-1`, or `euw-1` | `us-1` |
| `--format` | `markdown`, `json`, or `text` | `markdown` |
| `--verbose` / `-v` | Show full state changes, API logs, all details | off |
| `--exclude-state` | State key patterns to exclude (supports `/regex/`) | — |
| `--no-auto-refresh` | Skip automatic `polyctx` token refresh | off |

### Examples

```bash
# Basic (prompts for account/project)
call-diagnostics KA50592f7c-ebb1-4a46-af90-12703ea997ea

# With context
call-diagnostics KA50592f7c-ebb1-4a46-af90-12703ea997ea \
  --account-id pge-us --project-id PROJECT-852ddc1d

# JSON output
call-diagnostics KA50592f7c-ebb1-4a46-af90-12703ea997ea --format json

# Verbose with state exclusions
call-diagnostics KA50592f7c-ebb1-4a46-af90-12703ea997ea -v \
  --exclude-state ooh_config /delay/ /^_.*/

# Save to file
call-diagnostics <call_sid> --account-id <acct> --project-id <proj> > diagnostics.md
```

## Agent Workflow

When a user asks about a call issue:

1. **Extract the Call SID** from the query
2. **Determine account and project** from workspace context
   (directory path `agents/<team>/<account-id>/<project-id>/`, or `project.json`)
3. **Determine region** (default `us-1`, check workspace context for hints)
4. **Run the script** and wait for output
5. **Analyze** the markdown output:
   - Agent responses — find the problematic text
   - Function calls — check arguments, results, state changes
   - State changes — look for variables that caused the issue
   - Logs — check for errors or unexpected values
   - Turn sequence — understand the flow
6. **Diagnose and fix** the root cause

## Output Format

The markdown output includes:

- **Call Information**: Account, project, duration, channel, etc.
- **Call-Level Metrics**: Collapsible table of all metrics
- **Final Context State**: Collapsible JSON of end-of-call state
- **Conversation Turns**: Each turn shows:
  - User input and agent response
  - Latency / barge-in / intent badges
  - Function calls (arguments, results, state changes, logs)
  - Turn-level state changes (smart compact formatting)
  - Turn-level logs (errors in compact mode, full in verbose)
  - Turn-level metrics

## State Variable Exclusion

Exclude noisy state keys with literal names or `/regex/` patterns:

```bash
--exclude-state ooh_config /delay/ /^_.*/ /^internal_.*/i
```

## Authentication

The script handles `polyctx` authentication automatically:
- Checks `~/.polyctx/token-platform-{region}` for a valid token
- If expired/missing, runs `polyctx profile {region}` to refresh
- If that fails, tells the user to run `polyctx profile {region}` manually

## Dependencies

- Python 3.8+
- `requests` library — install via `pip install requests` or `pip install .[tools]`
- `polyctx` CLI tool installed and configured

## Troubleshooting

| Error | Fix |
|-------|-----|
| "Could not obtain bearer token" | Run `polyctx profile <region>` |
| "Failed to fetch from Jupiter API: 404" | Verify call SID, account, project, and region |
| "Account ID is required" | Pass `--account-id` or let script prompt |
