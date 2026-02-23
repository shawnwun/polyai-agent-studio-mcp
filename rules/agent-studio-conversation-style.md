---
description: Natural language and conversation style guidelines for Agent Studio prompts and topics
tags: [agent-studio, conversation, style, prompting, natural-language]
---

# Conversation Style & Natural Language

When writing prompts in the `content` field or `actions` field of topics, aim for natural, conversational agent behavior. The guidelines below help create agents that sound human and collaborative rather than robotic or overly formal.

## Brevity is the Soul of Wit

**Be concise and get to the point.** Users want minimal time on the phone, and brief utterances avoid "ad-copy speak":

✅ "If you want, I can sign you up for our rewards program so you can get a free appetizer with your next meal; would you like me to do that?"

❌ "Our Prime Rib Rewards Program lets you earn 10 cents in rewards for every dollar spent at any of our twelve locations! Plus, if you sign up today, you'll get a free delicious appetizer like our mouth-watering buffalo wings or crispy onion rings with your next meal. Would you like me to enroll you?"

**Exception: When explaining complex topics**, be more verbose to give users time to process:

✅ "California Alternate Rates for Energy, also known as CARE, is a discount program for lower-income California residents to help with monthly energy costs. You can get a discount of 20% or more on your electric bill if you meet the income requirements or are enrolled in certain public assistance programs."

## Natural Register

Avoid overly formal phrasings. Use contractions, informal language, and natural speech patterns:

❌ "Could you please **provide me with** your account number?"
✅ "Could you **tell me** your account number?"

❌ "How may I assist you today?"
✅ "How can I help?"

❌ "I apologize for the inconvenience."
✅ "Sorry about that."

❌ "Should I proceed with making that booking?"
✅ "Should I go ahead with that?"

## Avoid Repetitive Patterns

Don't overuse the `[declarative explanation] + [interrogative request]` structure:

❌ "In order to check for outages, I'll need to look up your account. Could you tell me your account number?"

✅ "No problem, what's your account number?"

❌ "To verify your identity, I'll need your birth date. Could you provide that?"

✅ "Great, and just to verify I have the right account, could you tell me your date of birth?"

**Vary your sentence structure** throughout the conversation.

## Social Presence Techniques

### Present Progressive for Active Collaboration

✅ "I'm not seeing any accounts under that phone number…"
⚠️ "I don't see any accounts under that phone number."

### Implicit Context References

Reference shared conversational context implicitly rather than restating everything:

✅ "How about Wednesday instead?"
❌ "How about Wednesday instead of Tuesday?"

✅ "In that case, how does Saturday at 2:30 sound?"
❌ "Since you said you prefer weekends, how does Saturday at 2:30 sound?"

### Varied Confirmationals

✅ "Great,…" "Okay,…" "Perfect,…" "Alright,…"
❌ "Great,…" "Great,…" "Great,…"

### Ethical Datives

✅ "Can you log into your account **for me**?"
✅ "Could you read **me** your account number?"
❌ "Could you read your account number aloud?"

### Face-Saving Past Tense

Use past tense when referencing potentially face-threatening requests:

✅ "When **were** you trying to come in?"
✅ "When **did** you want to come in?"
⚠️ "When are you trying to come in?"

## Don't Push the Conversation

### Step-by-Step Walkthroughs

Don't ask for confirmation after every step. Users will naturally confirm or ask follow-ups:

❌
"First, scroll down and click 'Account Settings'. **Let me know when you've done that.**"
"Then click 'Contact Details.' **Let me know when you're ready for the next step.**"

✅
"First scroll down and click 'Account Settings'"
"Then hit 'Contact Details'"
"Then just select the address you want to edit and input your new details!"

### Delayed "Anything Else"

Don't immediately ask "anything else?" after answering a question. Give users space to acknowledge or ask follow-ups:

❌ "Yes, we have large vehicle parking on Meridian street during weekdays. Is there anything else I can help you with?"

✅
"Yes, we have large vehicle parking on Meridian street during weekdays."
[User responds]
"No problem, is there anything else I can help you with?"
