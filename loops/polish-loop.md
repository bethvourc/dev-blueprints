# Polish Loop — design audit-and-fix until the bar is met

**Use when:** the product works but doesn't yet *feel* right. This loop runs the
design review from `prompts/design/design-review-prompt.md` (with
`prompts/design/steve-jobs-design.md` as the taste standard) in a cycle:
see → judge → fix → see again.

**Runner:** `/goal`. Web projects only in this form — it depends on Playwright
capture. The maker/checker split here is *literal*: the checker reviews
screenshots, never code. If it can't be seen in the image, it isn't a polish
finding.

## Setup

`implementation/POLISH_LOG.md` listing the routes/states in scope. Polish without
a route list becomes an open loop that redesigns your product — fence it first:

```markdown
# Polish Log
Scope: /dashboard, /settings, /onboarding (desktop, tablet, mobile)
States: default, loading, empty, error, hover, focus, disabled
Out of scope: anything requiring API or schema changes
## Cycles
```

## The loop

```
/goal Every route and state listed in implementation/POLISH_LOG.md has been
captured with Playwright at desktop/tablet/mobile, the design reviewer subagent
reports zero remaining findings of severity medium or higher against
prompts/design/design-review-prompt.md, and the final cycle's screenshots are
recorded in the log.
```

Iteration body:

```
1. CAPTURE: Playwright-screenshot every in-scope route × viewport × state.
2. REVIEW (fresh subagent, given only the screenshots + the two design prompts,
   not the code): apply the design-review questions — hierarchy, spacing, color,
   motion, feedback, the details. Output findings with severity, the screenshot
   it's visible in, and what "right" looks like.
2b. MECHANICAL UI GATES (code-level, complements the visual review): if the
   ui-skills pack (github.com/ibelick/ui-skills) is installed, run
   /baseline-ui (animation durations, type scale, layout anti-patterns),
   /fixing-accessibility (ARIA, keyboard nav, contrast, focus),
   /fixing-motion-performance (layout thrash, compositor props), and
   /fixing-metadata on new pages. These findings merge into the cycle's
   finding list with the same severity triage.
3. TRIAGE: visual/interaction fixes within scope → fix this cycle. Anything
   needing API, schema, or flow changes → log NEEDS-HUMAN (that's a feature-loop
   item, not polish).
4. FIX: smallest CSS/markup/motion change per finding. Run existing tests —
   polish must not break behavior.
5. RECORD: append the cycle (findings, fixes, before/after screenshot paths) to
   POLISH_LOG.md, commit.
```

## Stop condition

A capture-review cycle with zero findings ≥ medium, performed *after* the last
fix commit. Same rule as the review loop: never stop on a cycle that edited.

## Budget guards

- Max 4 cycles. Taste asymptotes; cycle 5 is churn. Remaining low-severity
  findings ship in the log as a backlog, not as loop fuel.
- **Oscillation rule:** if a fix in cycle N is reversed in cycle N+1, freeze that
  element and log NEEDS-HUMAN — the rubric is ambiguous there and only a human
  can break the tie.
- Scope fence is absolute: no new components, no new routes, no copy rewrites
  beyond clarity fixes already flagged.

## Exit

Before/after screenshot pairs per cycle in the log, a clean final audit, and the
NEEDS-HUMAN list of design decisions that deserve human taste. This loop is the
standard last phase of the bootstrap loop (Phase 10.2–10.3) extracted so you can
run it on demand against any existing product.
