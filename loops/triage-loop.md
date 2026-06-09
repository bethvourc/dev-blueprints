# Triage Loop — recurring discovery and queue-feeding

**Use when:** you want a heartbeat over a repo: surface CI failures, stale issues,
dependency drift, TODO debt, and flaky tests — and turn the worthwhile ones into
*plan entries* that other loops execute.

**Runner:** `/schedule` (cloud cron, survives your laptop closing) or `/loop 24h`
(in-session interval). This is the only loop here that runs on a timer instead of
toward a goal — it's the automation heartbeat; the other loops are the muscles.

**Key design rule: triage discovers, it does not fix.** The moment a triage loop
starts fixing things it becomes an unbounded open loop with no plan and no human
gate. Its only write targets are `implementation/TRIAGE.md` and (optionally) issue
tracker tickets via connectors.

## State

`implementation/TRIAGE.md`:

```markdown
# Triage Board
## Inbox        <- new findings land here, one line each, with evidence link
## Accepted     <- human moved it here; ready to become a feature-loop plan
## In progress  <- a loop/worktree is on it, link to its PLAN.md
## Done / Won't fix
```

The human moves items from Inbox to Accepted. That move is the closed-loop gate
between "the system noticed something" and "the system spends tokens on it".

## The scheduled prompt

```
You are the triage agent for <repo>. Read implementation/TRIAGE.md first —
never re-report an item already on the board.

Sweep, in order:
1. CI: failures and flaky tests since the last run (link the run, name the test).
2. Issues/PRs: new, stale (>14d), or unanswered review comments.
3. Drift: dependency advisories, deprecation warnings in build output.
4. Debt: new TODO/FIXME/HACK markers in the diff since the last sweep.
5. Quality: run the lightweight gate (lint, types) on the default branch; report
   any rot that merged.

For each NEW finding, append one Inbox line: what, where (file:line or URL),
evidence, suggested severity, and a one-sentence suggested next action.
If a finding is severe (main broken, security advisory on a direct dependency),
also notify via the configured connector (Slack/issue) immediately.

If the sweep finds nothing new, append a dated "clean sweep" line and exit —
do not invent work to justify the run.
```

## Hand-off to the other loops

When you move an item to **Accepted**, spawn the right loop for it:

- Bug/regression → **feature loop** with a minimal plan (often 2–4 steps)
- "This area needs review" → **review loop** on the relevant diff
- UX complaint → **polish loop** scoped to the affected routes
- Big capability gap → full **bootstrap/feature plan** session first

Each spawned loop gets its own worktree and its own `PLAN.md` under
`implementation/<item-slug>/`, and links back to the TRIAGE.md line.

## Budget guards

- Read-mostly by design: the sweep itself must not modify source code, ever.
- Cap Inbox additions at 10 per run; past that, summarize the overflow in one line
  ("12 further lint findings, run full gate to enumerate").
- If two consecutive sweeps are clean, it's fine — a quiet triage loop is a healthy
  repo, not a broken loop.
