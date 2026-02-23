---
description: State management and metrics tracking in Agent Studio
tags: [agent-studio, state, metrics, conv.state, local-development]
---

# State Management and Metrics

## State Management

### Setting State Variables

**Use `conv.state` to persist data**:

```python
conv.state.user_authenticated = True
conv.state.payment_amount = 150.00
conv.state.handoff_reason = "billing_inquiry"
```

### Access State Variables

```python
if conv.state.user_authenticated:
    proceed_with_request()
```

Do NOT use `getattr` to access state variables, instead use `conv.state.variable_name`. 
If the state variable doesn't exist, this will return `None`

### Referencing State in Prompts

In prompts (flow steps, KB actions), use `$variable` notation:

```yaml
prompt: |-
  $spanish_prompt
  Your balance is $balance.
```

Do NOT use `conv.state.variable` in prompts - that's Python-only syntax.

### Important Limitation

Our prompt templating does **not** support attribute access like `$variable.attribute`.

If you need to show structured state in a prompt, you must stringify it in Python first:

```python
# Set a string representation
conv.state.selected_appointment_details = f"Date: {appt.date}, Time: {appt.time}"

# Then reference in prompt
# $selected_appointment_details
```

## Counters within Flows

Use state counters within flow functions to ensure we don't loop endlessly around the same function:

```python
from functions.utils import account_id_is_valid
from functions.handoff import handoff

@func_description('Store the provided account ID')
@func_parameter('account_id', 'the account id provided by the user')
def store_account_id(conv: Conversation, flow: Flow, account_id: str):
    if account_id_is_valid(account_id):
        flow.goto_step('Collect Date of Birth')
        return
    else:
        # initialize counter
        if not conv.state.account_id_counter:
            conv.state.account_id_counter = 1
            return "Tell the user that's not a valid id and ask again"

        # iterate counter
        else:
            conv.state.account_id_counter += 1

        # id still not valid on third attempt
        if conv.state.account_id_counter > 2:
            return handoff(conv, handoff_reason="account_id_collection_fail")

        return "Tell the user that's not a valid id and ask again"
```

## Metrics

### Writing Metrics

**DO** write metrics to track important events:

```python
conv.write_metric("PAYMENT_COMPLETED")
conv.write_metric("PAYMENT_AMOUNT", 150.00)
conv.write_metric("SMS_ACCEPTED", write_once=True)
```

### Metrics During Flow Traversal

```python
def my_flow_function(conv: Conversation, flow: Flow):
    # Track flow entry
    conv.write_metric("FLOW_ENTERED", "payment_flow")

    # Track decisions
    if user_accepted_offer:
        conv.write_metric("OFFER_ACCEPTED")
    else:
        conv.write_metric("OFFER_DECLINED")
```

### Metric Naming Conventions

**Use SCREAMING_SNAKE_CASE**:

```python
conv.write_metric("AUTH_SUCCESS")
conv.write_metric("PAYMENT_COMPLETED")
conv.write_metric("HANDOFF_REASON", "billing")
```

**Group related metrics with prefixes**:

```python
conv.write_metric("SMS_OFFERED")
conv.write_metric("SMS_ACCEPTED")
conv.write_metric("SMS_SENT")
conv.write_metric("SMS_FAILED")
```

## Metrics Documentation File

### Purpose

Maintain a local `metrics.yaml` (or `<feature>_metrics.yaml`) file to document all metrics used in your project. This serves as:
- **Documentation** for the team about what each metric tracks
- **Single source of truth** for metric names and types
- **Validation reference** to ensure consistency
- **Onboarding guide** for new developers

### File Format

```yaml
# Section Header (use comments to organize)
METRIC_NAME:
  description: Clear explanation of what this metric tracks
  type: bool | string | int | float
  can_repeat: true  # Optional: for metrics written multiple times in a call
  values:           # Optional: for string enums
    - VALUE1
    - VALUE2
```

### Complete Example

```yaml
# Authentication Flow
AUTH_ATTEMPT:
  description: User attempted authentication
  type: bool

AUTH_SUCCESS:
  description: User successfully authenticated
  type: bool

AUTH_METHOD:
  description: Method used for authentication (phone, account, meter)
  type: string
  values:
    - phone
    - account
    - meter

AUTH_FAILED_REASON:
  description: Reason authentication failed (numeric code)
  type: string

# Payment Flow
PAYMENT_INITIATED:
  description: User started payment process
  type: bool

PAYMENT_AMOUNT:
  description: Payment amount in dollars
  type: float

PAYMENT_METHOD:
  description: Payment method used
  type: string
  values:
    - card
    - bank_account

PAYMENT_DECLINED:
  description: Payment was declined by processor
  type: bool
  can_repeat: true  # Can be declined multiple times

# Handoff Tracking
HANDOFF_REASON:
  description: Reason for transfer to CSR
  type: string

HANDOFF_DESTINATION:
  description: Queue or number transferred to
  type: string
```

### Field Descriptions

**`description`** (required):
- Clear, concise explanation of what the metric tracks
- Should help anyone understand when/why it's written
- Include context about what value means if not obvious

**`type`** (required):
- `bool` - True/False flags (most common)
- `string` - Text values (reasons, IDs, states)
- `int` - Whole numbers (counts, IDs)
- `float` - Decimal numbers (amounts, durations)

**`can_repeat`** (optional):
- Set to `true` if metric can be written multiple times in a single call
- Default is `false` (metric written once per call)
- Example: `PAYMENT_DECLINED` might happen multiple times

**`values`** (optional):
- List of allowed string values for enum-style metrics
- Helps document expected values
- Example: `AUTH_METHOD` should only be "phone", "account", or "meter"

### File Location

Place metrics files in your project root:

```
project/
├── metrics.yaml                    # Main metrics
├── appointment_metrics.yaml        # Feature-specific metrics
├── payment_metrics.yaml            # Another feature
└── functions/
```

### Naming Conventions

**Metrics should be:**
- `SCREAMING_SNAKE_CASE`
- Descriptive and unambiguous
- Grouped with prefixes for related metrics

**Good naming:**
```yaml
SMS_OFFERED:
  description: Agent offered to send SMS
  type: bool

SMS_ACCEPTED:
  description: User accepted SMS offer
  type: bool

SMS_SENT:
  description: SMS successfully sent
  type: bool

SMS_FAILED:
  description: SMS sending failed
  type: bool
```

**Bad naming:**
```yaml
sms:           # Not SCREAMING_SNAKE_CASE
  type: bool

SENT:          # Too vague - sent what?
  type: bool

USER_SAID_YES:  # Not specific enough
  type: bool
```

### Organizing Metrics

Group related metrics with comments:

```yaml
# === Authentication Flow ===

AUTH_ATTEMPT:
  description: User attempted authentication
  type: bool

AUTH_SUCCESS:
  description: Successfully authenticated
  type: bool

# === Payment Processing ===

PAYMENT_INITIATED:
  description: Payment flow started
  type: bool

PAYMENT_COMPLETED:
  description: Payment successfully processed
  type: bool

# === Error Handling ===

API_ERROR:
  description: External API call failed
  type: bool
  can_repeat: true

HANDOFF_REASON:
  description: Reason for transfer to CSR
  type: string
```

### Maintaining the File

**When adding new metrics:**
1. Add to appropriate section in metrics.yaml
2. Include clear description
3. Specify correct type
4. Add `can_repeat: true` if applicable
5. List `values` if it's an enum

**When removing metrics:**
1. Don't delete immediately - mark as deprecated
2. Add comment: `# DEPRECATED: Use NEW_METRIC_NAME instead`
3. Remove after confirming no longer used

**Version control:**
- Commit metrics.yaml alongside code changes
- Review in pull requests
- Keep up to date with code

### Example: Full Project Metrics File

```yaml
# Entry & Intent Detection
APPOINTMENTS_FLOW_DISABLED_FALLBACK:
  description: Fired when appointments_enabled=False, falling back to existing KB logic
  type: bool

APPOINTMENT_INTENT:
  description: Initial user intent (make, review, cancel, reschedule, general)
  type: string
  values:
    - make
    - review
    - cancel
    - reschedule
    - general

# API Interactions
FIELD_ACTIVITIES_API_ERROR:
  description: API error loading field activities
  type: bool

NUM_APPOINTMENTS:
  description: Count of readable appointments found
  type: int

# User Actions
APPOINTMENT_SELECTED:
  description: User selected a specific appointment (FAT code)
  type: string

CANCEL_APPOINTMENT_SUCCESS:
  description: Cancellation API succeeded
  type: bool

APPOINTMENT_CONFIRMED:
  description: User confirmed appointment details
  type: bool

# Handoff Tracking
APPOINTMENT_WINDOW_ATTEMPTS_EXCEEDED:
  description: User declined 3+ times, transferring to CSR
  type: bool
```

### Benefits

✅ **Documentation** - Clear record of what each metric means
✅ **Consistency** - Team uses same metric names
✅ **Validation** - Easy to check if metrics are used correctly
✅ **Onboarding** - New developers understand metrics quickly
✅ **Analytics** - Data team knows what metrics exist and their types
✅ **Debugging** - Quick reference when troubleshooting

## Quick Reference

| Task | Use |
|------|-----|
| State variable reference in prompt | `$variable` |
| State variable reference in function | `conv.state.variable` |
| Store data across turns | `conv.state.variable = value` |
| Track analytics | `conv.write_metric("NAME", value)` |
| Log debugging info | `conv.log.info("message")` |
| Document metrics | Create/update `metrics.yaml` file |
