---
description: Agent Studio low-code flow structure, function steps, default steps, patterns
tags: [agent-studio, low-code, no-code, low-code-flows, local-development, prompting]
---

# Agent Studio Low-Code Flows

## Intro
Low-code flows, or No-code flows, are a low-code, user-friendly alternative to standard Agent Studio flows.

Low-code Flows let you build conversational workflows visually — using prompts, entity extraction, and clear branching — without writing code — unless you explicitly choose to use a Function step for advanced logic.

Low-code flows serve the same purpose as no-code flows.

Low-code flows are multi-step conversational processes defined in `flows/<flow_name>/`. Each flow consists of:
- **`flow_config.yaml`**: Flow metadata (name, description, start_step)
- **`steps/*.yaml`**: Default steps that collect information and make LLM-driven decisions
- **`function_steps/*.py`**: Python functions for business logic and side effects

## Flow Configuration (`flow_config.yaml`)

```yaml
name: Flow Name
description: Brief description of what this flow does
start_step: First Step Name
```

- **`name`**: Human-readable flow name (must match folder name when cleaned)
- **`start_step`**: The name of the first step in the flow (not the filename or ID)

## Default Steps (`steps/*.yaml`)

Default steps guide the LLM through information collection and decision-making. Each step has:

**Core Structure:**
```yaml
step_type: default_step
name: Step Name
conditions:
  - name: Condition Name
    condition_type: step_condition  # or exit_flow_condition
    description: When this condition should trigger
    child_step: Next Step Name  # omit for exit_flow_condition
    required_entities:
      - entity_name
extracted_entities:
  - entity_name
prompt: |-
  Instructions for the LLM on what to do in this step
```

**Condition Types:**

1. **`step_condition`** — Transitions to another step (default or function step)
   - Use for moving to the next default step or calling a function step
   - The platform automatically determines if `child_step` is a function or default step
   - **CRITICAL**: Always use `step_condition`, never `function_step_condition` in YAML
   - `required_entities`: Entities that must be collected before this condition triggers
   - `child_step`: How to reference the next step depends on its type:
     - **Default step** → use the step's human-readable `name:` field (e.g. `child_step: Collect Date of Birth`)
     - **Function step** → use the Python filename without `.py` extension, in `snake_case` (e.g. `child_step: process_cancellation`)
     - **CRITICAL**: Function steps do NOT have a `name:` field — never use a human-readable title for them

2. **`exit_flow_condition`** — Exits the flow and returns to general conversation
   - Use when the user cancels, declines, or the flow reaches a natural end point
   - No `child_step` field needed
   - `required_entities` can be empty or specify entities for conditional exits

**Extracted Entities:**
- List entities that should be extracted during this step
- Entities are defined in `config/entities.yaml`
- Use `{{entity:entity_name}}` in prompts to reference entity values

**Prompt Best Practices:**
- Use markdown headers (`##`, `#`) to structure multi-part instructions
- Be explicit about the order of operations
- Include validation rules and edge cases
- Use `{{entity:entity_name}}` to reference entity values
- Use `{{vrbl:VARIABLE-ID}}` for dynamic variables (rarely needed)
- Format for voice: "read digit by digit", "say the full date", etc.
- Provide clear transitions: "Once X is collected, then Y"

**Key Concepts:**

- **Linear flows**: Steps progress sequentially (A → B → C)
- **Branching**: Multiple conditions lead to different paths based on user input or entity values
- **Loops**: Conditions can point back to earlier steps for corrections or retries
- **Exit points**: Use `exit_flow_condition` to allow users to leave the flow at any stage
- **Function integration**: Transition to function steps for business logic, then continue or exit
- **Entity requirements**: Use `required_entities` to ensure the LLM has collected necessary information before triggering a condition
- **Entity extraction**: Use `extracted_entities` to tell the LLM which information to gather in this step

**Design Considerations:**

- Steps can have any number of conditions (1, 2, 5, or more)
- Conditions can transition to any other step in the flow (forward, backward, or sideways)
- Mix `step_condition` (to other steps) and `exit_flow_condition` (exit flow) as needed
- Entity requirements can be empty `[]` if the condition is purely conversational
- Prompts can be short (one sentence) or detailed (multiple sections) depending on complexity
- Use markdown structure in prompts when instructing multi-part processes

## Function Steps (`function_steps/*.py`)

Function steps execute business logic, call APIs, update state, and control flow transitions.

**Structure:**
```python
from imports import *  # <AUTO GENERATED>

def function_name(conv: Conversation, flow: Flow):
    # Access entities
    entity_value = conv.entities.entity_name.value
    
    # Business logic
    result = perform_operation(entity_value)
    
    # Store state
    conv.state.result = result
    
    # Write metrics
    conv.write_metric("OPERATION_COMPLETED")
    
    # Log
    conv.log.info("Operation successful", result=result)
    
    # Control flow
    flow.goto_step('Next Step Name', 'Reason for transition')
    # OR
    conv.exit_flow()
    
    # Return message for LLM context
    return "Message describing what happened and what the LLM should tell the user"
```

**Key Patterns:**

1. **Access entities**: `conv.entities.entity_name.value`
   - Check existence: `if conv.entities.entity_name: ...`

2. **Store state**: `conv.state.variable_name = value`
   - Accessible in prompts as `$variable_name` or `{{vrbl:variable_name}}`

3. **Flow control**:
   - `flow.goto_step('Step Name', 'Reason')` — go to another step
   - `conv.exit_flow()` — exit the flow and return to general conversation

4. **Return value**: Optional string that gets fed back to the LLM as context
   - Describe what happened and what the agent should tell the user
   - Include key details the agent needs to communicate

5. **Error handling**:
   ```python
   try:
       result = api_call()
       if not result:
           flow.goto_step('error_step', 'API returned empty')
           return "API call failed..."
   except Exception as e:
       conv.log.error("Error details", error=e)
       flow.goto_step('error_step', 'Exception occurred')
       return "An error occurred..."
   ```

6. **Logging and metrics**:
   - `conv.log.info/warning/error("message", key=value, ...)` — structured logging
   - `conv.write_metric("METRIC_NAME", value)` — track business events

**Common Anti-Patterns to Avoid:**

❌ **Using `function_step_condition` in YAML** — Always use `step_condition` instead
❌ **Hardcoding IDs in YAML** — Use human-readable names; the platform handles ID mapping
❌ **Reading entities in default steps** — Entities are automatically available in prompts
❌ **Missing flow control** — Function steps must call `flow.goto_step()` or `conv.exit_flow()`
❌ **Not returning LLM context** — Return a string to guide the agent's response
❌ **Complex logic in prompts** — Move business logic to function steps

**Flow Design Principles:**

1. **Start simple**: Single path through the flow, then add branching
2. **Confirm before action**: Have a confirmation step before function steps that make changes
3. **Handle errors gracefully**: Add conditions/steps for failure cases
4. **Keep steps focused**: Each step should have one clear purpose
5. **Use meaningful names**: Step names should clearly describe what happens
6. **Test end-to-end**: Trace the full conversation flow from start to exit