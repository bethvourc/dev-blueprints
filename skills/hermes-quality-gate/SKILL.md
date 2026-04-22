---
name: hermes-quality-gate
description: Use after implementation work when a user asks for Hermes, Hercules, a quality gate, post-implementation review, CI/CD readiness, validation before commit, or verification of code changes. The skill reviews diffs, runs relevant tests/lint/type checks, fixes small deterministic failures, reports residual risk, and always asks before committing or pushing.
---

# Hermes Quality Gate

Use this skill after implementation work that changes code, tests, dependencies, database schema, infrastructure, security-sensitive behavior, or production-facing UI.

Do not run the full gate for purely conversational work or documentation-only edits unless the user asks for review. For documentation-only edits, run a lightweight docs review.

## Operating Model

Hermes is the reviewer and verifier. Hercules is the remediation pass.

If the environment allows subagents and the user explicitly authorized this workflow, Hermes and Hercules may be delegated as separate agents. If not, perform the same phases locally and label the phases in updates and reports.

## Trigger Rules

Run Hermes when the work changes:

- application source code
- tests, fixtures, or generated contracts
- dependency files or lockfiles
- database migrations, schema, policies, or seed data
- infrastructure, CI/CD, deployment, or environment config
- auth, authorization, payments, tracking, messaging, privacy, or security logic
- user-facing UI, navigation, state handling, or accessibility behavior

Use a lightweight review when the work changes only:

- markdown docs
- implementation plans
- comments without behavior change
- formatting-only files

## Required Workflow

### 1. Scope The Gate

Inspect the current change set before running checks.

Required actions:

- Run `git status --short` when the repo is a git worktree.
- Inspect changed file names and changed surfaces.
- Identify whether the change affects frontend, backend, database, infra, security, docs, or generated artifacts.
- Preserve unrelated user changes. Do not revert files the agent did not intentionally change.

### 2. Hermes Review

Hermes performs a review before fixing.

Check for:

- incorrect behavior or missing edge cases
- broken contracts between frontend, backend, database, and external services
- auth or authorization gaps
- payment, delivery, tracking, or data consistency risks
- missing tests for risky behavior
- UI state gaps, loading/error/empty states, and accessibility issues
- dependency or config drift

Prefer concrete file and line references in findings.

### 3. Select Verification Commands

Run only checks relevant to the changed surfaces.

Allowed to run automatically:

- normal unit tests
- normal integration tests
- lint checks
- type checks
- format checks
- build checks that are expected to be short

Ask the user before running:

- commands expected to take a long time
- commands that download large dependencies
- destructive commands
- production deploys
- database migrations against shared environments
- commands that mutate external services
- mobile builds/signing steps that require credentials

Discover project commands from the repo instead of inventing them:

- inspect `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `melos.yaml`, `pubspec.yaml`, `pyproject.toml`, `Makefile`, `.github/workflows`, and project docs
- prefer existing scripts over raw tool invocations
- if no command exists, report the gap and suggest the command to add

Common checks by stack:

- Flutter/Dart: `dart format --set-exit-if-changed .`, `flutter analyze`, `flutter test`
- Node/TypeScript: package manager scripts for lint, typecheck, test, build
- Python: project scripts first, then formatter/linter/type/test commands if configured
- Database: migration validation, schema drift checks, RLS/policy tests if configured
- Infra: plan/validate commands, not apply/deploy unless explicitly approved

### 4. Hercules Remediation

Hercules activates only when Hermes finds fixable issues.

Allowed fixes:

- formatting failures
- lint failures with clear remedies
- type errors caused by the current change
- failing tests caused by the current change
- missing imports, obvious null handling, missing mocks, and minor test adjustments
- small documentation corrections tied to the change

Do not use Hercules for:

- product behavior changes without user approval
- large refactors
- unrelated cleanup
- reverting user edits
- hiding failures by deleting tests or weakening assertions
- bypassing auth, validation, security, or payment checks

After fixes, rerun the failed checks and any directly impacted checks.

### 5. Hermes Recheck

Confirm the final state.

Required report fields:

- changed surfaces
- checks run
- pass/fail status
- fixes applied by Hercules, if any
- remaining risks or skipped checks
- whether the change is commit-ready

### 6. Commit Readiness

Always ask before committing.

Before asking, show:

- `git status --short` summary
- changed files
- checks that passed
- checks that were skipped and why
- recommended commit message

Never push without explicit user approval.

## Report Format

Use this concise format:

```markdown
Hermes Quality Gate

Changed surfaces:
- ...

Checks run:
- ...: passed
- ...: failed

Hercules fixes:
- ...

Remaining risk:
- ...

Commit readiness:
- Ready/not ready
- Suggested commit: "..."
```

If there are failures, lead with failures and the next action.

## CI/CD Alignment

When the user asks for CI/CD setup, translate this workflow into automated jobs:

- install/cache dependencies
- format check
- lint
- typecheck/analyze
- unit tests
- integration tests
- contract/schema validation
- security/dependency scanning
- build artifacts
- staging deploy after merge or approval
- production deploy only after explicit release approval

Local Hermes should mirror CI as closely as practical, but should not replace CI.
