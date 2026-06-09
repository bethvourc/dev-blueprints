# Bootstrap Loop — new project, idea to production-ready system

**Use when:** starting a project from an idea, PRD, or product brief.
**Runner:** Claude Code `/goal` (preferred) or `ralph-loop`.
**Persona:** `prompts/development/master-prompt.md` loaded as the system/project prompt
(copy it into the new repo's `CLAUDE.md` or reference it directly).

**The target is the full system, not a skeleton.** The master prompt's standard —
"you do not ship features, you ship complete systems" — is the loop's standard. The
loop does not stop when the app runs; it stops when every phase of the plan,
including security, observability, resilience, deployment, rollback, and the
Phase 10 audit, is verified done. No mockups, no stubbed integrations left behind,
no "TODO: add auth later". If a step can't be completed for real (e.g., a missing
third-party credential), it gets logged NEEDS-HUMAN and the loop continues on
unblocked steps — it never fakes the step to keep moving.

## Phase A — Plan (one shot, human gate)

Run once, outside the loop:

```
Using prompts/development/master-prompt.md as your operating standard and
prompts/development/implementation-plan-prompt.md as the planning framework,
produce the full implementation plan for: <idea / PRD link / brief>.
Cover all phases 0–10 — foundations, contracts, security, services, frontend,
integrations, observability, hardening, release engineering, final audit.
Write it to implementation/PLAN.md. Do not implement anything.
```

**Human gate (mandatory):** read `PLAN.md`. Cut steps you don't want, reorder if the
dependency fields allow it, tighten any vague Testing fields. The loop will treat this
file as law — fix it now, not mid-run. Do not delete the security, observability, or
release phases to "go faster"; that converts this from a production loop into a
prototype loop.

Then initialize loop state:

- `implementation/LOOP_LOG.md` — starts with `# Loop Log` and the **baseline ref**
  (current HEAD sha). Every later verification diff is measured against this baseline,
  so the final audit can check the whole system, not just the last step.

## Phase B — Loop (autonomous)

Start the runner with this goal:

```
/goal Every checkbox in implementation/PLAN.md is checked, the project builds,
all tests pass, lint and type checks are clean, the security review steps have
zero unresolved findings of severity medium or higher, and Step 10.4's
production readiness checklist has an explicit GO decision recorded in
implementation/LOOP_LOG.md.
```

Iteration body (this is the prompt the loop executes each pass):

```
You are operating under prompts/development/master-prompt.md.

1. READ implementation/PLAN.md. Find the first unchecked step whose Dependencies
   are all checked. If none exists, run the stop-condition check and finish.
2. READ implementation/LOOP_LOG.md for prior attempts at this step. Never repeat
   a failed approach without changing something.
3. IMPLEMENT only that step — fully. Real integrations, real validation, real
   error handling per the step spec. Touch only the files in its Files list plus
   tests. If the step turns out to need files outside its list, STOP, append a
   new step to PLAN.md describing the gap, log why in LOOP_LOG.md, and end this
   iteration.
4. VERIFY exactly what the step's Testing and UI Verification fields say.
   UI-affecting steps: Playwright screenshots per the step's spec, reviewed
   against prompts/design/design-review-prompt.md standards.
5. GATE — two layers:
   a. Hermes reviewer subagent (fresh context, no knowledge of your reasoning)
      per prompts/development/hermes-quality-gate-workflow.md on the step's diff.
      Hercules-fixes clear findings; ambiguous findings go to LOOP_LOG.md tagged
      NEEDS-HUMAN and the step stays unchecked.
   b. Security gate: for any step touching auth, input handling, secrets, data
      access, external integrations, or infrastructure, additionally run
      skills/security-skill on the diff. Security findings ≥ medium block the
      checkbox — they are never deferred to "later hardening".
6. RECORD: check the box in PLAN.md, append one LOOP_LOG.md entry
   (step id, what changed, verification evidence, open risks), and commit
   atomically with the step id in the commit message.
```

**Step-level recovery (three strikes, escalating — not three identical retries):**

1. First failure → diagnose before retrying: read the actual error, form a
   hypothesis, log it, retry with the fix.
2. Second failure → write a micro fix-spec in LOOP_LOG.md (what's wrong, what to
   change, how to verify) and execute that spec.
3. Third failure → mark the step `BLOCKED` in PLAN.md with the full attempt
   history, move to the next dependency-free step. If nothing is unblocked, stop
   and hand off.

## Phase C — Final audit (inside the loop, non-negotiable)

Phase 10 of the plan runs as ordinary loop steps, but with whole-system scope:
re-run build/test/lint/security against the **baseline ref** (everything since the
loop started, not the last diff), the full Playwright audit, the polish pass
(see `loops/polish-loop.md` — this is where it nests), and the production
readiness checklist. The audit gets up to **3 self-heal rounds**: if it finds
cross-step regressions, fix and re-audit. Still failing after 3 → stop, hand off
with the findings. The GO/NO-GO decision is written by the verifier context, not
the implementing context.

## Stop condition

All boxes checked + full quality gate green + security clean + Phase 10 GO recorded.
The `/goal` grader verifies this independently — the implementing context never
self-certifies.

## Budget guards

- Max 25 iterations per session; at the cap, run `skills/context-handoff` and stop.
  (A real product takes multiple sessions — the loop is designed to survive that;
  `PLAN.md` + `LOOP_LOG.md` + `report.md` are the resume state.)
- Three-strike rule above; BLOCKED steps surface to the human, the loop never
  grinds on one step.
- At ≥80% context: `skills/context-handoff` → new session resumes from
  `report.md` + `PLAN.md`.

## Exit

Final artifact set: a deployable, monitored, secured, documented system; a fully
checked-off `PLAN.md`; `LOOP_LOG.md` with the audit history and NEEDS-HUMAN list;
runbooks per the plan's Phase 9; and `report.md` for the next session or engineer.
The human reviews the NEEDS-HUMAN list and the diffs before anything reaches
production — "GO recorded" is the loop's claim; the merge is your decision.
