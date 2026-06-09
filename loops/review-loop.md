# Review Loop — review and remediate a branch until clean

**Use when:** a branch/PR exists (human-written or loop-written) and you want it
reviewed, fixed, and re-reviewed until it clears the bar — without you driving each
round-trip.

**Runner:** `/goal` for the full review-fix-rereview cycle; a single pass of the
gate workflow if you only want findings, not fixes.

This loop is the Hermes/Hercules workflow from
`prompts/development/hermes-quality-gate-workflow.md` made cyclic. The critical
property: **Hermes (reviewer) and Hercules (remediator) are different agents.**
Hermes runs in a fresh subagent context every cycle so it grades the code, not its
own memory of last cycle's intentions.

## Setup

Create `implementation/REVIEW_LOG.md`:

```markdown
# Review Log — <branch>
## Cycle 0
- Scope: <diff summary, base..head>
- Status: not yet reviewed
```

## The loop

```
/goal The current branch diff has zero open Hermes findings of severity medium or
higher, all checks in the project's quality-gate command table pass (format, lint,
types, unit, integration, build, security scan), and REVIEW_LOG.md records the
final clean cycle.
```

Iteration body:

```
1. SCOPE: git diff against the base branch. Read REVIEW_LOG.md for prior cycles —
   findings already marked WONTFIX-HUMAN-APPROVED are out of scope.
2. HERMES (fresh subagent, sees only the diff + project skills, not this
   conversation): review behavior, contracts, error states, tests, security, and
   operational impact per the quality-gate workflow. For security-sensitive
   surfaces, also run skills/security-skill. Output: findings with severity,
   file:line, and a concrete expected fix.
3. TRIAGE: split findings —
   - CLEAR (mechanical or unambiguous: lint, types, broken test, missing
     validation, agreed convention) → Hercules fixes this cycle.
   - JUDGMENT (architecture, product behavior, tradeoffs) → log NEEDS-HUMAN,
     do not fix. The loop never makes product decisions.
4. HERCULES: apply only the CLEAR fixes, smallest change that resolves the
   finding. No refactors beyond the finding's scope.
5. RE-VERIFY: rerun every check that any fix could affect.
6. RECORD: append the cycle to REVIEW_LOG.md (findings, fixes, deferred items),
   commit fixes with "review-loop cycle N" in the message.
```

## Stop condition

Zero open findings ≥ medium AND all gate checks green AND no fixes were applied in
the final cycle (a cycle that changed code must be followed by a cycle that finds
that code clean — never stop on the same cycle that edited).

## Budget guards

- Max 5 cycles. A diff that isn't clean after 5 review-fix rounds has a structural
  problem; stop and summarize for the human instead of grinding.
- **Oscillation rule:** if a finding reappears after being fixed (Hermes and Hercules
  disagree), stop fixing it, log both positions NEEDS-HUMAN.
- Findings below medium severity are recorded but never block the stop condition —
  the loop ships "clean", not "perfect".

## Exit

Branch with fix commits, `REVIEW_LOG.md` showing the cycle history and the
NEEDS-HUMAN list. The human reads that list before merging — it's the loop's honest
statement of what it was not qualified to decide. Never auto-merge from this loop.
