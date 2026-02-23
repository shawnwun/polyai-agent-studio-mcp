---
description: Best practices for hard-coded utterances in Agent Studio - slot filling, chronology, bilingual support
tags: [agent-studio, utterances, hard-coded, multilingual, tts, local-development]
---

# Hard-Coded Utterances in Agent Studio

## Overview

Hard-coded utterances provide consistent, deterministic phrasing for important parts of the conversation. They're typically stored in a central `functions/utterances.py` file and used throughout flows to ensure exact wording.

**Benefits:**
- ✅ Consistent phrasing across all calls
- ✅ Reliable TTS pronunciation
- ✅ Easy to update wording in one place
- ✅ Multilingual support with guaranteed translations
- ✅ Better quality assurance and testing

**When to Use Hard-Coded Utterances:**
- Critical business information (confirmation numbers, amounts, dates/times)
- Compliance-required language
- Complex formatted information (appointment details, payment schedules)
- Multi-step confirmation flows
- Any utterance that must be exactly right

**When to Use LLM-Generated Utterances:**
- Simple acknowledgments and transitions
- Error handling and clarification
- Follow-up questions with variable context
- Natural conversational flow between hard-coded sections

## Utterance File Structure

### Creating the Utterances Class

**File**: `functions/utterances.py`

```python
from imports import *  # <AUTO GENERATED>
import re


@func_description('Multilingual utterance storage')
@func_parameter('utterance', 'the name of the utterance being retrieved')
@func_parameter('tts_format', 'format dates, times, currency amounts for TTS')
@func_parameter('voice_speed', 'allows for voice speed to be changed')
def utterances(conv: Conversation, utterance: str, tts_format: bool, voice_speed: float):
    """Global access point. Set tts_format=True to apply TTS-friendly formatting."""
    def error(x):
        return "ERROR"
    enum_member = getattr(Utterances, utterance.upper().replace(" ", "_"), error)
    if enum_member is not error:
        return enum_member(
            conv, tts_format=tts_format or False, voice_speed=voice_speed
        )
    return ""


class Utterances:
    """
    Hard-coded utterances for the conversational AI.
    Each utterance must have both 'EN' and 'ES' variants (or whatever languages you support).

    To add a new utterance, follow the existing pattern:
    - Keys must be language codes ('en-US', 'es-US', etc.)
    - Use {placeholders} for dynamic content
    """

    # Payment confirmation
    PAYMENT_CONFIRMED = {
        "en-US": "Your payment of ${amount} has been processed. Your confirmation number is {confirmation_number}. Would you like me to repeat that?",
        "es-US": "Su pago de ${amount} ha sido procesado. Su número de confirmación es {confirmation_number}. ¿Le gustaría que se lo repita?",
    }

    # Appointment scheduling
    APPOINTMENT_SCHEDULED = {
        "en-US": "Great, your {service_type} appointment is confirmed for {weekday}, {date}, between {start_time} and {end_time}.",
        "es-US": "Perfecto, su cita para {service_type} está confirmada para el {weekday}, {date}, entre las {start_time} y las {end_time}.",
    }

    # Implementation of __call__ method for slot filling
    def __call__(self, conv, tts_format: bool = False, voice_speed: float = None):
        """
        When you do Utterances.X(conv), this looks up conv.language,
        falls back to the 2-letter code, then to en-US, then to any
        available string. Also formats slots using {} defaulting to conv.state.var_name
        """
        _SLOT_RE = re.compile(r"\{(\w+)\}")

        # 1) Get language-specific utterance
        mapping = (
            self.value.get(conv.language)
            or self.value.get(conv.language.split("-", 1)[0])
            or self.value.get("en-US")
            or next(iter(self.value.values()), "")
        )

        # 2) Replace each {slot} with getattr(conv.state, slot, "{slot}")
        def _replace(match):
            slot = match.group(1)
            val = getattr(conv.state, slot, match.group(0))
            return str(val)

        text = _SLOT_RE.sub(_replace, mapping)

        # 3) Set voice speed if specified
        if voice_speed is not None:
            from functions.voice_utils import set_slow_voice
            set_slow_voice(conv, voice_speed)

        # 4) Optional TTS-friendly formatting
        if tts_format:
            from functions.formatters import tts_postprocess
            text = tts_postprocess(text, conv)

        return text
```

## Critical: Slot Filling from conv.state

**🚨 IMPORTANT: Utterance placeholders are filled from `conv.state`, NOT from function parameters.**

### ❌ WRONG - Passing parameters to utterance

```python
# This does NOT work - parameters are ignored for slot filling
conv.state.count = 3
utterance = Utterances.APPOINTMENT_LIST(conv, count=3)  # ❌ count parameter ignored
```

### ✅ CORRECT - Set state variables first

```python
# Set state variables BEFORE calling utterance
conv.state.count = 3
conv.state.appointments_list = "a furnace check, a water heater relight, and a range safety check"
utterance = Utterances.APPOINTMENT_LIST(conv)  # ✅ Fills from conv.state
```

### Utterance Definition with Slots

```python
class Utterances:
    APPOINTMENT_LIST = {
        "en-US": "I see you have {count} appointments: {appointments_list}. Which one are you calling about?",
        "es-US": "Veo que tiene {count} citas: {appointments_list}. ¿Sobre cuál está llamando?",
    }
```

**The `{count}` and `{appointments_list}` slots are automatically filled from:**
- `conv.state.count`
- `conv.state.appointments_list`

### Setting Required State Variables

Always set ALL required state variables before calling an utterance:

```python
def review_appointment(conv: Conversation, flow: Flow):
    # Set ALL state variables needed by the utterance
    conv.state.service_type = "range safety check"
    conv.state.weekday = "Monday"
    conv.state.date = "December 26, 2025"
    conv.state.start_time = "8 AM"
    conv.state.end_time = "12 PM"

    # Now the utterance can fill all slots
    flow.goto_step("Confirm Appointment")
    conv.say(Utterances.APPOINTMENT_SCHEDULED(conv))
    return
```

## Critical: Utterance Chronology

**🚨 IMPORTANT: Utterances must be spoken BEFORE transitioning to the step where they're relevant, not DURING that step.**

### ❌ WRONG - Utterance in the target step

```python
# In confirm_appointment_details.py (called ON the "Confirm Details" step)
def confirm_appointment_details(conv: Conversation, flow: Flow):
    # ❌ TOO LATE - we're already AT this step
    conv.say(Utterances.APPOINTMENT_CONFIRM_DETAILS(conv))
    # User hears nothing because step prompt executes after function
```

### ✅ CORRECT - Utterance BEFORE transition

```python
# In notification_preference.py (called BEFORE transitioning)
def notification_preference(conv: Conversation, flow: Flow, wants_notifications: bool):
    if not wants_notifications:
        # Set state for utterance
        conv.state.service_type = conv.state.target_appointment_type_description
        conv.state.offer_window_text = conv.state.selected_window_text

        # Speak utterance BEFORE transitioning
        flow.goto_step("Confirm Appointment Details")
        conv.say(Utterances.APPOINTMENT_CONFIRM_DETAILS(conv))
        return
```

### The Step Prompt

```yaml
# flows/appointments/steps/confirm_appointment_details.yaml
prompt: |-
  # Confirm Appointment Details

  The appointment details have already been confirmed to the user using a hard-coded utterance.

  Wait for the user to confirm or decline the appointment.

  ## User Confirms
  Call {{ft:create_appointment}}

  ## User Declines
  Ask if there's anything else you can help with.
```

**Note:** The step prompt indicates the utterance has "already been" spoken, because it was spoken en route to this step.

## Using conv.say() Correctly

### ❌ WRONG - Returning conv.say() result

```python
def my_function(conv: Conversation, flow: Flow):
    flow.goto_step("Next Step")
    return conv.say(Utterances.MY_UTTERANCE(conv))  # ❌ Don't return the result
```

### ✅ CORRECT - Call conv.say(), then return separately

```python
def my_function(conv: Conversation, flow: Flow):
    flow.goto_step("Next Step")
    conv.say(Utterances.MY_UTTERANCE(conv))  # ✅ Call it
    return  # ✅ Return separately
```

**Reason:** The platform doesn't know how to handle the return value of `conv.say()`. Call it for its side effects, then return.

## Multilingual Support

### Always Provide All Languages

Every utterance MUST have all supported languages:

```python
class Utterances:
    # ✅ GOOD - Both languages provided
    GREETING = {
        "en-US": "Hello, how can I help you today?",
        "es-US": "Hola, ¿cómo le puedo ayudar hoy?",
    }

    # ❌ BAD - Missing Spanish
    GOODBYE = {
        "en-US": "Thank you for calling. Goodbye!",
    }
```

### Language-Specific Formatting

Account for grammatical differences between languages:

```python
class Utterances:
    APPOINTMENT_DETAILS = {
        # English: "on Monday, December 26"
        "en-US": "{service_type} on {weekday}, {date}",
        # Spanish: "el lunes, 26 de diciembre" (different word order)
        "es-US": "{service_type} el {weekday}, {date}",
    }
```

## Complex Utterances and Helper Functions

### When Utterances Need Pre-Formatting

For complex utterances with multiple pieces of formatted data, create helper functions:

```python
# functions/appointment_formatters.py

def set_appointment_state_for_utterance(conv: Conversation, appointment: dict) -> dict:
    """
    Format an appointment and set all required state variables for utterances.
    This centralizes the logic and prevents duplication.
    """
    appt_parts = format_existing_appointment(appointment, conv.language)

    # Set all state variables at once
    conv.state.selected_appointment_details = appt_parts["full_details"]
    conv.state.service_type = appt_parts["service_type"]
    conv.state.weekday = appt_parts["weekday"]
    conv.state.date = appt_parts["date"]
    conv.state.start_time = appt_parts["time"]
    conv.state.end_time = appt_parts["end_time"]

    return appt_parts


# Then use in functions:
def review_appointment(conv: Conversation, flow: Flow):
    appointment = conv.state.selected_appointment

    # One call sets everything
    appt_parts = set_appointment_state_for_utterance(conv, appointment)

    # Now use appropriate utterance
    if appt_parts["end_time"]:
        utterance = Utterances.REVIEW_APPOINTMENT_WITH_END_TIME(conv)
    else:
        utterance = Utterances.REVIEW_APPOINTMENT_NO_END_TIME(conv)

    flow.goto_step("Confirm Action")
    conv.say(utterance)
    return
```

### Formatting Lists for TTS

When building lists of items for natural speech:

```python
def format_appointments_list_for_tts(appointments: list, language: str = "en-US") -> str:
    """
    Format a list of appointments for natural TTS reading.

    Example output:
    "a furnace inspection on December 26th, a water heater relight on December 28th,
     and a range safety check on December 31st"
    """
    is_spanish = language.lower().startswith("es")

    formatted_list = []
    for appt in appointments[:5]:  # Max 5
        service_type = appt.get('read_text', 'appointment')
        weekday = appt.get('weekday', '')
        date = appt.get('date_formatted', '')

        if is_spanish:
            formatted_list.append(f"{service_type} el {weekday}, {date}")
        else:
            article = "an" if service_type[0].lower() in 'aeiou' else "a"
            formatted_list.append(f"{article} {service_type} on {weekday}, {date}")

    # Join with commas and "and" before last item
    if len(formatted_list) == 1:
        return formatted_list[0]
    elif len(formatted_list) == 2:
        conjunction = "y" if is_spanish else "and"
        return f"{formatted_list[0]} {conjunction} {formatted_list[1]}"
    else:
        conjunction = "y" if is_spanish else "and"
        return f"{', '.join(formatted_list[:-1])}, {conjunction} {formatted_list[-1]}"


# Usage:
conv.state.count = len(appointments)
conv.state.appointments_list = format_appointments_list_for_tts(appointments, conv.language)
conv.say(Utterances.LIST_APPOINTMENTS(conv))
```

## Combining Utterances

### Concatenating Multiple Utterances

Sometimes you need to chain utterances together:

```python
def store_dog_answer(conv: Conversation, flow: Flow, has_dog: bool):
    conv.state.has_dog = has_dog

    if has_dog:
        # Provide safety message, then ask next question
        utterance = Utterances.DOG_SAFETY_MESSAGE(conv) + " " + Utterances.ASK_ABOUT_GATES(conv)
        flow.goto_step("Ask Access Questions")
        conv.say(utterance)
        return
    else:
        # No dog, just ask next question
        flow.goto_step("Ask Access Questions")
        conv.say(Utterances.ASK_ABOUT_GATES(conv))
        return
```

## Common Patterns

### Confirmation Flow Pattern

```python
# Step 1: Offer confirmation options upfront
class Utterances:
    APPOINTMENT_CONFIRMED = {
        "en-US": "Great, your {service_type} appointment is confirmed for {date} between {start_time} and {end_time}. Would you like me to text you your confirmation number or would you prefer I read it to you now?",
        "es-US": "Perfecto, su cita para {service_type} está confirmada para el {date} entre las {start_time} y las {end_time}. ¿Le gustaría que le envíe su número de confirmación por mensaje de texto o prefiere que se lo lea ahora?",
    }

# Step 2: Read confirmation if requested
class Utterances:
    CONFIRMATION_NUMBER_READ = {
        "en-US": "Your confirmation number is {confirmation_number}. Would you like me to repeat that?",
        "es-US": "Su número de confirmación es {confirmation_number}. ¿Le gustaría que se lo repita?",
    }
```

### Conditional Utterances

```python
def present_appointment_details(conv: Conversation, flow: Flow):
    # Set common state
    conv.state.service_type = "range safety check"
    conv.state.weekday = "Monday"
    conv.state.date = "December 26"
    conv.state.start_time = "8 AM"

    # Choose utterance based on whether we have end time
    if has_end_time:
        conv.state.end_time = "12 PM"
        utterance = Utterances.APPOINTMENT_WITH_TIME_WINDOW(conv)
    else:
        utterance = Utterances.APPOINTMENT_WITH_START_TIME_ONLY(conv)

    flow.goto_step("Confirm Booking")
    conv.say(utterance)
    return
```

## Testing and Debugging

### Using get_call_diagnostics.py

After making changes to utterances, test with real calls:

```bash
python scripts/get_call_diagnostics.py <call_id>
```

Look for:
- ✅ Utterances spoken at the right time
- ✅ All slots filled correctly
- ✅ Correct language used
- ✅ Natural pronunciation
- ❌ Any missing or duplicate utterances
- ❌ Slots showing as "{slot_name}" (unfilled)
- ❌ Utterances in wrong order

### Common Issues

**Slots not filled:**
```
"Your appointment is for {service_type}"  # ❌ service_type not set
```
→ Check that `conv.state.service_type` was set before calling utterance

**Utterance spoken too late:**
```
User arrives at step, but hasn't heard the question yet
```
→ Move utterance to the function that transitions TO this step

**Wrong language:**
```
Spanish caller hears English utterance
```
→ Check that utterance has "es-US" key defined

## Quick Reference

| Task | Pattern |
|------|---------|
| Define utterance | `MY_UTTERANCE = {"en-US": "text", "es-US": "texto"}` |
| Set state for slots | `conv.state.slot_name = value` |
| Call utterance | `conv.say(Utterances.MY_UTTERANCE(conv))` |
| Speak before transition | `flow.goto_step("Next"); conv.say(...); return` |
| Conditional utterance | Choose utterance based on state, then call |
| Format complex data | Create helper function, set state, then call |
| Concatenate utterances | `utterance1 + " " + utterance2` |
| Test | Use `get_call_diagnostics.py <call_id>` |

## Best Practices

✅ **DO:**
- Define both EN and ES (or all supported languages)
- Set all required state variables before calling utterance
- Speak utterances BEFORE transitioning to their target step
- Create helper functions for complex formatting
- Use descriptive slot names that match state variable names
- Test utterances with real calls
- Call `conv.say()` then `return` separately

❌ **DON'T:**
- Pass parameters to utterances (they're ignored)
- Call utterances from within the target step
- Return the result of `conv.say()`
- Leave slots unfilled (set defaults if needed)
- Forget to handle both languages
- Mix LLM and hard-coded utterances in critical sections
