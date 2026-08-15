# Agentic Dev Blueprint

Reusable prompts, skills, and loops for agentic development.

## Structure

- `prompts/` — the raw material
  - `development/master-prompt.md` — the operating persona: staff-level, production-first
  - `development/implementation-plan-prompt.md` — turns an idea into a checkboxed, dependency-ordered plan
  - `development/hermes-quality-gate-workflow.md` — reviewer (Hermes) / remediator (Hercules) gate
  - `design/` — design review prompt and taste standard
  - `system/` — system-prompt authoring guides
- `skills/` — packaged project knowledge agents load instead of guessing
  - `hermes-quality-gate/`, `security-skill/`, `context-handoff/`
- `loops/` — the wiring layer: closed loops that drive the prompts and skills autonomously
  - Start with [`loops/README.md`](loops/README.md) for the architecture
  - `bootstrap-loop.md` (new project → production-ready system), `feature-loop.md`,
    `review-loop.md`, `triage-loop.md` (scheduled discovery), `polish-loop.md`
    (design audit-and-fix), `example-walkthrough.md` (one product traced through
    every loop and nesting level)

## The model

Prompts define *how to work*. Skills make that knowledge loadable. Loops decide
*when to work and when to stop*: plan once with a human gate, iterate one plan step
per pass, verify with an independent checker, record state on disk
(`PLAN.md` / `LOOP_LOG.md`), and stop on a mechanically verifiable condition.
