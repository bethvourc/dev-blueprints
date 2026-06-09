# Feature Loop — new capability in an existing codebase

**Use when:** adding a feature to a project that already exists. Same skeleton as the
bootstrap loop, but the plan is scoped to a feature and the loop must protect existing
behavior, not just produce new behavior.

**Runner:** `/goal`. Run in a dedicated git worktree (`isolation: worktree` or
`git worktree add`) so the loop can't collide with your own work or a sibling loop.

## Phase A — Discover, then plan (one shot, human gate)

Discovery comes first — in an existing repo the plan is only as good as the agent's
model of what's already there:

```
1. Explore the codebase areas this feature touches: entry points, existing
   contracts, conventions, test patterns. Write findings to
   implementation/<feature>/DISCOVERY.md (existing components to reuse,
   constraints, risks, conventions to match).
2. Then, using prompts/development/master-prompt.md as your operating standard
   and prompts/development/implementation-plan-prompt.md as the framework,
   produce a feature-scoped plan in implementation/<feature>/PLAN.md.
   Include only the phases that apply — do not re-plan foundations that exist.
   Every step must state how existing behavior is protected (regression tests
   that must stay green).
```

**Human gate:** review `DISCOVERY.md` for wrong assumptions first, then `PLAN.md`.
A plan built on a misread codebase fails in iteration 4, not iteration 1 — cheaper
to catch here.

## Phase B — Loop

```
/goal Every checkbox in implementation/<feature>/PLAN.md is checked, the full
existing test suite passes (zero regressions), lint and type checks are clean,
and the feature's end-to-end flow is verified per the plan's Phase 10 steps.
```

Iteration body: identical to the bootstrap loop's six-step body
(read state → implement one step → verify → Hermes gate → record → commit), with
two additions:

- **Regression rule:** every iteration runs the existing test suite, not just the
  step's tests. A green new test with a red old test is a failed iteration.
- **Convention rule:** match what `DISCOVERY.md` documented. If the right move
  conflicts with an existing convention, log it NEEDS-HUMAN rather than silently
  introducing a second pattern.

## Stop condition

All feature-plan boxes checked + zero regressions + end-to-end verification recorded.

## Budget guards

Same as bootstrap (25 iterations, 3-strike stall rule, 80% context handoff), plus:

- **Diff budget:** if the cumulative branch diff exceeds what one human can review in a
  sitting (~600 lines as a default), stop at the next step boundary and propose splitting
  the remaining plan into a second PR/branch.

## Exit

Feature branch with atomic per-step commits, checked-off `PLAN.md`, `LOOP_LOG.md`,
and a PR description generated from the log. Hand the branch to the **review loop**
(`loops/review-loop.md`) before merging — the loop that built it doesn't get to
approve it.
