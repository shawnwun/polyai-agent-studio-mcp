---
description: Agent Studio entities configuration, purpose, patterns
tags: [agent-studio, entities, low-code, no-code, low-code-flows, local-development, prompting]
---

# Agent Studio Entities

Entities are defined in `config/entities.yaml` and represent structured pieces of information the agent collects during conversations. Entities provide validation, formatting, and type-specific handling.

Entities are used for low-code flows, but not for standard flows. 

## Entity Structure

```yaml
entities:
  - name: entity_name
    description: Clear description of what this entity represents
    entity_type: type_name
    config:
      # Type-specific configuration fields
```

- **`name`**: Unique identifier (snake_case, used in code and prompts)
- **`description`**: Instructions for the LLM on what to collect and how to format it
- **`entity_type`**: The type of entity (see below for all types)
- **`config`**: Type-specific configuration options

## Available Entity Types

**1. `numeric` — Numbers (integers or decimals)**

Collects numeric values with optional range validation.

```yaml
- name: loan_amount
  description: The amount the customer wishes to borrow, in GBP.
  entity_type: numeric
  config:
    has_decimal: true          # Allow decimal values (false for integers only)
    has_range: true            # Enable min/max validation
    min: 1000                  # Minimum value (optional)
    max: 50000                 # Maximum value (optional)
```

**Use for:** Quantities, amounts, counts, measurements, percentages

**2. `free_text` — Unstructured text**

Collects open-ended text with no validation.

```yaml
- name: special_requirements
  description: Any special requirements for the booking.
  entity_type: free_text
  config: {}
```

**Use for:** Comments, notes, descriptions, reasons, feedback

**3. `enum` — Predefined options**

Collects a selection from a fixed list of options.

```yaml
- name: employment_status
  description: The customer's current employment status.
  entity_type: enum
  config:
    options:
      - employed full-time
      - employed part-time
      - self-employed
      - retired
      - unemployed
      - student
```

**Use for:** Categories, statuses, choices, types, selections

**4. `date` — Calendar dates**

Collects dates with optional relative date support.

```yaml
- name: date_of_birth
  description: "The customer's date of birth. Format: DD-MM-YYYY"
  entity_type: date
  config:
    relative_date: false       # If true, accepts "tomorrow", "next Monday", etc.
```

**Use for:** Birthdates, appointment dates, deadlines, start/end dates

**5. `time` — Time of day**

Collects time values with optional time range restrictions.

```yaml
- name: pickup_time
  description: 'The time the user wants to be picked up at. Format: HH:MM'
  entity_type: time
  config:
    enabled: false             # Enable time range validation
    start_time: '09:00'        # Earliest allowed time (optional)
    end_time: '17:00'          # Latest allowed time (optional)
```

**Use for:** Appointment times, meeting times, operating hours

**6. `phone_number` — Phone numbers**

Collects phone numbers with country code validation.

```yaml
- name: booking_phone_number
  description: The phone number used to make the booking.
  entity_type: phone_number
  config:
    enabled: true              # Enable country code validation
    country_codes:             # Allowed country codes (optional)
      - GB
      - US
```

**Use for:** Contact numbers, callback numbers, verification numbers

**7. `address` — Physical addresses**

Collects structured address information.

```yaml
- name: delivery_address
  description: The address for delivery.
  entity_type: address
  config: {}
```

**Use for:** Mailing addresses, delivery locations, billing addresses

**8. `name_config` — Personal names**

Collects full names (first and last).

```yaml
- name: full_name
  description: The customer's full name.
  entity_type: name_config
  config: {}
```

**Use for:** Customer names, cardholder names, contact names

**9. `alphanumeric` — Text with validation**

Collects text with optional regex validation.

```yaml
- name: email
  description: Email address validation
  entity_type: alphanumeric
  config:
    enabled: true                    # Enable regex validation
    validation_type: email           # Label for validation type (optional)
    regular_expression: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
```

**Use for:** Email addresses, postal codes, reference numbers, IDs, codes

## Using Entities in Flows

**In step definitions:**

```yaml
# Declare which entities to extract in this step
extracted_entities:
  - entity_name
  - another_entity

# Require entities before triggering a condition
conditions:
  - name: Ready to Proceed
    condition_type: step_condition
    child_step: Next Step
    required_entities:
      - entity_name
      - another_entity
```

**In prompts:**

```yaml
prompt: |-
  Reference entity values: {{entity:entity_name}}
  
  Ask the user to provide their {{entity:entity_name}}.
  Save as {{entity:entity_name}}.
```

**In function steps:**

```python
def my_function(conv: Conversation, flow: Flow):
    # Access entity values
    value = conv.entities.entity_name.value
    
    # Check if entity exists
    if conv.entities.optional_entity:
        optional_value = conv.entities.optional_entity.value
```

## Entity Design Best Practices

- **Descriptive names**: Use clear, specific names (e.g., `loan_amount` not `amount`)
- **Clear descriptions**: The LLM uses this to understand what to collect and how to format it
- **Appropriate types**: Choose the type that provides the right validation
- **Validation where needed**: Use ranges, regex, or enums to ensure data quality
- **Format guidance**: Include format examples in the description (e.g., "Format: DD-MM-YYYY")
- **Reusable entities**: Define entities that can be used across multiple flows
- **Avoid over-validation**: Don't make validation so strict that legitimate inputs are rejected
