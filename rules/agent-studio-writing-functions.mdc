---
description: How to write functions in Agent Studio - signatures, decorators, returns, calling patterns
tags: [agent-studio, functions, python, local-development, coding]
---

# Writing Functions in Agent Studio

## Critical: File Name Must Match Function Name

**Every Python file in `functions/` must contain a function with the same name as the file.**

This function must:
- Have the signature: `def filename(conv: Conversation, ...)` or `def filename(conv: Conversation, flow: Flow, ...)`
- Include `@func_description()` decorator
- Include `@func_parameter()` for any parameters beyond `conv` and `flow`

**Other helper functions in the same file do NOT get decorated. It will crash imports if you decorate any function other than the one that matches the file name**

### Example: Valid File Structure

**File**: `functions/collect_phone_number.py`

```python
from imports import *  # <AUTO GENERATED>

# Main function - MUST match filename and have decorators
@func_description('Collect and validate phone number from user')
@func_parameter('phone_number', 'Phone number provided by user')
def collect_phone_number(conv: Conversation, phone_number: str):
    if _is_valid_phone(phone_number):  # Helper function
        conv.state.phone = phone_number
        return "Phone number collected successfully"
    return "Please provide a valid 10-digit phone number"

# Helper function - no decorators needed
def _is_valid_phone(number: str) -> bool:
    return len(number) == 10 and number.isdigit()
```

### Common Validation Error

**Error**: `Function definition 'def myfile(conv: Conversation)' not found`

**Causes**:
1. No function matching the filename
2. Function signature has linebreaks (must be on one line)
3. Missing `conv: Conversation` parameter

**Wrong** - Linebreak in signature:
```python
def my_function(
    conv: Conversation,
    param: str
):
```

**Right** - Single line signature:
```python
def my_function(conv: Conversation, param: str):
```

### Utility Modules

If creating a pure utility module (not meant to be called by LLM), you must still include a stub function with the filename:

```python
from imports import *  # <AUTO GENERATED>

@func_description('Utility module - should not be called directly by LLM')
def my_utils(conv: Conversation):
    """Utility module with helper functions."""
    conv.log.warning("Utility module called directly", is_pii=False)
    return "This is a utility module. Import specific functions instead."

# Actual utility functions
def helper_one():
    pass

def helper_two():
    pass
```

## Naming Functions

Some functions are utility functions that the LLM will never see as callable tools; however any function that is referenced in either a KB topic or a flow step prompt as `{{fn:my_function}}` will be visible to the model.

> 💡 **BEST PRACTICE:** Often, the best way to name an LLM tool is after the event immediately proceeding its use that should prompt the LLM to call it.

> ❌ **DON'T** Name the function after what it does e.g. `store_first_name`
> ✅ **DO** Name the function after what occurrence should prompt it to be used e.g. `first_name_provided`

## Function Signatures

### Global Functions (in `functions/`)

```python
from imports import *  # <AUTO GENERATED>

@func_description('What this function does')
@func_parameter('param_name', 'Description of parameter')
def my_function(conv: Conversation, param_name: str):
    pass
```

### Flow Functions (in `functions/flow_<uuid>/`)

```python
from imports import *  # <AUTO GENERATED>

@func_description('What this function does')
def my_flow_function(conv: Conversation, flow: Flow):
    flow.goto_step("Next Step")
```

## Decorators

**ALWAYS** include:
- `@func_description()` - Brief description of what function does
- `@func_parameter()` - For each parameter (except `conv` and `flow`)

**Example**:

```python
@func_description('This function sends an SMS to the user when called.')
@func_parameter('sms_id', "The sms_id will come directly from the 'instructions' of the CONTEXT_INFORMATION dictionary when the function is called.")
def send_sms(conv: Conversation, sms_id: str):
    # implementation
```

> **💡 NOTE**: The LLM sees these function descriptions and parameters, so they should be descriptive and specific enough that the model will know exactly when/how to use them. You can include things like formatting preferences in the parameter descriptions (e.g. `@func_parameter('date', 'The date the user provided in YYYY-MM-DD format')`)

## Function Returns

### Return String for LLM System Prompts

```python
return "Tell the user that their payment was successful and ask if they need anything else."
```

### Use `conv.` Methods for Deterministic Control

```python
# Set exact utterance (agent speaks this exact phrase)
conv.say(f"Sure, no problem! Your balance is {conv.state.balance}. Is there anything else I can help with?")
```

> ⚠️ **NOTE**: It is important that the first sentence of any hard-coded utterance (i.e. an utterance returned by `conv.say()` or `return {"utterance": "..."}`) is static (i.e. does not contain an f-string variable). This is because we rely on cached audio to avoid latency and want to use the streaming time of that first static sentence to hide the latency of TTS-generation for any dynamic one.

> 💡 **SEE ALSO**: For comprehensive guidance on hard-coded utterances including multilingual support, slot filling, and chronology, see `agent-studio-utterances.mdc`.

### Navigation and Control Methods

```python
# Navigate to a flow (this enters the flow at the configured Start Step)
conv.goto_flow("payment_flow")

# Navigate to a step (within flow functions)
flow.goto_step("Confirm Payment")

# Exit current flow
conv.exit_flow()

# Transfer call
conv.call_handoff(
    destination="support",
    reason="billing_inquiry"
)

# Transfer call with utterance
conv.call_handoff(
    destination="support",
    reason="billing_inquiry",
    utterance="Let me transfer you now."
)
```

### Return Dict (Only When Needed)

```python
# End call
return {
    "hangup": True
}

# Return a specific step of a flow from not within that flow
return {
    "transition": {
        "goto_flow": "Flow Name",
        "goto_step": "Step Name"
    }
}

# Complex return combining content and utterance
return {
    "utterance": f"Sure, no problem! Your balance is {conv.state.balance}",
    "content": "Immediately call the `balance_informed` function",
    "end_turn": False
}  # NOTE: It _only_ works for the hard coded utterance to be followed by the content action, not vice versa
```

## Calling Other Functions

### Global Functions

```python
conv.functions.my_global_function(arg1, arg2)
```

### Flow Functions (Within Same Flow)

```python
flow.functions.my_flow_function(arg1, arg2)
```

## Essential Methods Quick Reference

```python
# Voice
conv.set_voice(ElevenLabsVoice("voice_id"))
conv.set_language("es-US")

# Messaging
conv.send_sms(to_number="+1234567890", content="text")

# Handoff
conv.call_handoff(destination="support", reason="billing")

# Return hard coded utterance
conv.say("utterance")

# Metrics
conv.write_metric("EVENT_NAME", value="data", write_once=True)
```

## When to Use What

| Task | Use |
|------|-----|
| Agent speaks exact phrase | `conv.say("text")` |
| Guide agent behavior | `return "instructions"` or `return {"content": "instructions"}` |
| Navigate to flow | `conv.goto_flow("flow_name")` |
| Navigate within flow | `flow.goto_step("step_name")` |
| Exit current flow | `conv.exit_flow()` |
| Transfer call | `conv.call_handoff(destination, reason)` |
| End call | `return {"hangup": True}` |
| Call another function | `conv.functions.function_name()` |
