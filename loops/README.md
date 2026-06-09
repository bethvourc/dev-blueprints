# Loop Architecture

This directory defines the looping layer of dev-blueprints: closed, bounded loops that drive the prompts in `prompts/` and the skills in `skills/` without a human prompting each step.

## The core idea

A loop is not a new prompt. It is a wiring diagram around prompts you already have:

```
                ┌─────────────────────────────────────────┐
                │              LOOP RUNNER                │
                │   (/goal, /loop, ralph-loop, schedule)  │
                └───────────────────┬─────────────────────┘
                                    │ each iteration
                                    ▼
   PERSONA                  ┌──────────────┐
   prompts/development/ ──► │  1. READ     │  read state file, pick next
   master-prompt.md         │     STATE    │  unchecked step
                            ├──────────────┤
   PLAN = STATE             │  2. WORK     │  implement exactly one step,
   implementation/PLAN.md ─►│              │  scoped to that step's Files list
   (checkboxes)             ├──────────────┤
                            │  3. VERIFY   │  Hermes quality gate +
   skills/                  │              │  step's Testing / UI Verification
   hermes-quality-gate ────►├──────────────┤
                            │  4. RECORD   │  check the box, append to
                            │              │  LOOP_LOG.md, commit atomically
                            └──────┬───────┘
                                   │
                     stop condition met? ──no──► next iteration
                                   │yes
                                   ▼
                          final review + handoff
                          (skills/context-handoff)
```

## The canonical cycle

Every loop in this directory — at every nesting level — is the same five-phase
cycle (per @shannholmberg's agent-looping diagram), just at different scale:

| Phase | At plan scale (L1) | At step scale (L2) | At gate scale (L3) |
| --- | --- | --- | --- |
| 1. Discovery | explore codebase → `DISCOVERY.md` | read `PLAN.md` + `LOOP_LOG.md` for prior attempts | read the diff + project skills |
| 2. Planning | generate `PLAN.md` (human-gated) | pick the next dependency-free step | triage findings CLEAR vs JUDGMENT |
| 3. Execution | run the step loop until done | implement the one step | apply the scoped fix |
| 4. Verification | stop-condition check by independent grader | step's Testing/UI fields + gates | rerun affected checks |
| 5. Iteration | next step, or final audit | fix gaps, ≤3 strikes, record | next cycle until clean, ≤5 |

"Verification passes → hand off or ship; otherwise fix and loop" is the universal
exit rule. This self-similarity is what makes a fleet coherent: an orchestrator,
its specialists, and their subagents aren't running different processes — they're
running the same cycle on differently-sized goals, which means the same budget
guards and stop-condition discipline apply at every node of the tree.

## The six pieces, mapped to this repo

| Loop piece | What this repo uses |
| --- | --- |
| Automation / heartbeat | Claude Code `/goal` (run-until-condition), `/loop` (interval), `/schedule` (cron cloud agents), or the `ralph-loop` plugin |
| Worktrees | `isolation: worktree` on subagents; one worktree per loop when running loops in parallel |
| Skills | `skills/hermes-quality-gate`, `skills/security-skill`, `skills/context-handoff` — plus external skill packs like [ibelick/ui-skills](https://github.com/ibelick/ui-skills) (`baseline-ui`, `fixing-accessibility`, `fixing-metadata`, `fixing-motion-performance`) for UI gates |
| Plugins / connectors | MCP connectors (GitHub, Linear, Slack) declared per-project, not here |
| Sub-agents (maker ≠ checker) | The implementing agent never grades itself: Hermes (reviewer) and Hercules (remediator) run as separate subagents or separate phases |
| Memory | `implementation/PLAN.md` (the checkboxed plan **is** the state file) + `implementation/LOOP_LOG.md` (what was tried, what failed, what's next) |

## The twist: the implementation plan is the loop state

Most loop setups invent a separate state file. We don't. The plan format in
`prompts/development/implementation-plan-prompt.md` already produces:

- `- [ ]` checkboxes → the work queue and progress ledger
- **Dependencies** fields → the ordering constraint the loop must respect
- **Testing** / **UI Verification** fields → the per-step eval gate, written before the code exists
- **Files** lists → the blast-radius bound (≤10 files per step)

So every loop here follows the same lifecycle:

1. **Plan phase (one shot, human-reviewed):** run `prompts/development/master-prompt.md`
   as the system persona with `prompts/development/implementation-plan-prompt.md` as the
   planning framework. Output goes to `implementation/PLAN.md`. **A human reads and edits
   the plan before any loop starts.** This is the "closed loop" boundary — the human
   designs the path, the loop walks it.
2. **Loop phase (autonomous):** the runner iterates step-by-step until the stop condition.
3. **Exit phase:** final review (Phase 10 of the plan framework), then `context-handoff`
   writes `report.md` so the next session/agent/human can pick up cold.

## Stop conditions (write these, don't improvise them)

Every loop must declare a *verifiable* stop condition before it starts. Good ones:

- "Every checkbox in `implementation/PLAN.md` is checked AND the full quality gate passes"
- "Zero Hermes findings of severity ≥ medium on the current diff"
- "All tests in `tests/` pass and lint is clean"

Bad ones: "the feature works", "the code is good", "done". If a fresh verifier agent
can't evaluate it mechanically, it is not a stop condition.

This is the open/closed cost line: open loops with a loose standard are fast slop
machines on an unlimited budget; closed loops are cheap and repeatable precisely
because the human built the path and the eval first. The standard is what keeps
the loop honest — weaken the stop condition and you haven't made the loop faster,
you've made it open.

## Budget guards (every loop, no exceptions)

- **Max iterations:** default 25 per loop run. Hitting it = stop and write a handoff, not "keep trying".
- **Stall detection:** if the same step fails verification 3 times, stop, log the failure
  in `LOOP_LOG.md` with what was tried, and surface to the human. Do not widen scope to "fix it".
- **Scope fence:** an iteration may only touch files listed in its step (plus tests).
  Anything else is a new plan entry, not a detour.
- **Context guard:** at ≥80% context usage, invoke `skills/context-handoff` and let the
  next session resume from `report.md` + `PLAN.md`. The loop survives; the session doesn't have to.

## Maker / checker separation

The agent that wrote the code never decides the loop is done:

- Per-step gate: Hermes review (separate subagent, fresh context) per
  `prompts/development/hermes-quality-gate-workflow.md`. Hercules fixes only clear,
  scoped findings; ambiguous findings go to `LOOP_LOG.md` for the human.
- Loop-level gate: `/goal`'s independent grader, or a final verifier subagent that
  re-checks the stop condition against the rubric with no knowledge of how the work was done.

## The loops

| Loop | File | Use case | Runner |
| --- | --- | --- | --- |
| Bootstrap | [bootstrap-loop.md](bootstrap-loop.md) | New project from idea/PRD to deployable skeleton | `/goal` |
| Feature | [feature-loop.md](feature-loop.md) | New feature in an existing codebase | `/goal` |
| Review | [review-loop.md](review-loop.md) | Review + remediate a branch/PR until clean | `/goal` or one-shot |
| Triage | [triage-loop.md](triage-loop.md) | Recurring discovery: CI failures, issues, drift | `/schedule` or `/loop` |
| Polish | [polish-loop.md](polish-loop.md) | Design/UX audit-and-fix until the design bar is met | `/goal` |

Each blueprint is copy-paste runnable: it contains the goal statement to give the runner,
the iteration body, the verification gate, the stop condition, and the budget guards.

## Nested loops

The loops above are not flat — they compose. A "fleet" is just loops nested with
clear contracts between levels, and every node in the tree runs the same
five-phase canonical cycle from the top of this doc — orchestrator, specialist,
and subagent differ only in the size of the goal they own:

```
L0  TRIAGE LOOP            (scheduled, forever)        discovers work
     │  human accepts an item ──────────────┐
     ▼                                      ▼
L1  BOOTSTRAP / FEATURE LOOP (per goal)     owns one PLAN.md, runs to its stop condition
     │  each iteration
     ▼
L2  STEP LOOP               (per plan step) implement → verify → fix, ≤3 strikes
     │  each step's gate
     ▼
L3  GATE LOOPS              (per gate)      Hermes↔Hercules cycles, security re-scan,
                                            polish capture→review→fix cycles
```

Rules that keep nesting from becoming chaos:

1. **One state file per loop level.** L1 owns `PLAN.md`. L2 writes only to its step's
   checkbox and `LOOP_LOG.md`. L3 gate loops write findings, never plan entries.
   A child loop never edits its parent's goal.
2. **Children report up, never sideways.** A gate loop's unresolved finding becomes a
   NEEDS-HUMAN log line or a BLOCKED step — it does not spawn a sibling loop on its own.
   Only L0→L1 spawning involves a human gate (moving a triage item to Accepted).
3. **Budgets divide downward.** The parent's iteration budget bounds the children:
   L1 gets ~25 iterations, each L2 step gets 3 strikes, each L3 gate gets 3–5 cycles.
   A child that exhausts its budget fails upward with its history; it never borrows
   budget from a sibling.
4. **Stop conditions compose upward.** L1's stop condition ("all boxes checked") is
   only satisfiable if every L2 succeeded, which required every L3 gate to pass.
   Verifying the top verifies the tree — that's why each level's check must be
   mechanical.
5. **Depth is capped at these four levels.** A loop spawning a loop spawning an
   unplanned loop is the open-loop slop machine with extra steps. New depth = new
   blueprint in this directory, reviewed by a human first.
6. **Parallel siblings get worktrees.** Two L1 loops on one repo = two worktrees +
   two namespaced state dirs (`implementation/<slug>/`), merged through the review
   loop like any other branch.

Concrete nestings already wired into the blueprints: the bootstrap loop's Phase C
runs the **polish loop** as a child; the feature loop hands its branch to the
**review loop**; the triage loop spawns **feature loops** for accepted items.
See [example-walkthrough.md](example-walkthrough.md) for one goal traced through
all four levels.

## Patterns borrowed from prior art

From [supergoal](https://github.com/robzilla1738/supergoal) (a planning + autonomous
execution system for `/goal` on Claude Code/Codex), four patterns adopted here:

- **Baseline ref:** capture HEAD at loop start; the final audit diffs the whole run
  against it, catching cross-step regressions a per-step gate can't see.
- **Escalating three-strike recovery:** retry-with-diagnosis → written fix-spec →
  fail upward with history. Never three identical retries.
- **Namespaced state dirs** (`implementation/<slug>/`) so parallel loops coexist in
  one repo without clobbering each other's state.
- **Subjective-verification warning:** if more than ~30% of a plan's Testing fields
  are subjective ("looks right", "feels fast"), flag the plan at the human gate —
  a loop can only hill-climb on checks a machine can run.

One supergoal idea deliberately *not* adopted: fully automated intake → plan → run
in one paste. We keep the human plan-review gate; it's the closed-loop boundary.

## What the loops do not do

The loop ships nothing you haven't confirmed. You still:

- review and edit `PLAN.md` before the loop starts (the plan is the contract),
- read `LOOP_LOG.md` and the diffs the loop produced,
- own the merge. "All boxes checked" is a claim, not a proof.
