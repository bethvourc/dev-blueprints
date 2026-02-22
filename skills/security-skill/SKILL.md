---
name: security-scan
description: >
  Perform a rigorous, evidence-driven application security review across source code,
  configuration, auth boundaries, data flows, and dependencies. Detect likely exploitable
  vulnerabilities, prioritize by real risk, and produce actionable fixes with validation steps.
  Use when the user asks to run a security scan, audit vulnerabilities, review auth/data exposure,
  or harden a codebase before release.
metadata:
  author: bethvour
  version: "2.1.0"
  tags: security, audit, vulnerability, owasp, sast, appsec
  argument-hint: "[path-or-scope]"
---

# Security Scan Skill

## Mission

Act as a senior application security engineer performing a production-grade audit.
Maximize real vulnerability detection and minimize false positives.

Do not claim absolute security. No audit can prove a system is unbreakable.
Goal: surface credible, evidence-backed risks and concrete remediations.

## Bundled Resources

- `scripts/run_scan.sh`: deterministic collector for pattern scans, secrets signals, manifests, and optional dependency audit outputs.
- `scripts/collect_findings.py`: normalizes raw outputs into `findings.json` and draft markdown report.
- `references/report_template.md`: canonical report template used to structure final output.

## Operating Principles

1. Evidence over pattern matching: confirm findings with code-path context and attacker-controlled inputs.
2. Exploitability first: prioritize issues that are reachable and impactful in real deployments.
3. No invented CVEs: only report dependency vulnerabilities with verifiable package/version evidence.
4. No silent assumptions: explicitly state trust boundaries, assumptions, and confidence.
5. Reproducible output: every finding must include proof and a fix path that can be validated.

## Script-First Execution (Required)

Run scripts first, then perform manual validation:

1. Execute deterministic scan:
   - `~/.claude/skills/security-scan/scripts/run_scan.sh [target_path] [output_dir_optional]`
2. Review generated artifacts:
   - `raw/` for direct command output evidence
   - `meta/` for scan context and status files
   - `findings/findings.json` for normalized findings
   - `findings/findings.md` for draft report
3. Validate each high-impact finding manually in code-path context.
4. Produce final report using `references/report_template.md` structure.

If optional tools are missing (`pnpm audit`, `npm audit`, `pip-audit`, `cargo-audit`), continue with available evidence and state coverage gaps explicitly.

## Required Workflow (In Order)

### Phase 0: Scope and Constraints

1. Determine scan scope (full repo or provided path).
2. Identify environments (dev/staging/prod assumptions, public vs internal exposure).
3. If critical context is missing, proceed with conservative assumptions and state them.

### Phase 1: Architecture and Threat Surface

1. Identify stack: languages, frameworks, runtime, package managers, datastore, auth/session model.
2. Map trust boundaries:
   - Internet-facing entry points (API routes, forms, webhooks, upload handlers)
   - Privileged execution points (admin actions, background jobs, CI/CD)
   - Data boundaries (PII, secrets, tokens, payment data, internal-only data)
3. Map authz model:
   - Authentication mechanisms
   - Role/permission checks
   - Tenant isolation boundaries

### Phase 2: Deep Vulnerability Analysis

Analyze all relevant categories below with data-flow awareness.
For each suspected issue: verify user-controlled source -> sensitive sink path.

1. Secrets and credential exposure
2. Injection risks (SQL/NoSQL/command/template/LDAP/XML/header/path traversal)
3. AuthN/AuthZ flaws (missing checks, IDOR, privilege escalation, weak session/JWT)
4. Sensitive data exposure (logging, error leaks, transport/storage weaknesses)
5. Dependency and supply-chain risk (manifest + lockfile + verifiable advisory)
6. Security misconfiguration (CORS, headers, cookies, debug exposure, redirects)
7. Cryptography misuse (weak algorithms, key handling, insecure randomness)
8. Business logic abuse (race conditions, mass assignment, workflow bypass)

### Phase 3: Validation and False-Positive Control

Before finalizing each finding, perform these checks:

1. Reachability: can attacker input reach the vulnerable code path?
2. Preconditions: are required attacker conditions realistic?
3. Existing mitigations: is there upstream validation/sanitization/authorization?
4. Environment impact: is this exploitable in likely production deployment?
5. Confidence grade:
   - Confirmed: clear vulnerable path and impact shown from code.
   - Probable: strong indicators but one assumption remains.
   - Potential: plausible but blocked by missing runtime context.

If uncertain, downgrade confidence and explain exactly what evidence is missing.

### Phase 4: Remediation Design

For each finding, provide both:

1. Quick fix: minimal patch to reduce immediate risk.
2. Durable fix: robust long-term mitigation (design/policy/test/process).

Each fix must include validation steps (what to test, expected secure behavior).

## Severity and Prioritization

Assign severity by impact x exploitability (not by pattern name alone).

- CRITICAL: easily exploitable, high-impact compromise (RCE, auth bypass, major data breach)
- HIGH: exploitable with moderate effort, significant data/privilege impact
- MEDIUM: constrained exploitability or limited blast radius
- LOW: defense-in-depth or low-impact weakness

Also assign confidence: Confirmed / Probable / Potential.

## Dependency and CVE Rules

When reporting dependency vulnerabilities:

1. Include package name and exact resolved version.
2. Include advisory identifier if available (CVE/GHSA/OSV).
3. If advisory cannot be verified from available evidence, label as "Unverified advisory".
4. Do not fabricate CVE IDs or claim exploitability without version match.

## Output Format (Required)

```markdown
# Security Audit Report

**Project**: [name]
**Date**: [YYYY-MM-DD]
**Scope**: [paths/components scanned]
**Assumptions**: [deployment/trust assumptions]
**Overall Risk**: [CRITICAL/HIGH/MEDIUM/LOW]

## Executive Summary
[2-5 concise sentences focused on the highest-risk issues]

## Threat Surface Snapshot
- Internet-facing entry points: [...]
- Auth boundaries: [...]
- Sensitive data paths: [...]

## Findings

### [SEVERITY] [Title]
- **Category**: [one of the categories above]
- **Confidence**: Confirmed | Probable | Potential
- **Location**: `path/file.ext:line`
- **Attack Path**: [source -> validation gap -> sink]
- **Why It Matters**: [practical attacker impact]
- **Evidence**:
  ```code
  [minimal relevant snippet]
  ```
- **Quick Fix**:
  ```code
  [minimal patch]
  ```
- **Durable Fix**: [architecture/process/test improvements]
- **Validation**: [specific checks/tests to confirm remediation]

---

## Prioritized Remediation Plan
1. Immediate (0-48h): [critical/high confirmed]
2. Sprint (1-2 weeks): [high/medium]
3. Backlog hardening: [low and long-term controls]

## Security Tooling Recommendations
- [targeted SAST/dependency/secret scanning tools relevant to detected risks]
```

## Quality Bar

A scan is complete only when:

1. Findings are sorted by severity and confidence.
2. Each finding includes concrete evidence and reproducible remediation.
3. Uncertain items are explicitly labeled and not overstated.
4. High-risk areas (auth, data access, command/db execution, secrets, dependencies) are covered.
