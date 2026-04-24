# Hermes Quality Gate Workflow Template

Use this template in any project that needs a repeatable post-implementation review, remediation, and commit-readiness workflow.

Recommended project files:

- `skills/hermes-quality-gate/SKILL.md` for the reusable Codex skill
- `docs/workflows/hermes-quality-gate.md` or `implementation/HERMES_QUALITY_GATE.md` for project-specific rules
- `.github/workflows/ci.yml` for automated CI once the repo is ready

## Roles

Hermes is the reviewer/verifier.

Hercules is the remediation pass that fixes clear, scoped failures found by Hermes.

Use subagents only when the active environment permits them and the user has authorized that workflow. Otherwise, run the same phases locally.

## Trigger Policy

Run the full gate after changes to:

- source code
- tests
- dependencies or lockfiles
- database schema or migrations
- infrastructure or CI config
- auth, payments, security, permissions, or data privacy behavior
- user-facing UI

Use a lightweight gate for documentation-only work.

## Project Setup Checklist

Customize these values for the project:

| Area | Project Value |
| --- | --- |
| Frontend stack | `[example: Flutter, React, Next.js]` |
| Backend stack | `[example: NestJS, Go, Django]` |
| Package manager | `[example: pnpm, npm, yarn, melos, uv]` |
| Format command | `[command]` |
| Lint command | `[command]` |
| Type/analyze command | `[command]` |
| Unit test command | `[command]` |
| Integration test command | `[command]` |
| Build command | `[command]` |
| Database validation | `[command or N/A]` |
| Security scan | `[command or N/A]` |
| UI verification | `[screenshots, golden tests, Playwright, Flutter widget tests, manual checklist]` |

## Local Workflow

1. Scope the diff.
   - Run `git status --short`.
   - Identify changed surfaces.
   - Preserve unrelated user changes.

2. Hermes review.
   - Review behavior, contracts, error states, tests, security, and operational impact.
   - Lead with concrete findings if anything is wrong.

3. Run relevant checks.
   - Run normal tests, lint, type checks, and format checks automatically.
   - Ask before long-running, destructive, cloud-mutating, or deployment commands.

4. Hercules remediation.
   - Fix clear formatting, lint, type, and test failures.
   - Avoid broad refactors or product changes without approval.

5. Hermes recheck.
   - Rerun failed checks.
   - Summarize the final state.

6. Commit readiness.
   - Report changed files, checks run, skipped checks, remaining risk, and suggested commit message.
   - Always ask before committing.
   - Never push without explicit approval.

## CI/CD Jobs

Translate the local workflow into CI:

- install dependencies with cache
- format check
- lint
- typecheck/analyze
- unit tests
- integration tests
- contract/schema validation
- security/dependency scan
- build artifacts
- staging deploy after merge or approval
- production deploy only after explicit release approval

## Report Template

```markdown
Hermes Quality Gate

Changed surfaces:
- ...

Checks run:
- ...: passed
- ...: failed

Hercules fixes:
- ...

Skipped checks:
- ... because ...

Remaining risk:
- ...

Commit readiness:
- Ready/not ready
- Suggested commit: "..."
```
