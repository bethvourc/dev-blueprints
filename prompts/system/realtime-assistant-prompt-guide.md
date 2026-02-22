# Real-Time Contextual Assistant Prompt Guide

A framework for building prompts that make decisions in real-time based on live context—conversations, screens, streaming data.

---

## The Architecture

Real-time assistants are fundamentally different from request-response systems. They must:

1. **Observe** continuously (screen, audio, data streams)
2. **Detect** what type of moment this is
3. **Decide** what action to take (or not take)
4. **Respond** with the right format for this moment

```
┌─────────────────────────────────────┐
│         1. CORE IDENTITY            │  Who + primary goal
├─────────────────────────────────────┤
│      2. PRIORITY CASCADE            │  Ranked actions to check
├─────────────────────────────────────┤
│      3. DETECTION TRIGGERS          │  When each action activates
├─────────────────────────────────────┤
│     4. RESPONSE TEMPLATES           │  Format for each action type
├─────────────────────────────────────┤
│      5. INPUT INTERPRETATION        │  Handling messy real-world data
├─────────────────────────────────────┤
│       6. PASSIVE/FALLBACK           │  When to do nothing
├─────────────────────────────────────┤
│      7. CONTEXT OVERRIDE            │  User-provided info takes precedence
└─────────────────────────────────────┘
```

---

## Layer 1: Core Identity

Same as standard prompts, but emphasize the **real-time nature** and **primary goal**.

### Template

```xml
<core_identity>
You are [role], and you are the user's [relationship to user].
</core_identity>

Your goal is to help the user at the current moment in [context].
You can see [input sources: screen, audio, data, etc.].
Execute in the following priority order:
```

### Example

```xml
<core_identity>
You are the user's live-meeting co-pilot.
</core_identity>

Your goal is to help the user at the current moment in the conversation
(the end of the transcript). You can see the user's screen and the audio
history of the entire conversation.

Execute in the following priority order:
```

### Principles

- **"At the current moment"** — Emphasize recency. The end of the stream matters most.
- **List input sources explicitly** — What can the assistant see?
- **Signal the priority system** — "Execute in the following priority order" sets up the cascade.

---

## Layer 2: Priority Cascade

The core pattern. A ranked list of possible actions, checked in order.

### The Pattern

```xml
<priority_1_name>
  <primary_directive>
    [What to do + when this is the MOST IMPORTANT action]
  </primary_directive>

  <detection_triggers>
    [Conditions that activate this priority]
  </detection_triggers>

  <confidence_threshold>
    [X%+ confident → take this action]
  </confidence_threshold>

  <response_structure>
    [Exact format for this action type]
  </response_structure>

  <example>
    [Concrete example of trigger → response]
  </example>
</priority_1_name>

<priority_2_name>
  ...
</priority_2_name>
```

### Designing Your Priority Order

Ask: **What's the most valuable action at any given moment?**

Order by:
1. **Immediate value** — What helps the user right now?
2. **Time sensitivity** — What expires if not acted on?
3. **Specificity** — More specific actions before more general ones

### Example Priority Cascade

```
Priority 1: Answer direct questions (highest value, time-sensitive)
Priority 2: Define terms/context (helps comprehension)
Priority 3: Advance conversation (when no question, but opportunity)
Priority 4: Handle objections (context-specific situations)
Priority 5: Solve screen problems (visible issues)
Priority 6: Passive acknowledgment (fallback when nothing applies)
```

### Priority Cascade Template

```xml
<question_answering_priority>
  <primary_directive>
    If a question is presented to the user, answer it directly.
    This is the MOST IMPORTANT ACTION if there is a question at the end.
  </primary_directive>

  <confidence_threshold>
    If 50%+ confident someone is asking something, treat it as a question.
  </confidence_threshold>
</question_answering_priority>

<term_definition_priority>
  <definition_directive>
    Define any proper noun or term in the last 10-15 words of input.
    HIGH PRIORITY if a company name or technical term appears.
  </definition_directive>
</term_definition_priority>

<conversation_advancement_priority>
  <advancement_directive>
    When no direct question but action is needed—suggest follow-ups,
    provide things to say, help move forward.
  </advancement_directive>
</conversation_advancement_priority>

<passive_mode_priority>
  <passive_directive>
    Enter ONLY when ALL other priorities do not apply.
    Still show intelligence by referencing visible context.
  </passive_directive>
</passive_mode_priority>
```

---

## Layer 3: Detection Triggers

For each priority, define exactly **when it activates**.

### The "Recency Window" Pattern

Real-time systems care most about what just happened:

```xml
<detection_window>
  Focus on the last [N] words/seconds/items.
  Prioritize the END of the input stream.
</detection_window>
```

Example:
```
Define any term that appears in the final 10-15 words of the transcript.
```

### The "Intent Over Form" Pattern

Real-world input is messy. Detect intent, not perfect syntax:

```xml
<intent_detection_guidelines>
  Real [input type] has errors, unclear [elements], and incomplete [structures].
  Focus on INTENT rather than perfect [markers].

  Infer from context:
  - "[partial phrase]..." even if garbled
  - Incomplete [structures]: "[example]"
  - Implied [intent]: "[example signals]"
  - [Input] errors: "[example error]" → "[intended meaning]"
</intent_detection_guidelines>
```

Example:
```xml
<intent_detection_guidelines>
  Real transcripts have errors, unclear speech, and incomplete sentences.
  Focus on INTENT rather than perfect question markers:

  Infer from context: "what about..." "how did you..." even if garbled
  Incomplete questions: "so the performance..." "and scaling wise..."
  Implied questions: "I'm curious about X" "walk me through Z"
  Transcription errors: "what's your" → "what's you"
</intent_detection_guidelines>
```

### The "Trigger List" Pattern

Enumerate specific signals that activate an action:

```xml
<triggers>
  Any ONE of these is sufficient:
  - [trigger 1]
  - [trigger 2]
  - [trigger 3]
</triggers>

<exclusions>
  Do NOT activate for:
  - [exclusion 1]
  - [exclusion 2]
</exclusions>
```

---

## Layer 4: Confidence Thresholds

Different actions need different certainty levels.

### The Pattern

```xml
<confidence_threshold>
  If [X]%+ confident [condition], [action].
</confidence_threshold>
```

### Threshold Guidelines

| Threshold | Use Case |
|-----------|----------|
| **90%+** | High-stakes actions, irreversible decisions |
| **70%+** | Moderate confidence, can recover from errors |
| **50%+** | Bias toward action, low cost of false positive |

### Example Thresholds

```xml
<!-- Low threshold: bias toward helping -->
<question_answering>
  If 50%+ confident someone is asking something, treat it as a question.
</question_answering>

<!-- Medium threshold: some inference allowed -->
<speaker_inference>
  If not 70% confident, err toward the request being from the other person.
</speaker_inference>

<!-- High threshold: don't act unless certain -->
<passive_mode>
  Only enter when highly confident no action would be appropriate.
</passive_mode>
```

### The "Err Toward" Pattern

When uncertain, specify which direction to bias:

```
If not [X]% confident, err toward [safe default action].
```

---

## Layer 5: Response Templates

Each priority type gets its own response format.

### The Hierarchical Response Pattern

For information-dense responses, use a consistent hierarchy:

```xml
<response_structure>
  Short headline (≤6 words) — the actual answer
  Main points (1-2 bullets, ≤15 words each) — core details
  Sub-details — examples, metrics, specifics under each
  Extended explanation — additional context as needed
</response_structure>
```

### The "Action Type → Format" Mapping

```xml
<question_response_structure>
  Start with the direct answer, then supporting details:
  - Headline answer (≤6 words)
  - Main points (1-2 bullets)
  - Sub-details
  - Extended explanation
</question_response_structure>

<definition_response_structure>
  [Term] is [one-sentence definition].
  - Key fact 1
  - Key fact 2
  - Relevance to current context
</definition_response_structure>

<suggestion_response_structure>
  Follow-up questions to [goal]:
  - "[Question 1]"
  - "[Question 2]"
  - "[Question 3]"

  Never more than 3. One clear idea per bullet.
</suggestion_response_structure>

<objection_response_structure>
  **Objection: [Generic Name]**
  [Specific objection from conversation]

  Response: "[Tailored counter with specifics from conversation]"
</objection_response_structure>
```

### Word/Length Limits

Enforce constraints at each level:

```
Headline: ≤6 words
Main bullet: ≤15 words
Sub-bullet: ≤20 words
Total suggestions: ≤3 items
```

---

## Layer 6: Input Interpretation

Real-time data is messy. Build in error handling.

### The Speaker/Source Clarification Pattern

When input has multiple sources that might be confused:

```xml
<source_label_understanding>
  [Input type] uses specific labels:
  - "[label_1]": [who/what this represents]
  - "[label_2]": [who/what this represents]
  - "[label_3]": [who/what this represents]
</source_label_understanding>

<mislabeling_handling>
  [Input type] often mislabels [sources]. Use context clues:
  - Look at [what to examine]
  - [Rule for inference]
  - If not [X]% confident, err toward [safe assumption]
</mislabeling_handling>
```

Example:
```xml
<speaker_label_understanding>
  Transcripts use specific labels:
  - "me": The user you are helping (your primary focus)
  - "them": The other person in the conversation
  - "assistant": You (separate from above two)
</speaker_label_understanding>

<transcription_error_handling>
  Audio transcription often mislabels speakers. Use context clues:
  - Look at conversation flow and context
  - "Me:" will never be mislabeled as "Them:", only vice versa
  - If not 70% confident, err toward the request being from the other person
</transcription_error_handling>
```

### The "Messy Input" Pattern

Acknowledge that input will be imperfect:

```xml
<input_handling_constraints>
  [Input type] clarity: Real [input] is messy with [common issues].

  - Infer intent from [unclear patterns] when confident (≥[X]%)
  - Prioritize [what matters] even if imperfectly [captured]
  - Don't get stuck on perfect [accuracy] — focus on [intent]
</input_handling_constraints>
```

---

## Layer 7: Passive/Fallback Mode

What to do when **no action is appropriate**.

### The "All Conditions Must Be Met" Pattern

Define passive mode as the absence of all triggers:

```xml
<passive_mode_conditions>
  <when_to_enter>
    Enter passive mode ONLY when ALL of these are true:
    - No [priority 1 condition]
    - No [priority 2 condition]
    - No [priority 3 condition]
    - No [priority N condition]

    Only enter when highly confident no action would be appropriate.
  </when_to_enter>

  <passive_behavior>
    Still show intelligence by:
    - Acknowledging the current state: "[standard passive response]"
    - Referencing visible context ONLY if truly relevant
    - Never [unwanted behavior in passive mode]
  </passive_behavior>
</passive_mode_conditions>
```

Example:
```xml
<passive_mode_conditions>
  Enter ONLY when ALL conditions are met:
  - No clear question at the end of transcript
  - No term requiring definition in final 10-15 words
  - No visible problem on screen
  - No opportunity for follow-up questions
  - No objection requiring handling

  <passive_behavior>
    Still show intelligence by:
    - Saying "Not sure what you need help with right now"
    - Referencing visible screen elements ONLY if truly relevant
    - Never giving random summaries
  </passive_behavior>
</passive_mode_conditions>
```

---

## Layer 8: Context Override

User-provided context takes precedence over general knowledge.

### Template

```xml
<context_override>
  User-provided context (defer to this information over general knowledge).
  If there is specific script/desired responses, prioritize this over
  previous instructions.
</context_override>

[User context inserted here at runtime]
```

### Principles

- User knows their situation better than the model
- Allow customization without rewriting the whole prompt
- Create a clear insertion point for dynamic context

---

## Multimodal Integration

When the assistant sees multiple input types (screen + audio, video + text, etc.).

### The "Priority by Relevance" Pattern

```xml
<multimodal_integration>
  <input_sources>
    - [Source 1]: [what it shows]
    - [Source 2]: [what it shows]
  </input_sources>

  <priority_rules>
    Use [source] only if relevant to [other source].
    If [condition in source 1], prioritize [source 1 action].
    If [conflicting signals], prefer [which source] because [reason].
  </priority_rules>
</multimodal_integration>
```

Example:
```xml
<screen_usage_guidelines>
  Use the screen only if relevant for helping with the audio conversation.

  Example: If there is a leetcode problem on the screen and the conversation
  is small talk, DEFINITELY solve the leetcode problem. But if there is a
  specific question asked at the end, answer that using the screen as
  additional context.
</screen_usage_guidelines>
```

---

## Question Type Handlers

For assistants that handle many question types, create sub-handlers:

### Template

```xml
<question_type_handlers>
  <[question_type]_handling>
    <directive>
      [How to handle this type]
    </directive>

    <example>
      <input>[Example question]</input>
      <response>[Example response]</response>
    </example>
  </[question_type]_handling>
</question_type_handlers>
```

### Example Types

```xml
<creative_questions_handling>
  <directive>
    Complete answer + 1-2 rationale bullets explaining the choice.
  </directive>
</creative_questions_handling>

<behavioral_questions_handling>
  <directive>
    Use ONLY real user history/context. NEVER invent details.
    If no context, create generic examples with specific actions/outcomes.
    Focus on specific metrics.
  </directive>
</behavioral_questions_handling>

<technical_coding_handling>
  <directive>
    START with fully commented, line-by-line code.
    Then: complexity analysis, dry runs, algorithm explanation.
    NEVER skip detailed explanations.
  </directive>
</technical_coding_handling>

<business_finance_handling>
  <directive>
    Use established frameworks (profitability trees, market sizing).
    Include quantitative analysis with specific numbers.
    Spell out calculations. Provide clear recommendations.
  </directive>
</business_finance_handling>
```

---

## Operational Constraints

Guardrails that apply across all actions.

### Template

```xml
<operational_constraints>
  <content_constraints>
    - Never fabricate [what]
    - Use only [verified sources]
    - If unknown: [how to handle]
  </content_constraints>

  <input_handling_constraints>
    - [How to handle messy input]
    - [Confidence thresholds for inference]
  </input_handling_constraints>
</operational_constraints>

<forbidden_behaviors>
  <strict_prohibitions>
    - NEVER [prohibited action 1]
    - NEVER [prohibited action 2]
  </strict_prohibitions>
</forbidden_behaviors>
```

---

## Complete Template

```xml
<core_identity>
You are [role], and you are the user's [relationship].
</core_identity>

Your goal is to help the user at the current moment in [context].
You can see [input sources].
Execute in the following priority order:

<priority_1_name>
  <primary_directive>
    [What to do + why this is highest priority]
  </primary_directive>

  <detection_triggers>
    [When to activate]
  </detection_triggers>

  <confidence_threshold>
    If [X]%+ confident, [action].
  </confidence_threshold>

  <response_structure>
    [Format for this action]
  </response_structure>

  <example>
    <input>[trigger]</input>
    <response>[response]</response>
  </example>
</priority_1_name>

<priority_2_name>
  [Same structure...]
</priority_2_name>

<priority_N_name>
  [Same structure...]
</priority_N_name>

<passive_mode>
  <conditions>
    Enter ONLY when ALL priorities do not apply.
  </conditions>

  <behavior>
    [What to do/say in passive mode]
  </behavior>
</passive_mode>

<input_interpretation>
  <source_labels>
    [Define what each input source/label means]
  </source_labels>

  <error_handling>
    [How to handle messy/mislabeled input]
  </error_handling>

  <inference_rules>
    [When to infer, when to ask]
  </inference_rules>
</input_interpretation>

<response_format>
  [Universal formatting rules]
</response_format>

<question_type_handlers>
  [Specific formats for specific question types]
</question_type_handlers>

<operational_constraints>
  [Guardrails and prohibitions]
</operational_constraints>

<context_override>
  User-provided context (defer to this over general knowledge):
  [Dynamic insertion point]
</context_override>
```

---

## Checklist Before Shipping

- [ ] Core identity states the real-time relationship clearly
- [ ] Priority cascade is ordered by value/urgency
- [ ] Each priority has: directive, triggers, threshold, format, example
- [ ] Confidence thresholds are calibrated (lower = bias toward action)
- [ ] Passive mode has strict "ALL must be true" conditions
- [ ] Input interpretation handles messy real-world data
- [ ] Response formats have word/length limits
- [ ] Question type handlers cover expected variations
- [ ] Context override point is clearly defined
- [ ] Forbidden behaviors are explicitly listed
