# Context Handoff Report

**Generated**: [date/time]
**Project root**: `[absolute path]`
**Git branch**: `[branch]`
**HEAD**: `[commit]`
**Handoff reason**: [automatic-threshold / manual-switch / compaction-warning / session-ending / other]
**Configured threshold**: [80]%
**Observed usage**: [reported usage signal or unavailable]
**Source agent/model**: [current agent/model if known]
**Intended next agent/model**: [any capable agent/model or specific target if known]

## Next-Agent Start Prompt

Read this `report.md` first, then inspect the current git status and diffs before editing. Continue from the Remaining Implementation section, preserve unrelated user changes, and update this report if the handoff assumptions are stale.

## Current User Goal

[Latest user request and desired outcome.]

## Session Summary

[What happened in this session, including decisions, pivots, constraints, and completion state.]

## Repository State

```text
[git status --short and any relevant diff stats]
```

## Files Changed

| Path | Status | Reason / handoff notes |
| --- | --- | --- |
| `[path]` | `[modified/added/deleted/etc.]` | `[why this file changed]` |

## Files Changed Details

### `[path]`
- **Status**: [status]
- **Reason behind change**: [reason]
- **What changed**: [concrete implementation details]
- **What the next agent should know**: [constraints, edge cases, coupling, hazards]
- **Verification touching this file**: [tests/checks/manual verification]

## Files Affected But Not Necessarily Changed

| Path / area | Why it matters | What the next agent should inspect |
| --- | --- | --- |
| `[path or area]` | `[impact]` | `[inspection step]` |

## Work Completed

- [Completed step with file references.]

## Reasoning Behind Key Changes

- [Design or implementation rationale.]

## Remaining Implementation

- [Exact next step.]
- [Likely files to edit next.]
- [Blockers or decisions needed.]

## Verification Performed

| Command / check | Result | Notes |
| --- | --- | --- |
| `[command]` | `[passed/failed/skipped]` | `[output summary and follow-up]` |

## Known Risks And Constraints

- [Risks, fragile assumptions, unrelated dirty files, environment constraints, skipped checks, and safety notes.]

## Workflow Integration Notes

- This report is intended as a developer workflow handoff artifact, not a commit artifact, unless the user explicitly asks to keep or commit it.
- The next agent should treat this report as context, then verify the live workspace state before editing.

## Resume Checklist

- [ ] Read this report fully.
- [ ] Run `git status --short` and compare it with the Repository State section.
- [ ] Inspect diffs for every changed file before editing.
- [ ] Continue from Remaining Implementation.
- [ ] Run or update Verification Performed before final response.
