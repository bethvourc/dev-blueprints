# System Prompt Engineering Guide

A framework for writing precise, effective system prompts—extracted from battle-tested patterns.

---

## The Architecture

Every strong system prompt has these layers:

```
┌─────────────────────────────────────┐
│         1. CORE IDENTITY            │  Who is this? What's the purpose?
├─────────────────────────────────────┤
│       2. GENERAL GUIDELINES         │  Universal behavioral rules
├─────────────────────────────────────┤
│    3. CONTENT-TYPE HANDLERS         │  Specific rules for specific inputs
├─────────────────────────────────────┤
│    4. RESPONSE QUALITY GATES        │  Meta-requirements across all outputs
└─────────────────────────────────────┘
```

---

## Layer 1: Core Identity

Define who the assistant is in 2-3 sentences. Answer:

- **What** is it?
- **What** is its sole purpose?
- **What qualities** define its responses?

### Template

```xml
<core_identity>
You are [name/role], whose sole purpose is to [primary function].
Your responses must be [quality 1], [quality 2], and [quality 3].
</core_identity>
```

### Example

```xml
<core_identity>
You are a technical writing assistant whose sole purpose is to transform rough notes into polished documentation.
Your responses must be clear, structured, and immediately publishable.
</core_identity>
```

### Principles

- **One purpose.** If you can't state it in one sentence, it's too broad.
- **Define the output qualities.** These become the criteria for every response.
- **No fluff.** "Helpful" and "friendly" are meaningless. Be specific.

---

## Layer 2: General Guidelines

Universal rules that apply to ALL responses. These are behavioral constraints.

### Template

```xml
<general_guidelines>

[NEVER statements - what the assistant must avoid]
[ALWAYS statements - what the assistant must do]
[Formatting standards - how to present output]
[Identity protection - how to respond when asked about itself]
[Ambiguity handling - what to do when intent is unclear]

</general_guidelines>
```

### The NEVER/ALWAYS Pattern

Be explicit. Be absolute. Ambiguity creates inconsistency.

```
NEVER [specific action].
NEVER [specific action].
ALWAYS [specific action].
ALWAYS [specific action].
```

### Example

```xml
<general_guidelines>

NEVER use meta-phrases (e.g., "I'd be happy to help", "Let me explain").
NEVER summarize unless explicitly requested.
NEVER provide unsolicited advice beyond the question asked.
ALWAYS use markdown formatting.
ALWAYS acknowledge uncertainty when present.
ALWAYS start with the direct answer before explanation.

If asked what model you are, respond: "[Your standard identity response]".

If user intent is unclear, do NOT guess. Acknowledge ambiguity explicitly.

</general_guidelines>
```

### Common Guidelines to Consider

| Category | Examples |
|----------|----------|
| **Tone** | Formal/casual, use of emojis, personality traits |
| **Verbosity** | Concise vs. thorough, when to elaborate |
| **Formatting** | Markdown, code blocks, LaTeX, lists vs. prose |
| **Boundaries** | What not to do, topics to avoid, scope limits |
| **Uncertainty** | How to express doubt, when to ask for clarification |
| **Identity** | How to respond to "who are you" questions |

---

## Layer 3: Content-Type Handlers

This is where specificity creates excellence.

**Identify every distinct type of input your assistant will receive.** For each type, define exactly how to respond.

### Template

```xml
<[content_type]>

[How to START the response]
[What to INCLUDE in the body]
[How to STRUCTURE the output]
[How to END or what final element to include]

</[content_type]>
```

### The "START WITH" Pattern

The most powerful pattern for consistent responses. Tell the model exactly how to begin.

```
START IMMEDIATELY WITH [the thing].
START with [the answer].
START with EXACTLY: "[literal text]"
```

This eliminates preamble and ensures consistency.

### The Conditional Pattern

Different situations require different behaviors:

```
If [condition], then [action].
If [condition] — even with [exception] — do NOT [action].
```

### The Threshold Pattern

For judgment calls, provide explicit thresholds:

```
If you are 90%+ confident, [action A].
If you are NOT 90%+ confident, [action B].
```

### Example: Technical Questions

```xml
<technical_questions>

START IMMEDIATELY WITH THE SOLUTION CODE.
Every line of code must have a comment on the following line.
After the solution, provide:
- Time/space complexity
- Key algorithm explanation
- Example walkthrough

</technical_questions>
```

### Example: Unclear Intent

```xml
<unclear_intent>

MUST START WITH EXACTLY: "I'm not sure what you're looking for."
Draw a horizontal line: ---
Follow with: "My guess is that you might want [specific guess]."
Keep the guess focused—one possibility, not a list.

Enter this mode when you are NOT 90%+ confident what the correct action is.

</unclear_intent>
```

### Example: Step-by-Step Instructions

```xml
<step_by_step_instructions>

Provide EXTREMELY detailed instructions with granular specificity.

For each step, specify:
- Exact button/menu names (use quotes: "File" → "Save As")
- Precise location ("top-right corner", "left sidebar")
- Visual identifiers (icons, colors, relative position)
- What happens after each action

Be comprehensive enough that someone unfamiliar could follow exactly.

</step_by_step_instructions>
```

### Content Types to Consider

Brainstorm all the distinct inputs your assistant will handle:

- Questions (factual, conceptual, comparative)
- Code (write, debug, review, explain)
- Writing (draft, edit, summarize, translate)
- Data (analyze, format, transform)
- Decisions (compare options, recommend)
- Errors/problems (diagnose, fix)
- Unclear/empty input

---

## Layer 4: Response Quality Gates

Meta-requirements that apply across all outputs. These are your final checks.

### Template

```xml
<response_quality_requirements>

[Thoroughness expectations]
[Actionability requirements]
[Formatting consistency]
[What to never do, even if tempted]

</response_quality_requirements>
```

### Example

```xml
<response_quality_requirements>

Be thorough and comprehensive in technical explanations.
Ensure all instructions are unambiguous and actionable.
Provide sufficient detail that responses are immediately useful.
Maintain consistent formatting throughout.
NEVER just summarize what was provided unless explicitly asked.

</response_quality_requirements>
```

---

## Writing Principles

### 1. Be Specific, Not Vague

| Vague | Specific |
|-------|----------|
| "Be helpful" | "Provide working code that can be copied directly" |
| "Be concise" | "Answer in 3 sentences or fewer unless asked to elaborate" |
| "Be professional" | "Use formal tone, no contractions, no emoji" |

### 2. Show, Don't Tell

Instead of describing what to do, show the exact format:

```
Format your response like this:

**Answer**: [direct answer]

**Why**: [one-sentence explanation]

**Example**: [concrete example]
```

### 3. Handle Edge Cases Explicitly

Don't leave gaps. For every "do X", consider:

- What if they ask for Y instead?
- What if the input is ambiguous?
- What if the input is empty?
- What if you can't do what they asked?

### 4. Use XML Tags for Structure

XML tags create clear boundaries that models respect:

```xml
<section_name>
Content for this section
</section_name>
```

This is clearer than markdown headers for system prompts.

### 5. Order Matters

Put the most important rules first. If there's a conflict, earlier rules take precedence.

---

## The Complete Template

```xml
<core_identity>
You are [role], whose sole purpose is to [primary function].
Your responses must be [quality 1], [quality 2], and [quality 3].
</core_identity>

<general_guidelines>

NEVER [constraint 1].
NEVER [constraint 2].
ALWAYS [requirement 1].
ALWAYS [requirement 2].
[Formatting standard].
[Identity response].
[Ambiguity handling].

</general_guidelines>

<[content_type_1]>

[START instruction]
[Body requirements]
[Structure/format]
[End requirement]

</[content_type_1]>

<[content_type_2]>

[START instruction]
[Body requirements]
[Structure/format]
[End requirement]

</[content_type_2]>

<unclear_or_ambiguous>

[Exactly what to do when intent is unclear]
[Threshold for triggering this mode]

</unclear_or_ambiguous>

<response_quality_requirements>

[Thoroughness]
[Actionability]
[Consistency]
[Final constraints]

</response_quality_requirements>
```

---

## Checklist Before Shipping

- [ ] Core identity is one clear sentence
- [ ] All NEVER/ALWAYS rules are explicit and unambiguous
- [ ] Every content type has a START instruction
- [ ] Unclear intent has explicit handling
- [ ] No vague words ("helpful", "appropriate", "good")
- [ ] Examples are provided where format matters
- [ ] Edge cases are addressed
- [ ] Formatting standards are specified
- [ ] Response quality gates are defined
