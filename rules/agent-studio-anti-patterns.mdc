---
description: Common mistakes and anti-patterns to avoid in Agent Studio development
tags: [agent-studio, anti-patterns, mistakes, best-practices, local-development]
---

# Anti-Patterns (Never Do This)

## ❌ CRITICAL: Never Silently Swallow Errors

**WRONG**:

```python
try:
    result = external_api_call()
    parsed = ast.literal_eval(result)
except (ValueError, SyntaxError):
    pass  # NEVER DO THIS - error is silently ignored
```

**ALSO WRONG**:

```python
try:
    result = parse_data()
except Exception as e:
    print(e)  # Printing is not error handling!
    return ["ERROR"]  # Returning error flags is not proper handling
```

**WHY**: Silently swallowing errors makes debugging impossible and can lead to incorrect behavior. Users will be stuck with no clear path forward.

**RIGHT**: Always have explicit error handling with appropriate transitions, typically handoffs:

```python
try:
    result = external_api_call()
    parsed = ast.literal_eval(result)
except (ValueError, SyntaxError) as e:
    conv.log.error("Data parsing failed", error=str(e), is_pii=False)
    conv.write_metric("PARSING_ERROR")
    conv.state.handoff_reason = "parsing_error"
    return conv.functions.handoff("parsing_error")
```

**Standard PG&E Pattern for Errors**:

```python
try:
    # ... operation that might fail ...
except Exception as e:
    conv.log.error("Operation failed", error=str(e), is_pii=False)
    conv.write_metric("OPERATION_ERROR")
    conv.state.handoff_reason = "operation_error"
    return conv.functions.handoff("operation_error")
```

## ❌ Don't Forget the Main Function Matching Filename

**CRITICAL**: Every `.py` file in `functions/` must have a function with the same name as the file.

**WRONG** - No function named `address_utils` in `address_utils.py`:

```python
# File: address_utils.py
from imports import *

def parse_address(addr: str):  # Function name doesn't match filename!
    pass
```

**RIGHT** - Function matches filename:

```python
# File: address_utils.py
from imports import *

@func_description('Utility module for address parsing')
def address_utils(conv: Conversation):  # Function name matches filename
    """Utility module - not meant to be called directly."""
    return "Utility module"

def parse_address(addr: str):  # Helper functions are fine
    pass
```

**Common validation error:**
```
Function definition 'def myfile(conv: Conversation)' not found
```

This means:
1. No function matching the filename exists
2. Function signature has linebreaks (must be single line)
3. Missing `conv: Conversation` parameter

## ❌ Don't Repeat Yourself (DRY Violation)

**WRONG**: Defining the same utility function in multiple files:

```python
# In verify_address.py
def _parse_address_list(llm_response: str) -> list[str]:
    # ... implementation ...

# In verify_unit_number.py
def _parse_address_response(llm_response: str) -> list[str]:
    # ... same implementation ...

# In test_address_parsing.py
def _parse_address_list(llm_response: str) -> list[str]:
    # ... same implementation again ...
```

**WHY**: Duplicated code leads to:
- Bugs when you fix an issue in one place but not others
- Inconsistent behavior across the codebase
- Maintenance nightmares

**RIGHT**: Create a shared utility module and import it:

```python
# In functions/address_utils.py
def parse_address_list(llm_response: str) -> list[str]:
    """Parse LLM response and return list of addresses."""
    # ... single source of truth ...

# In verify_address.py
from functions.address_utils import parse_address_list

def verify_address(conv: Conversation, flow: Flow, address: str):
    matched_addresses = parse_address_list(conv, llm_response)
    # ...
```

**When to create shared utilities:**
- Function is used in 2+ places
- Function is pure logic (doesn't depend on flow/step state)
- Function is a helper for common operations (parsing, validation, formatting)

## ❌ Don't Mix Instructions and Function Calls in Content

**WRONG**:

```python
return {
    "content": f"Tell the user their balance is {conv.state.balance}, then call {{fn:make_payment}}"
}
```

**WHY**: Our in-house LLM doesn't support instructing the model to both say something and call a function in the same turn.

**RIGHT**:

```python
# Either give instructions:
return f"Tell the user their balance is {conv.state.balance} and offer to help with payment"

# OR combine a hard coded utterance with additional prompting
conv.say(f"Your balance is {conv.state.balance}.")
return "Depending on what the user says, you can offer to make a payment"

# However, note that the prompting will not be seen on the same turn unless you return a dictionary with end_turn=False
return {
    "utterance": f"Your balance is {conv.state.balance}.",
    "content": "Immediately offer to help make a payment.",
    "end_turn": False
}
```

## ❌ Don't Forget Decorators

**WRONG**:

```python
def my_function(conv: Conversation, amount: float):
    process_payment(amount)
```

**RIGHT**:

```python
@func_description('Process a payment')
@func_parameter('amount', 'Payment amount in dollars')
def my_function(conv: Conversation, amount: float):
    process_payment(amount)
```

## ❌ Don't Decorate Helper Functions

**CRITICAL**: Only the function matching the filename should have decorators. Decorating helper functions **will crash imports**.

**WRONG** - Decorating helper functions:

```python
# File: payment_utils.py
from imports import *

@func_description('Payment utilities')
def payment_utils(conv: Conversation):
    """Utility module."""
    return "Utility module"

@func_description('Validate payment amount')  # ❌ WRONG - will crash!
@func_parameter('amount', 'Amount to validate')  # ❌ WRONG - will crash!
def validate_amount(amount: float) -> bool:
    return amount > 0
```

**RIGHT** - Only decorate the main function:

```python
# File: payment_utils.py
from imports import *

@func_description('Payment utilities')
def payment_utils(conv: Conversation):
    """Utility module."""
    return "Utility module"

# Helper functions - NO decorators
def validate_amount(amount: float) -> bool:
    return amount > 0

def format_currency(amount: float) -> str:
    return f"${amount:.2f}"
```

**WHY**: The decorator system only expects the main function (matching the filename) to be decorated. Adding decorators to helper functions breaks the import mechanism and causes runtime errors.

**Rule**: One file = one decorated function (matching the filename). All other functions in the file are helpers and must NOT be decorated.

## ❌ Don't Manually Import Poly Platform Content into Function Files

**WRONG**:

```python
from poly_platform.function_runtime import Conversation
import re

def my_function(conv: Conversation):
    return re.match(r'\d{10}', conv.caller_number)
```

**RIGHT**:

```python
from imports import *  # <AUTO GENERATED>
import re

def my_function(conv: Conversation):
     return re.match(r'\d{10}', conv.caller_number)
```

## ❌ Don't Use Hard-Coded Values

**WRONG**:

```python
conv.say("Call us at 1-800-123-4567 for help.")
return {"hangup": True}
```

**RIGHT**:

```python
support_number = conv.variant.support_phone_number
conv.say(f"Call us at {support_number} for help.")
return {"hangup": True}
```

## ❌ Don't Forget Flow Navigation

**WRONG** (flow function):

```python
def my_flow_function(conv: Conversation, flow: Flow):
    conv.state.data_collected = True
    # Function ends without calling flow.goto_step() or returning a transition, meaning it will stay on the same step prompt
```

**RIGHT**:

```python
def my_flow_function(conv: Conversation, flow: Flow):
    conv.state.data_collected = True
    flow.goto_step("Next Step")  # Always navigate
```

## ❌ Don't Write Duplicate Metrics

**WRONG**:

```python
for i in range(5):
    conv.write_metric("FLOW_ENTERED", "payment")  # Written 5 times!
```

**RIGHT**:

```python
conv.write_metric("FLOW_ENTERED", "payment", write_once=True)  # Written once
```

## ❌ Don't Forget Logging

**WRONG**:

```python
def my_function(conv: Conversation):
    result = external_api_call()
    # Silent failure if API fails
    return process_result(result)
```

**RIGHT**:

```python
def my_function(conv: Conversation):
    try:
        result = external_api_call()
        conv.log.info("API call succeeded", status=result.status_code)
        return process_result(result)
    except Exception as e:
        conv.log.error("API call failed", error=str(e))
        return "There was a technical issue. Let me transfer you to someone who can help."
```

## ❌ Don't Put Deterministic Logic in Prompts

**WRONG**:

```yaml
prompt: |-
  If $num_appts == 0: Go to Offer Make Appointment
  If $num_appts == 1: Go to Recite Details
  If $num_appts > 1: Ask which appointment
```

**RIGHT**: Handle in Python, then transition to the appropriate step:

```python
def load_appointments(conv: Conversation):
    num_appts = conv.state.num_appts

    if num_appts == 0:
        return transition(flow="appointments", step="Offer Make Appointment")
    elif num_appts == 1:
        return transition(flow="appointments", step="Recite Details")
    else:
        return transition(flow="appointments", step="Ask Which")
```

## ❌ Don't Create Separate "Anything Else" Steps

**WRONG** - Creating a dedicated step just to ask if there's anything else:

```python
def user_done(conv: Conversation, flow: Flow):
    flow.goto_step("Anything Else")  # DON'T create a step just for this
    return "Ask if there's anything else."
```

**RIGHT** - Exit the flow and return prompting directly:

```python
def user_done(conv: Conversation, flow: Flow):
    conv.exit_flow()
    return "Ask if there's anything else you can help with."
```

**WHY**: Creating a separate step adds unnecessary complexity. The prompting can be delivered directly when exiting the flow.

## ❌ Don't Misuse `end_turn=False`

**WRONG** - Using `end_turn=False` when asking a question that needs user input:

```python
return {
    "transition": {
        "goto_flow": "appointments",
        "goto_step": "Ask Intent"
    },
    "utterance": "Hi, welcome!",
    "content": "Ask what the user needs.",
    "end_turn": False  # WRONG - user needs to respond
}
```

**RIGHT** - Include the complete question in the utterance:

```python
# In utterances.py
APPT_GREETING = {
    "en-US": "Hi, welcome! Are you calling to make, review, or cancel an appointment?",
    "es-US": "Hola, bienvenido! ¿Llama para hacer, revisar o cancelar una cita?",
}

# In code
return {
    "transition": {
        "goto_flow": "appointments",
        "goto_step": "Ask Intent"
    },
    "utterance": Utterances.APPT_GREETING(conv)
}
```

**RIGHT USE of end_turn=False** - Agent immediately calls function after speaking:

```python
return {
    "utterance": f"Your balance is {conv.state.balance}.",
    "content": "Immediately call balance_informed to continue.",
    "end_turn": False
}
```

**WHY**:
- `end_turn=False` is a rare pattern for agent-initiated actions, not user responses
- Including the question in the utterance is clearer and more maintainable
- The step will naturally handle collecting the user's response

## ❌ Don't Combine `conv.exit_flow()` with Flow Transitions

**WRONG**: Using `conv.exit_flow()` followed by a transition or function call that handles flow routing:

```python
# Example 1: exit_flow + return transition
conv.exit_flow()
return transition(flow="appointments", step="Start")

# Example 2: exit_flow + goto_flow
conv.exit_flow()
conv.goto_flow("some_flow")
return ...

# Example 3: exit_flow + function that transitions
conv.exit_flow()
return authenticate(conv)
```

**WHY**: The `transition()`, `goto_flow()`, or function return overrides the `exit_flow()`, making it redundant.

**RIGHT**: Let the transition or function handle the flow routing:

```python
# Example 1: Just return the transition
return transition(flow="appointments", step="Start")

# Example 2: Just use goto_flow
conv.goto_flow("some_flow")
return ...

# Example 3: Let the function handle it
return authenticate(conv)

# Example 4: ONLY use exit_flow when staying in place or returning content
conv.exit_flow()
return "Is there anything else I can help with?"
```

**When to use `conv.exit_flow()`:**
- When exiting the flow and returning content/prompting (no transition)
- When you want to exit back to the parent flow without specifying where to go

**When NOT to use `conv.exit_flow()`:**
- Before `return transition(...)` - the transition handles it
- Before `conv.goto_flow(...)` - goto_flow handles it
- Before calling functions that manage flow routing (like `authenticate()`, `handoff()`, etc.)
