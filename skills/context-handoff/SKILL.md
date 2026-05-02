---
name: context-handoff
description: Create a thorough `report.md` handoff summary for transferring work between agents or sessions. Use when an agent is near a context/session/rate limit threshold such as 80%, before compaction or shutdown, when the user asks to switch agents such as Codex to Claude, when resuming work needs full context reconstruction, or whenever the user asks for a context transfer, handoff report, session summary, implementation summary, affected-files report, or remaining-work report.
---

# Context Handoff

## Overview

Create a complete `report.md` that lets another agent reconstruct the current task, file state, implementation reasoning, verification status, and remaining work without relying on hidden conversation context.

This skill can be invoked manually by the user or proactively by an agent. If the host runtime exposes an automatic threshold trigger, configure it to invoke this skill around 80% context/session usage; otherwise, invoke it as soon as context pressure, rate-limit pressure, model switching, or handoff risk becomes visible.

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
python3 /path/to/context-handoff/scripts/create_handoff_report.py --project-root . --output report.md
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
- `assets/report-template.md`: manual template for environments where the script is unavailable.
