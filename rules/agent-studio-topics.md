---
description: Writing knowledge base topics in Agent Studio - structure, content, actions, branching
tags: [agent-studio, topics, knowledge-base, yaml, local-development]
---

# Writing Topics in Agent Studio

## Topic Structure

Every YAML file has three fields:

```yaml
example_queries:
- User input example 1
- User input example 2
- ...

content: |-
  Factual information about this topic.
  What the agent should know to answer questions.

actions: |-
  Instructions for what to do when this topic is triggered.

  ## Conditional Branch 1
  If user wants X, call {{fn:function_name}} with appropriate arguments.

  ## Conditional Branch 2
  If user wants Y, guide them to do Z.
```

## Example Queries

**LIMIT to 10 queries** that cover **broad variations**:

```yaml
example_queries:
- pay by phone
- make a payment over the phone
- can I pay my bill now?
- phone payment
- I want to pay
- payment by phone
- how can I pay?
```

**DON'T** try to cover every tiny variation—use diverse phrasings.

## Content Field

Put **factual information** here (used for RAG):

```yaml
content: |-
  We offer quick and easy payment options online or by phone. You can also pay by mail or in person.
  To pay by phone there will be a transaction fee. You will be advised how much the fee is prior to approving the payment.
```

## Actions Field

Put **behavioral instructions** here including any function calls or variant attributes:

```yaml
actions: |-
  Inform the user about payment options and the transaction fee.

  ## User Wants to Continue Payment
  Call {{fn:make_payment}} to initiate the pay-by-phone process.

  ## User Declines
  Say "No problem. Let me know if you have any other questions."
```

> **NOTE**: **actions** is the _only_ KB topic field in which functions or `$variables` can be referenced and evaluated. ❌ Do not use these in the content or example question sections. Variant attributes _can_ be used in the content section.

## Branching Logic

Use markdown headers (`##`, `###`) for conditions:

```yaml
actions: |-
  Help the user check their balance.

  ## User Prefers Online
  Guide them to sign in at pge.com and navigate to View Current Bill.

  ## User Prefers Over the Phone
  Call {{fn:check_billing_balance}} to retrieve balance and inform user.
```

## Variant Attributes

Reference variant attributes with `{{attr:attribute_name}}`:

```yaml
actions: |-
  Direct user to call {{attr:support_phone_number}} for assistance.
```

## Best Practices

> **NOTE:** In both `content` and `actions` you should avoid prompting the model to repeat quoted content directly, as this can prevent the LLM from responding in the correct language for multilingual projects.

> ❌ DON'T include: "Say: 'Our premium perks are only available to diamond rewards members'"
> ✅ DO include: "Tell the user that our premium perks are only available to diamond rewards members"

## Anti-Pattern: Over-Complicated Actions

❌ **WRONG**:

```yaml
actions: |-
  First answer the user's question using the information provided by saying "Our diamond rewards program let's you earn 5 points for every dollar spent at one of our restaurants. Would you like me to send you a text with a link to learn more?" Then, if the user accepts the text message, call {{fn:send_sms}} with the string 'diamond_rewards' as the sms_id argument. Otherwise call the {{fn:sms_declined}} function
```

✅ **RIGHT**:

```yaml
actions: |-
  ## Primary Response
  Answer the user's query and offer a text message with a link to more information

  ### SMS accepted
  Call `{{fn:send_sms}}('diamond_rewards')`

  ### SMS declined
  Call `{{fn:sms_declined}}`
```
