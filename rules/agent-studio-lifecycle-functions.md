---
description: Start and end function patterns in Agent Studio
tags: [agent-studio, lifecycle, start-function, end-function, local-development]
---

# Lifecycle Functions

## Start Function

Runs **once at call start** (before first user input). **Only takes `conv` argument, no `@func_parameter` required**:

```python
from imports import *

@func_description('Start function')
def start_function(conv: Conversation):
    # Initialize state
    conv.state.user_authenticated = False
    conv.state.app_tags = []

    # Extract SIP headers
    conv.state.shared_id = conv.sip_headers.get("X-CallUID", "")

    # Set language
    if conv.callee_number == "+15551234567":
        conv.set_language("es-US")

    # Write initial metrics
    conv.write_metric("CALL_START")

    # Route to initial flow
    conv.goto_flow("authentication")
```

## End Function

Runs **once at call end** (after call completes):

```python
from imports import *

def end_function(conv: Conversation):
    # Aggregate metrics
    topics = [m.value for m in conv.metric_events if m.name == "TOPIC_TRIGGERED"]

    # Write summary metrics
    conv.write_metric("TOPICS_DISCUSSED", len(set(topics)))
    conv.write_metric("CALL_OUTCOME", conv.state.get("outcome", "unknown"))

    # Send post-call webhook if needed
    if conv.env == "live":
        trigger_webhook(conv)
```
