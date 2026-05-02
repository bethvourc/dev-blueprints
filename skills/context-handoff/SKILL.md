---
name: context-handoff
description: Create a thorough `report.md` handoff summary for transferring work between any agents, models, tools, or sessions. Automatically use when the host/runtime reports that context, session, token, or rate-limit usage has reached the configured handoff threshold, defaulting to 80%; also use before compaction or shutdown, when switching between any model or agent, when resuming work needs full context reconstruction, or whenever the user asks for a context transfer, handoff report, session summary, implementation summary, affected-files report, or remaining-work report.
---

# Context Handoff

## Overview

Create a complete `report.md` that lets any next agent or model reconstruct the current task, file state, implementation reasoning, verification status, and remaining work without relying on hidden conversation context.

The intended behavior is automatic invocation at the configured handoff threshold. Default to 80% usage when the user or host has not supplied a different threshold.

## Automatic Trigger Requirement

Treat this skill as mandatory once the host/runtime reports any of these conditions:

- Context window, token budget, session limit, rate-limit budget, or compaction budget is at or above the configured handoff threshold.
- The default threshold is 80%.
- The host reports a "near limit", "compaction soon", "session ending", or equivalent warning without a precise percentage.
- The user asks to switch from one agent, model, coding assistant, chat assistant, IDE agent, or CLI agent to another.

When the threshold condition is met, invoke this skill immediately before starting more implementation work. The only acceptable work before the report is a small stabilizing action needed to leave the workspace coherent.

Important host limitation: the skill cannot measure hidden context, token, session, or rate-limit percentages by itself. The agent host or orchestration layer must expose the threshold event and load this skill automatically. If the host cannot expose that telemetry, use the nearest visible signal: compaction warning, session warning, tool/runtime warning, user request, or agent judgment that the conversation is at risk of losing context.

## Workflow Integration Contract

For seamless developer workflow integration, configure the agent host, IDE extension, CLI wrapper, or orchestration layer to follow this contract:

1. Monitor the best available usage signal: context percent, token budget percent, session budget percent, rate-limit budget percent, or compaction warning.
2. Set `CONTEXT_HANDOFF_THRESHOLD` to the desired percentage. Use `80` when unset.
3. When usage is at or above the threshold, stop normal implementation routing and invoke this skill.
4. Pass the trigger metadata into the report generator when available:

```bash
python3 /path/to/context-handoff/scripts/create_handoff_report.py \
  --project-root . \
  --output report.md \
  --handoff-reason automatic-threshold \
  --trigger-threshold 80 \
  --observed-usage "82% context" \
  --source-agent "current agent/model" \
  --next-agent "model-agnostic"
```

5. Require the active agent to complete the narrative sections before switching models.
6. Run `scripts/validate_handoff_report.py report.md`. If validation fails, fix the report before handoff.
7. Give the next agent the start prompt from `report.md`.

Do not treat `report.md` as a commit artifact by default. It is a workflow artifact unless the user explicitly wants to keep or commit it.

## Transfer Scope

Make the handoff model-agnostic. Never assume the next worker is a specific product or model family. Write the report so it works for transfers between:

- any OpenAI model or Codex session
- Claude, Gemini, local models, IDE agents, CLI agents, or other assistants
- the same agent in a later session
- a human engineer reading the report directly

## Required Workflow

### 1. Pause New Work

Stop expanding the implementation unless a tiny stabilizing action is needed to leave the workspace coherent. Do not commit, push, revert, delete, or reformat unrelated files just to prepare the handoff.

### 2. Gather Workspace State

Run repository inspection from the active project root:

```bash
git status --short
git branch --show-current
git rev-parse --short HEAD
git diff --stat
git diff --name-status
git diff --cached --stat
git diff --cached --name-status
```

If the project is not a git worktree, inspect the relevant directory tree manually and state that git evidence is unavailable.

### 3. Draft `report.md`

Prefer the bundled script when Python 3 is available:

```bash
python3 /path/to/context-handoff/scripts/create_handoff_report.py --project-root . --output report.md --trigger-threshold 80
```

The script creates a structured draft from git metadata. Treat the draft as incomplete until the active agent fills the narrative sections from conversation context and direct file review.

If the script cannot run, create `report.md` manually using `assets/report-template.md`.

### 4. Fill The Report

Complete every section with concrete, handoff-useful facts:

- Current user goal and latest instruction.
- Work completed so far, in chronological or component order.
- Files changed: every modified, added, deleted, renamed, staged, and untracked implementation file.
- Files affected: files read, APIs/contracts touched, tests/config/docs impacted, generated artifacts, and files that were important to reasoning even if unchanged.
- Reason behind each change: the user need, bug, design constraint, or dependency that caused the edit.
- Implementation details that matter to the next agent: decisions, tradeoffs, invariants, edge cases, and rejected approaches.
- Remaining implementation: exact next steps, blockers, unresolved TODOs, commands to run, and likely files to edit next.
- Verification: commands run, results, failures, skipped checks, and why any checks were not run.
- Workspace safety: unrelated dirty files, user-owned changes, generated files, credentials/secrets to avoid exposing, and commands not to run.

Define terms consistently:

- **Changed files** are files with actual filesystem or git changes.
- **Affected files** include changed files plus inspected or logically impacted files that the next agent should understand.

### 5. Validate The Handoff

Before finalizing, read `report.md` once as if you were the next agent. Fix gaps until the report answers:

- What was the user trying to accomplish?
- What did the current agent do?
- Which files changed and why?
- Which relevant files were only inspected or affected?
- What remains?
- How should the next agent verify or continue safely?

Do not leave unresolved placeholders such as `TODO`, `unknown`, or `fill in` unless the information is genuinely unavailable. When information is unavailable, explain exactly why and what the next agent should inspect.

Run the validator when Python 3 is available:

```bash
python3 /path/to/context-handoff/scripts/validate_handoff_report.py report.md
```

If validation fails, treat the output as a checklist of missing handoff context and update `report.md` before continuing.

### 6. Final User Message

After writing the report, tell the user:

- The path to `report.md`.
- Whether the report is complete or any facts are explicitly unknown.
- The exact prompt to give the next agent, for example:

```text
Read report.md in this repository first, then continue the implementation from the Remaining Implementation section. Preserve unrelated user changes and verify the current git diff before editing.
```

## Report Quality Bar

A usable handoff report must be specific enough that a capable agent can continue without asking the original agent for context. Avoid generic claims such as "updated the code" or "fixed issues"; name the files, changes, reasons, and validation evidence.

Do not include secrets, API keys, private tokens, or credentials in `report.md`. If secret handling affected the work, describe it without revealing secret values.

## Bundled Resources

- `scripts/create_handoff_report.py`: generate a `report.md` draft from git status and diff metadata.
- `scripts/validate_handoff_report.py`: detect missing required sections and unresolved placeholders before handoff.
- `assets/report-template.md`: manual template for environments where the script is unavailable.
