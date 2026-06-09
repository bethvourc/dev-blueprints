# Worked Example — StatusBeacon, traced through every loop

A concrete run-through so the blueprints aren't abstract. The product:
**StatusBeacon**, a hosted status-page service. Teams sign up, create a status page,
add components ("API", "Dashboard"), post incidents, and StatusBeacon pings their
endpoints every minute and auto-opens incidents on downtime. Real auth, real billing
surface, real background jobs, real public pages — a genuinely production-shaped target.

## Day 1 — Plan phase (human in the loop)

You run the bootstrap loop's Phase A prompt with the StatusBeacon brief. The agent,
operating under `master-prompt.md` + `implementation-plan-prompt.md`, produces
`implementation/PLAN.md`: ~40 steps across phases 0–10 — architecture docs, repo
standards, CI, domain contracts (Page, Component, Incident, Check), Postgres schema
and migrations, auth + org membership, validation and rate limiting, the uptime
checker as a background job with retries and dead-lettering, the public status page,
the dashboard, structured logging, health endpoints, deploy pipeline, rollback
runbook, final audit.

**You read it.** You cut the SMS-notification step (not v1), tighten Step 6.1's
Testing field from "verify checks work" to "simulated endpoint returns 500 → incident
auto-opens within 2 check cycles; flapping endpoint → no duplicate incidents", and
note that Stripe steps will be NEEDS-HUMAN until you supply test keys. You commit the
plan and the baseline ref lands in `LOOP_LOG.md`. This 30 minutes of editing is the
highest-leverage work in the whole project.

## Day 1–3 — The bootstrap loop runs (L1)

```
/goal Every checkbox in implementation/PLAN.md is checked, the project builds,
all tests pass, lint and type checks are clean, security steps have zero
unresolved findings ≥ medium, and Step 10.4 has an explicit GO in LOOP_LOG.md.
```

What a healthy iteration looks like (L2, one plan step):

> **Iteration 9 — Step 3.1 (auth + org membership).** Reads PLAN.md, finds 3.1 is the
> first unchecked step with satisfied dependencies. Implements session auth and the
> org-role model — only the files in the step's Files list. Runs the step's tests:
> login, logout, protected routes, role matrix. Spawns Hermes (L3) on the diff:
> Hermes flags that the session cookie lacks `SameSite` and that the invite endpoint
> doesn't check org membership. Both are CLEAR findings → Hercules fixes, checks
> rerun green. Because this step touches auth, `security-skill` also runs: clean.
> Box checked, LOOP_LOG entry written, committed as `step-3.1: auth + org membership`.

What a failure looks like (the three-strike rule earning its keep):

> **Iterations 14–16 — Step 6.1 (uptime checker job).** Strike 1: the
> flapping-endpoint test fails — duplicate incidents. The agent diagnoses (no
> debounce window), logs the hypothesis, adds one, retries: still failing
> intermittently. Strike 2: writes a fix-spec in LOOP_LOG.md — the race is two
> concurrent checks for the same component; fix is a uniqueness constraint on open
> incidents per component plus an idempotent open-incident operation. Executes the
> spec: tests pass 20/20 runs. Hermes gate passes. Box checked. The spec stays in
> the log, so a future session (or you) can see *why* that constraint exists.

What honest blocking looks like:

> **Iteration 21 — Step 6.3 (Stripe billing).** No test keys in the environment.
> The agent does **not** mock it and call it done — it marks the step BLOCKED /
> NEEDS-HUMAN ("requires STRIPE_TEST_KEY; webhook signature verification is written
> but unverified against a live test event") and moves on to Step 7.1.

Around iteration 25 the session hits its cap mid-phase-7. `context-handoff` writes
`report.md`; you skim `LOOP_LOG.md` over coffee, drop the Stripe keys into the env,
flip 6.3 back to unchecked, and start a fresh session with the same `/goal`. The new
session reads `PLAN.md` + `report.md` and resumes exactly where the last one stopped.
That's the disk-state design doing its job — the loop outlives the context window.

## Day 3 — Final audit, with the polish loop nested inside (Phase C)

Phase 10 steps run as normal iterations, but whole-system: build/test/lint/security
against the **baseline ref**, full Playwright sweep. Step 10.2–10.3 invoke the
**polish loop** as a child (L3): capture every route × viewport × state; a fresh
reviewer subagent judges screenshots against `design-review-prompt.md`; the
ui-skills gates (`/baseline-ui`, `/fixing-accessibility`,
`/fixing-motion-performance`, `/fixing-metadata` on the public status page — the
one page where SEO/social tags actually matter) run on the code. Cycle 1 finds 11
findings; cycle 2 finds 2; cycle 3 is clean. The audit's verifier records GO in
LOOP_LOG.md with two NEEDS-HUMAN items: the Stripe live-mode webhook is still
unverified, and the empty-state illustration is a judgment call.

**You** read the NEEDS-HUMAN list, verify the Stripe webhook against a live test
event yourself, shrug at the illustration, and ship. The loop claimed GO; you decided
merge.

## Week 2 onward — the triage loop takes over (L0)

```
/schedule daily 07:00 — triage sweep on statusbeacon repo
```

Wednesday's sweep appends to `implementation/TRIAGE.md`:

> - [Inbox] Flaky: `checker.test.ts > backoff after 3 failures` failed 2/14 CI runs
>   (link). Suggested: feature-loop, severity medium.
> - [Inbox] Dependency advisory: `jsonwebtoken` < 9.0.3 (GHSA-XXXX). Suggested:
>   feature-loop, severity high. *(Also pinged Slack because severity ≥ high.)*

It fixes nothing — discovery only. Thursday you move the advisory to **Accepted**.
That human move is the gate that spends tokens.

## The accepted item becomes a feature loop (L1 again, nested under L0)

A worktree is created, and a scoped run begins: discovery first
(`implementation/jwt-upgrade/DISCOVERY.md` — where tokens are issued/verified, what
the upgrade changes), then a 4-step plan, then `/goal` with a zero-regression stop
condition. Three iterations later the branch is done — and is handed to the
**review loop**, not merged: Hermes (fresh context) reviews the diff over 2 cycles,
Hercules fixes one CLEAR finding (a missed token-verify call site found by grep),
cycle 3 is clean with zero code changes, `REVIEW_LOG.md` records it. You read the
log, merge, and TRIAGE.md's item moves to Done with links to the plan, the log, and
the PR.

## The full nesting, in one picture

```
L0 triage (daily, forever)
 └─ human accepts "jwt advisory"
     └─ L1 feature loop (worktree, own PLAN.md)
         ├─ L2 step iterations (implement → verify, ≤3 strikes each)
         │    └─ L3 Hermes/security gates per step
         └─ hands branch to review loop (L3-style gate at branch scope)
              └─ human merges

L1 bootstrap loop (days 1–3, multiple sessions)
 ├─ L2 step iterations × ~40
 │    └─ L3 gates per step
 └─ Phase C audit
      └─ L3 polish loop (capture → review → fix, 3 cycles)
```

Every level: its own state file, its own budget, a mechanical stop condition, and
failures that surface upward instead of being silently absorbed. Every human
appearance is at a gate you chose in advance — plan review, triage acceptance,
NEEDS-HUMAN list, merge. You prompted almost nothing; you decided everything.
