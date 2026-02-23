---
description: Agent Studio flow structure, step prompts, navigation, and patterns
tags: [agent-studio, flows, local-development, prompting]
---

# Agent Studio Flows

## Intro to Flows

Flows are used for choreographing complex, multi-step processes in a reliable step-by-step way. A project may require a user to traverse multiple flows in order to accomplish a particular task or intent.

When navigating a flow, the LLM only sees the prompting and tools for the particular step it is on (alongside any other global functions and prompting that are exposed in agent rules). It is always best where possible to maintain a one-task-to-one-step mapping and to implement branching and conditional logic via transitions to additional steps.

## Entering a Flow

Flows are entered via function calls either with a `conv.goto_flow('Flow Name')` call (in which case we will enter the flow at the preconfigured "Start Step") or via an explicit transition in a return dict:

```python
return {
    "transition": {
        "goto_flow": "Flow Name",
        "goto_step": "Step Name"  # or Start Step if none specified
    }
}
```

Within a flow, steps are transitioned to via `flow.goto_step("Step Name")` calls within flow functions. Step transitions cannot be made this way from global functions because they do not take the `flow` argument.

## Flow File Structure

The general file structure of a flow:

```
flows/{flow_name_cleaned}/
├── {Flow name}.yaml
├── steps/
│   └── {step_name_cleaned}.yaml
└── functions/
    └── {function_name}.py
```

For a name to be "cleaned" it is lowercase and using snake case (i.e. flow name `"Pickup Status"` is `pickup_status.yaml`)

## Flow Configs

Flow configs are the main header of each flow:

```yaml
name: Pickup Status
description: 'Description'
start_step: Collect Pickup Confirmation Number And Confirm
```

Validation:

- Description exists (cannot be empty)
- start_step is name of a real step

## Flow Steps

### Advanced Flow Step

This is a flow step that allows function calling directly. ASR and DTMF config is here. To turn on, enable `is_enabled` for each.

Step type has to be `advanced_step`.

```yaml
step_type: advanced_step
name: New step
asr_biasing:
  is_enabled: false
  alphanumeric: false
  name_spelling: false
  numeric: false
  party_size: false
  precise_date: false
  relative_date: false
  single_number: false
  time: false
  yes_no: false
  address: false
  custom_keywords: []
dtmf_config:
  is_enabled: true
  inter_digit_timeout: 0
  max_digits: 1
  end_key: '#'
  collect_while_agent_speaking: false
  is_pii: false
prompt: Call this function {{ft:flow_function}} this is new content
```

> **NOTE**: When referencing/evaluating state variables in prompts or KB actions, use `$variable` notation, not the full `conv.state.variable` name

> **IMPORTANT**: Our prompt templating does **not** support attribute access like `$variable.attribute`. If you need to show structured state in a prompt, you must stringify it in Python first (e.g. set `conv.state.selected_appointment_details = "..."`) and reference the string variable (e.g. `$selected_appointment_details`).

> **IMPORTANT**: Do not expose internal routing state (like `$user_intent`) in prompts and ask the model to branch on it. Route deterministically in Python (e.g. `if/else` on `conv.state.user_intent`) and transition to a dedicated step whose prompt only depends on user input.

## ⚠️ Critical: Avoid Deterministic Logic in Step Prompts

**DO NOT** put programmatic/deterministic logic in step prompts. Value comparisons, variable evaluations, and conditional routing should be handled in Python functions that transition directly to the appropriate step.

❌ **BAD** - Deterministic logic in prompt:

```yaml
prompt: |-
  If $num_appts == 0: Go to Offer Make Appointment
  If $num_appts == 1: Go to Recite Details
  If $num_appts > 1: Ask which appointment
  Call {{ft:route_by_intent}}
```

✅ **GOOD** - Logic in Python, called directly from previous function:

```python
def load_appointments(conv: Conversation):
    # ... load appointments ...
    num_appts = conv.state.num_appts

    # Route programmatically
    if num_appts == 0:
        return transition(flow="appointments", step="Offer Make Appointment")
    elif num_appts == 1:
        return transition(flow="appointments", step="Recite Details")
    else:
        return transition(flow="appointments", step="Ask Which")
```

**When to use prompts vs. Python routing:**
- **Prompts**: Collecting user input, presenting information, handling conversational flow
- **Python**: Value comparisons (==, >, <), boolean checks (if/else), routing based on state variables

## Example Step Prompts

### Complex Multi-Value Collection

```
## Collect Account Details
$spanish_prompt
Collect either the user's phone number, account number, or meter number to look up their account. Do not infer or assume that the user is unwilling or unable to provide a phone number based on earlier responses to unrelated questions.
Even if the user said "I don't have a phone number" earlier in the call, you must ask them explicitly for their phone number. *Always* begin authentication with Option A, phone number.

### Option A: Collect Phone

1. Ask the user for the phone number on their account.

#### Valid US phone number collected

**NOTE** You should try to store any valid phone number the user provides

Call {{ft:number_provided}}(number=phone number stripped of any spaces or punctuation, number_type='phone')

#### Invalid US phone number collected or Nothing Collected

E.g. number contains a digit or is not 10 digits long

Tell the user you didn't quite catch that and ask them for the number again

### Option B: User Can't Provide Phone Number
e.g. "I don't know it", "I can't remember", or user otherwise expresses uncertainty or unwillingness to provide.

Say nothing and call {{ft:user_cant_provide_phone_number}} for further instructions of other ways to authenticate
```

### Simple Step Prompt

```
## Ask Enroll AMP
Ask the user if they'd like to be enrolled in AMP.

### If the caller says they'd like to enroll
call {{ft:enroll_amp}}

### If the caller doesn't want to enroll
call {{ft:skip_enroll_amp}}
```

## Best Practices

### Avoid Separate "Anything Else" Steps

When a flow completes and you want to ask if there's anything else you can help with, **don't create a separate step for this**. Instead, exit the flow and return prompting content directly from the function.

❌ **BAD** - Creating a separate step:

```python
def user_done(conv: Conversation, flow: Flow):
    flow.goto_step("Anything Else")
    return "Ask if there's anything else."
```

✅ **GOOD** - Exit flow with prompting:

```python
def user_done(conv: Conversation, flow: Flow):
    conv.exit_flow()
    return "Ask if there's anything else you can help with."
```

### Store Hard-Coded Utterances in utterances.py

When a flow needs a specific greeting or hard-coded message, **don't create a separate function just to return it**. Instead, add the utterance to `utterances.py` and return it directly from the calling function (e.g., `start_function`).

❌ **BAD** - Creating a function just to return a greeting:

```python
# flows/my_flow/functions/my_greeting.py
def my_greeting(conv: Conversation, flow: Flow):
    return {
        "utterance": "Hi, welcome to our service!",
        "content": "Ask what the user needs."
    }
```

✅ **GOOD** - Store in utterances.py and use directly:

```python
# In utterances.py
MY_GREETING = {
    "en-US": "Hi, welcome to our service!",
    "es-US": "Hola, bienvenido a nuestro servicio!",
}

# In start_function.py
if conv.state.line == 'my_line':
    return {
        "transition": {
            "goto_flow": "my_flow",
            "goto_step": "Ask Intent"
        },
        "utterance": Utterances.MY_GREETING(conv),
        "content": "Ask what the user needs.",
        "end_turn": False
    }
```

This approach:
- Keeps utterances centralized and translatable
- Reduces the number of function files
- Makes the flow entry cleaner

### Avoid Unnecessary `end_turn=False` Usage

The `end_turn=False` pattern is for **rare cases** where you need to couple a hard-coded utterance with an immediate agent-initiated function call or branching decision on the same turn. Don't use it just to combine an utterance with a question.

❌ **BAD** - Using end_turn=False to ask a question:

```python
return {
    "transition": {
        "goto_flow": "my_flow",
        "goto_step": "Ask Intent"
    },
    "utterance": "Hi, welcome to our service!",
    "content": "Ask what the user needs.",
    "end_turn": False
}
```

✅ **GOOD** - Include the question in the utterance itself:

```python
# In utterances.py
MY_GREETING = {
    "en-US": "Hi, welcome to our service! What can I help you with today?",
    "es-US": "Hola, bienvenido a nuestro servicio! ¿En qué puedo ayudarle hoy?",
}

# In code
return {
    "transition": {
        "goto_flow": "my_flow",
        "goto_step": "Ask Intent"
    },
    "utterance": Utterances.MY_GREETING(conv)
}
```

✅ **GOOD USE of end_turn=False** - Agent needs to immediately call a function after speaking:

```python
return {
    "utterance": f"Your balance is {conv.state.balance}.",
    "content": "Immediately call the balance_informed function to proceed.",
    "end_turn": False
}
```

**When to use end_turn=False:**
- Agent must call a function immediately after speaking (without user input)
- Agent needs to make a branching decision immediately after delivering information

**When NOT to use end_turn=False:**
- You're asking the user a question (they need to respond)
- You're transitioning to a step that will collect user input
