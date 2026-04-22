# Production Implementation Plan Framework

## Philosophy

We do not ship features. We ship reliable, secure, operable systems that deliver great experiences.

Every implementation plan is a blueprint for something that must survive real usage, real failures, real scale, and real humans. A production system is not just code that works. It is code that can be deployed safely, monitored clearly, maintained confidently, and extended without collapsing under its own weight.

Design is not separate from engineering. Reliability is not separate from delivery. Security is not separate from functionality. Performance is not separate from user experience.

The product is the sum of:
- how it looks
- how it behaves
- how it fails
- how it recovers
- how it scales
- how it is operated
- how confidently it can be changed

Break the development process into small, manageable, sequential steps that a code generation AI can execute safely. Each step must be concrete enough to implement in a single iteration, but aligned to the full end-to-end system vision.

---

## Core Mandate

Every plan must produce a system that is:

1. **Functional** — solves the intended user problem correctly
2. **Reliable** — handles failure gracefully and predictably
3. **Secure** — protects data, access, and trust boundaries
4. **Observable** — emits logs, metrics, traces, and health signals
5. **Testable** — verified at unit, integration, and system levels
6. **Deployable** — can move through environments safely and repeatedly
7. **Maintainable** — readable, modular, documented, and extensible
8. **Usable** — designed intentionally for human experience
9. **Performant** — responsive under realistic load
10. **Recoverable** — supports rollback, retry, backup, and incident response

---

## Planning Principles

1. **Start at the foundation.**  
   Establish architecture, environments, contracts, and operational standards first. Get the bones right.

2. **Design the whole before building the parts.**  
   Define system boundaries, core flows, data ownership, trust boundaries, and deployment model before implementation begins.

3. **Build in dependency order.**  
   Infrastructure, contracts, domain models, services, interfaces, integrations, and polish should unfold in logical sequence.

4. **Keep changes atomic.**  
   Each step should ideally modify no more than 10 files. Smaller changes improve reviewability, traceability, and recovery.

5. **Production readiness starts on day one.**  
   Security, observability, validation, error handling, configuration, and testing are not final-phase add-ons.

6. **Validate at every boundary.**  
   Validate inputs, outputs, schemas, permissions, states, and integration assumptions. Never trust a boundary implicitly.

7. **Test continuously, not eventually.**  
   Every phase should include verification that protects the existing system while enabling safe progress.

8. **Design from the start.**  
   The user experience is shaped by architecture as much as visuals. Latency, failure messages, retries, and empty states are design decisions.

9. **See the product constantly.**  
   For web projects, after every UI-affecting step, use Playwright to visually inspect the result immediately.

10. **Plan for failure explicitly.**  
    Every critical workflow should define failure modes, retries, user feedback, fallback behavior, and recovery paths.

11. **Prefer extensible systems over clever shortcuts.**  
    Use patterns that support future change, team growth, and operational clarity.

12. **Document decisions as you go.**  
    Record architecture choices, tradeoffs, assumptions, and operational notes throughout implementation.

---

## Required System Design Coverage

Every implementation plan must account for all relevant parts of the system, including:

- Product architecture
- Application architecture
- Domain modeling
- API and contract design
- Data storage and schema design
- Authentication and authorization
- Validation and error handling
- Background jobs and async workflows
- Caching strategy
- File/object storage where relevant
- Third-party integrations
- Secrets and configuration management
- Logging, metrics, tracing, and alerting
- CI/CD pipeline design
- Environment strategy (local, staging, production)
- Infrastructure and deployment model
- Performance considerations
- Accessibility and responsive behavior
- Analytics and product instrumentation
- Testing strategy
- Backup, rollback, and disaster recovery considerations
- Documentation and runbooks
- Final design audit and system hardening

---

## Step Format

Present the implementation plan using this exact structure. Each step must be self-contained and executable in a single iteration.

``````
# Implementation Plan

## Phase 0: System Definition

- [ ] Step 0.1: Define architecture and execution model
  - **Task**: Define the system architecture, major components, trust boundaries, deployment model, and primary user/system flows.
  - **Why**: Prevents local implementation decisions from creating global inconsistency.
  - **Deliverables**:
    - Architecture summary
    - Core flow definitions
    - System boundary notes
    - Key technical decisions
  - **Files**:
    - `docs/architecture.md`: High-level architecture and system boundaries
    - `docs/flows.md`: Primary user and system flows
  - **Dependencies**: None
  - **Design Consideration**: Clear system behavior produces clearer user experiences.
  - **Testing**: Validate that all major product flows are represented.
  - **UI Verification**: None
  - **Operational Readiness**: Identify critical services, dependencies, and failure-sensitive paths.
  - **User Instructions**: Review assumptions before implementation continues

## Phase 1: Foundation

- [ ] Step 1.1: Initialize project structure and engineering standards
  - **Task**: Set up repository structure, linting, formatting, type checking, environment config strategy, and base documentation.
  - **Why**: A production system needs consistency before velocity.
  - **Files**:
    - `README.md`: Setup and project overview
    - `.env.example`: Environment variable contract
    - `[lint config]`: Linting rules
    - `[formatter config]`: Formatting rules
    - `[type config]`: Type system configuration
    - `docs/contributing.md`: Development standards
  - **Dependencies**: Step 0.1
  - **Design Consideration**: Engineering consistency reduces downstream defects.
  - **Testing**: Lint, format, and type-check pass in CI and locally.
  - **UI Verification**: None
  - **Operational Readiness**: Ensure local setup is reproducible.
  - **User Instructions**: Populate local environment variables

- [ ] Step 1.2: Establish CI pipeline and quality gates
  - **Task**: Configure automated checks for linting, typing, tests, and build validation.
  - **Why**: Prevent broken code from entering the main branch.
  - **Files**:
    - `.github/workflows/ci.yml`: CI pipeline
    - `docs/ci-cd.md`: CI expectations
  - **Dependencies**: Step 1.1
  - **Design Consideration**: Faster feedback loops improve quality and confidence.
  - **Testing**: Open a sample pull request and verify pipeline execution.
  - **UI Verification**: None
  - **Operational Readiness**: CI becomes the first enforcement boundary.
  - **User Instructions**: Configure repository secrets if needed

## Phase 2: Contracts and Data Model

- [ ] Step 2.1: Define domain models and canonical data contracts
  - **Task**: Create the source-of-truth types, schemas, and interface contracts across the system.
  - **Why**: Shared contracts reduce integration drift and production defects.
  - **Files**:
    - `src/domain/*`: Domain models
    - `src/contracts/*`: Request/response/event schemas
    - `docs/data-model.md`: Entity definitions and relationships
  - **Dependencies**: Step 1.2
  - **Design Consideration**: Stable contracts create predictable user-facing behavior.
  - **Testing**: Schema validation tests and contract fixtures.
  - **UI Verification**: None
  - **Operational Readiness**: Explicit versioning strategy for contracts
  - **User Instructions**: None

- [ ] Step 2.2: Design persistence layer and migration strategy
  - **Task**: Define database schema, indexes, constraints, and migration flow.
  - **Why**: Data integrity is central to production reliability.
  - **Files**:
    - `db/schema.*`: Schema definitions
    - `db/migrations/*`: Migration files
    - `docs/database.md`: Storage decisions and migration policy
  - **Dependencies**: Step 2.1
  - **Design Consideration**: Good schema design improves product speed and resilience.
  - **Testing**: Migration up/down tests, seed validation, constraint verification.
  - **UI Verification**: None
  - **Operational Readiness**: Rollback-safe migration policy
  - **User Instructions**: Initialize local database

## Phase 3: Security and Access Control

- [ ] Step 3.1: Implement authentication, authorization, and session strategy
  - **Task**: Add identity, access control, session management, and role enforcement.
  - **Why**: Production systems must enforce trust boundaries explicitly.
  - **Files**:
    - `src/auth/*`: Auth flows
    - `src/lib/permissions/*`: Authorization rules
    - `docs/security.md`: Auth and access model
  - **Dependencies**: Step 2.2
  - **Design Consideration**: Secure access should feel seamless, not fragile.
  - **Testing**: Auth flow tests, unauthorized access tests, role matrix tests.
  - **UI Verification**: Verify login, logout, protected routes, and denied states.
  - **Operational Readiness**: Token expiry, session invalidation, secret rotation notes
  - **User Instructions**: Configure auth provider credentials

- [ ] Step 3.2: Add input validation, secrets handling, and security middleware
  - **Task**: Validate all external inputs, protect secrets, add rate limiting, headers, and request protections where applicable.
  - **Why**: Production systems fail at boundaries first.
  - **Files**:
    - `src/lib/validation/*`: Shared validators
    - `src/lib/security/*`: Security middleware
    - `docs/security-checklist.md`: Security controls checklist
  - **Dependencies**: Step 3.1
  - **Design Consideration**: Clear validation errors create trust; silent failures destroy it.
  - **Testing**: Invalid input tests, rate-limit tests, security regression checks.
  - **UI Verification**: Verify user-facing validation and error messaging.
  - **Operational Readiness**: Secret sourcing and rotation process documented
  - **User Instructions**: Store secrets outside the repo

## Phase 4: Core Application Services

- [ ] Step 4.1: Implement primary service layer and business workflows
  - **Task**: Build the core business logic with clean service boundaries and idempotent operations where needed.
  - **Why**: Business logic must be correct, isolated, and testable.
  - **Files**:
    - `src/services/*`: Core workflows
    - `src/repositories/*`: Data access layer
  - **Dependencies**: Step 3.2
  - **Design Consideration**: Reliable workflows create a calm user experience.
  - **Testing**: Unit and integration tests for all major workflows.
  - **UI Verification**: None unless visible behavior changes
  - **Operational Readiness**: Idempotency, retries, and state-transition safeguards documented
  - **User Instructions**: None

- [ ] Step 4.2: Implement API or backend interface layer
  - **Task**: Expose application capabilities through stable endpoints or interfaces with validation and structured errors.
  - **Why**: Interface consistency is essential for frontend and integration reliability.
  - **Files**:
    - `src/api/*` or equivalent: Route handlers/controllers
    - `docs/api.md`: Endpoint definitions, contracts, and errors
  - **Dependencies**: Step 4.1
  - **Design Consideration**: Good APIs produce fast, predictable interfaces and fewer edge-case bugs.
  - **Testing**: Endpoint integration tests, contract tests, error response tests.
  - **UI Verification**: Validate UI behavior against real API responses if applicable.
  - **Operational Readiness**: Versioning and deprecation notes
  - **User Instructions**: None

## Phase 5: Frontend and Experience Layer

- [ ] Step 5.1: Build application shell, navigation, layout system, and design primitives
  - **Task**: Create the foundational UI structure, component primitives, design tokens, and responsive layout rules.
  - **Why**: A coherent UI system prevents design drift and speeds future development.
  - **Files**:
    - `src/components/ui/*`: Core primitives
    - `src/app/layout/*`: Shell and navigation
    - `docs/design-system.md`: Tokens and usage rules
  - **Dependencies**: Step 4.2
  - **Design Consideration**: The shell defines the emotional tone of the product.
  - **Testing**: Component tests and responsive verification.
  - **UI Verification**: Capture layout across desktop, tablet, and mobile.
  - **Operational Readiness**: Accessibility baseline established
  - **User Instructions**: None

- [ ] Step 5.2: Implement core user flows end-to-end
  - **Task**: Build the main product workflows from interface to backend integration.
  - **Why**: This is where the system becomes a usable product.
  - **Files**:
    - `src/features/*`: End-to-end product flows
    - `src/hooks/*` or equivalent: Data orchestration and client logic
  - **Dependencies**: Step 5.1
  - **Design Consideration**: Great workflows feel obvious, fast, and forgiving.
  - **Testing**: End-to-end tests for the highest-value user journeys.
  - **UI Verification**: Capture default, loading, success, empty, and error states.
  - **Operational Readiness**: Client error reporting and retry patterns added
  - **User Instructions**: None

- [ ] Step 5.3: Add accessibility, motion, and interaction refinement
  - **Task**: Improve keyboard support, focus states, semantics, transitions, feedback states, and responsiveness.
  - **Why**: Production quality is defined by the edges, not the happy path alone.
  - **Files**:
    - Relevant UI and style files
  - **Dependencies**: Step 5.2
  - **Design Consideration**: Polished interaction reduces friction and increases trust.
  - **Testing**: Accessibility checks, keyboard navigation tests, responsive audits.
  - **UI Verification**: Capture hover, focus, disabled, and interactive states.
  - **Operational Readiness**: None
  - **User Instructions**: None

## Phase 6: Background Workflows and Integrations

- [ ] Step 6.1: Implement async jobs, queues, webhooks, and external integrations
  - **Task**: Build background processing, retries, dead-letter handling, webhook verification, and provider abstractions.
  - **Why**: External systems and async workflows are common production failure points.
  - **Files**:
    - `src/jobs/*`
    - `src/integrations/*`
    - `docs/integrations.md`
  - **Dependencies**: Step 4.2
  - **Design Consideration**: Users should understand system progress without seeing system complexity.
  - **Testing**: Mocked integration tests, retry tests, webhook signature tests, failure simulations.
  - **UI Verification**: Verify visible pending/processing/completed states where applicable.
  - **Operational Readiness**: Retry policy, timeout policy, dead-letter strategy documented
  - **User Instructions**: Configure provider credentials and callback URLs

## Phase 7: Observability and Operational Safety

- [ ] Step 7.1: Add structured logging, metrics, tracing, and health endpoints
  - **Task**: Instrument the system to expose actionable operational telemetry.
  - **Why**: If you cannot observe the system, you cannot operate it.
  - **Files**:
    - `src/lib/observability/*`
    - `src/api/health/*` or equivalent
    - `docs/observability.md`
  - **Dependencies**: Step 6.1
  - **Design Consideration**: Faster diagnosis means less user pain during incidents.
  - **Testing**: Verify logs, health endpoints, and instrumentation wiring.
  - **UI Verification**: None
  - **Operational Readiness**: Define key service-level indicators and critical alerts
  - **User Instructions**: Connect telemetry providers

- [ ] Step 7.2: Add analytics and product instrumentation
  - **Task**: Instrument meaningful product events, funnel stages, and critical user actions.
  - **Why**: Production systems should be measurable both technically and product-wise.
  - **Files**:
    - `src/lib/analytics/*`
    - `docs/analytics.md`
  - **Dependencies**: Step 5.2
  - **Design Consideration**: Measure real behavior, not assumptions.
  - **Testing**: Verify event payloads and trigger points.
  - **UI Verification**: Confirm event-triggering interactions.
  - **Operational Readiness**: Event naming conventions documented
  - **User Instructions**: Configure analytics keys if needed

## Phase 8: Performance, Hardening, and Failure Readiness

- [ ] Step 8.1: Optimize critical paths and establish performance budgets
  - **Task**: Identify slow paths, optimize rendering/query behavior, and define performance targets.
  - **Why**: Performance is a feature users feel instantly.
  - **Files**:
    - Relevant service, query, cache, and UI files
    - `docs/performance.md`
  - **Dependencies**: Step 7.1
  - **Design Consideration**: Speed improves clarity, confidence, and delight.
  - **Testing**: Load tests, latency benchmarks, bundle analysis, query analysis.
  - **UI Verification**: Verify perceived performance in loading and transition states.
  - **Operational Readiness**: Performance thresholds documented
  - **User Instructions**: None

- [ ] Step 8.2: Add caching, retry, timeout, and degradation strategies
  - **Task**: Implement safe caching, bounded retries, timeouts, and graceful degraded behavior for non-critical dependencies.
  - **Why**: Production systems must keep working even when parts fail.
  - **Files**:
    - Relevant infrastructure and service files
    - `docs/resilience.md`
  - **Dependencies**: Step 8.1
  - **Design Consideration**: Graceful degradation is part of the user experience.
  - **Testing**: Failure injection tests, timeout tests, dependency outage simulations.
  - **UI Verification**: Verify fallback states and recovery messaging.
  - **Operational Readiness**: Circuit breaking and cache invalidation guidance documented
  - **User Instructions**: None

## Phase 9: Release Engineering and Environments

- [ ] Step 9.1: Prepare staging and production deployment workflows
  - **Task**: Configure environment-specific deployment pipelines, secrets injection, migrations, and promotion rules.
  - **Why**: Production delivery must be repeatable and safe.
  - **Files**:
    - Deployment configs
    - Infrastructure manifests
    - `docs/deployment.md`
  - **Dependencies**: Step 8.2
  - **Design Consideration**: Stable releases prevent user-facing instability.
  - **Testing**: Deploy to staging, run smoke tests, verify environment health.
  - **UI Verification**: Validate staging visually after deployment.
  - **Operational Readiness**: Deployment checklist and release gate criteria defined
  - **User Instructions**: Configure production environment secrets and domains

- [ ] Step 9.2: Add rollback, backup, and recovery procedures
  - **Task**: Document and validate rollback paths, data backup procedures, and incident recovery steps.
  - **Why**: Production readiness includes recovery, not just release.
  - **Files**:
    - `docs/runbooks/release-rollback.md`
    - `docs/runbooks/incident-response.md`
    - `docs/runbooks/backup-recovery.md`
  - **Dependencies**: Step 9.1
  - **Design Consideration**: Recovery speed directly affects user trust.
  - **Testing**: Perform rollback rehearsal and backup restoration verification where possible.
  - **UI Verification**: None
  - **Operational Readiness**: Incident handling baseline established
  - **User Instructions**: Store runbooks in an accessible operational location

## Phase 10: Final System Review and Design Audit

The final phase. Non-negotiable.

- [ ] Step 10.1: End-to-end system verification
  - **Task**: Execute full-system validation across primary workflows, edge cases, permissions, failures, and recovery paths.
  - **Why**: The system must work as a whole, not just in isolated pieces.
  - **Coverage**:
    - Happy paths
    - Edge cases
    - Auth and permission boundaries
    - Validation failures
    - Partial system failures
    - Retry and recovery behavior
    - Deployment smoke checks
  - **Testing**: Run full regression suite and manual system walkthrough.
  - **UI Verification**: Verify all visible states tied to tested workflows.
  - **Operational Readiness**: Confirm alerts, dashboards, and health checks are live

- [ ] Step 10.2: Visual audit with Playwright
  - **Task**: Systematically navigate every route and capture every relevant UI state.
  - **Why**: See the product as users will see it.
  - **Playwright Scope**:
    - Screenshot every page at desktop, tablet, and mobile sizes
    - Capture hover, focus, active, disabled, loading, empty, error, and success states
    - Verify layout consistency, spacing, readability, and motion
    - Inspect accessibility-critical interactions and keyboard states
  - **Review Each Screenshot**: Does this meet the product standard?

- [ ] Step 10.3: Design refinement and polish pass
  - **Task**: Fix all visual and interaction issues identified during the audit.
  - **Why**: Details define perceived quality.
  - **Scope**:
    - Typography
    - Spacing
    - Alignment
    - Contrast
    - Motion
    - Feedback
    - Empty states
    - Error clarity
    - Consistency
  - **Standard**: Would this feel credible to a real user on first contact?

- [ ] Step 10.4: Production readiness review
  - **Task**: Review the complete system against launch criteria before release.
  - **Why**: A system is not production-ready because coding is complete.
  - **Checklist**:
    - Security controls in place
    - Observability functioning
    - CI/CD healthy
    - Documentation complete
    - Runbooks present
    - Performance acceptable
    - Rollback tested
    - Critical flows verified
    - Known risks documented
  - **Outcome**: Explicit go/no-go decision
``````

---

## Rules for Plan Generation

When generating the implementation plan:

1. Break complex capabilities into multiple sequential steps.
2. Put shared foundations before feature-specific work.
3. Identify dependencies clearly and never violate them.
4. Include error handling and edge cases in relevant steps.
5. Include data validation at every system boundary.
6. Include observability for any critical service or workflow.
7. Include security for any auth, data, or external integration path.
8. Include CI/CD and environment readiness before calling something production-ready.
9. Include rollback and recovery planning before launch.
10. Keep each step small enough for one implementation iteration.
11. Prefer concrete file-level change scopes.
12. For web work, require Playwright UI verification after every UI-affecting step.
13. Do not label the target as an MVP unless explicitly requested.
14. Build for extensibility, maintainability, and operational clarity.
15. Assume the result must support real users, real failures, and future change.

---

## Additional Requirements for Production-Ready Plans

Every generated plan should also:

- Identify core system components and responsibilities
- Define where business logic lives
- Define where validation lives
- Define where permissions are enforced
- Define how configuration is loaded safely
- Define how errors are normalized and surfaced
- Define how telemetry is emitted
- Define how deployments are validated
- Define how failures are investigated
- Define how the team can safely extend the system later

If relevant, explicitly include:

- schema versioning
- API versioning
- feature flags
- audit logging
- admin tooling
- rate limiting
- queue durability
- idempotency keys
- concurrency control
- multi-environment config separation
- object storage lifecycle rules
- cron or scheduled tasks
- data retention policy
- privacy and compliance considerations
- localization and timezone handling
- mobile responsiveness
- accessibility compliance

---

## Final Output Requirements

Output the complete implementation plan in markdown, wrapped in six backticks for easy copying.

After the plan, provide a brief summary covering:
- Overall implementation strategy
- Key architectural decisions
- System foundations established first
- Critical delivery path
- Reliability and security approach
- Deployment and operational readiness strategy
- Design principles guiding the build

---

## Final Reflection

Take a breath. Step back from the code.

You are no longer the engineer who built this. You are now the operator, the reviewer, the user, and the future teammate who inherits the system.

Look at the product from all four angles:

- As a user: is it clear, fast, and trustworthy?
- As an engineer: is it clean, modular, and understandable?
- As an operator: is it observable, diagnosable, and recoverable?
- As a business: is it stable, extensible, and ready to grow?

Do not stop at "it works."

Ask instead:

- Will this survive production?
- Will this be easy to change safely?
- Will failures be visible and understandable?
- Will users feel confidence when using it?
- Would we be proud to put our name on it?

Refine until the answer is yes.

Make it dependable.  
Make it elegant.  
Make it worthy of real use.
