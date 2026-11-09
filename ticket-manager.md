# PUSTORA Ticket Manager

## Purpose and operating rules

This is the Phase 0 implementation backlog for the PUSTORA books platform. The project began with product and agent guidance only; P0-02 now defines the workspace boundaries and reproducible package manifests, while application entry points remain in P0-03 and P0-04.

Work tickets in dependency order, but deliver Phase 0 as one integrated, runnable foundation. Do not start identity, catalog, checkout, inventory workflows, notifications, or other Phase 1+ product features here. Phase 0 may establish contracts, safe configuration, health/readiness, policy definitions, and migration/test infrastructure for those later slices.

- **One ticket = one reviewable outcome.** Split a ticket if its acceptance criteria cannot be demonstrated in one review.
- **Every implementation ticket includes backend, frontend, and/or database impact tags.** Tags are lowercase: `frontend`, `backend`, `db`. Multiple tags are allowed.
- **Definition of done:** acceptance criteria pass; relevant tests/checks pass; API/schema/design contracts and setup docs are updated; no secrets are committed; the reviewer can reproduce the result.
- **Dependencies:** finish listed prerequisite tickets first. A dependency is not implied by ticket order.
- **Status:** all tickets begin as `Proposed`; update this field as work starts and completes.
- **No invented launch commitments:** where PRD assumptions need tax, legal, hosting, or vendor validation, capture an owner and decision evidence. Do not block a local scaffold on a production vendor choice.
- **Architecture bias:** reusable modular monolith, explicit contracts, replaceable provider adapters, PostgreSQL as business source of truth, and no speculative microservices or marketplace implementation.

## Phase 0 epic

**Epic:** P0 — Product decisions and delivery foundation  
**Goal:** A new developer can configure and run the React and FastAPI applications locally, apply the database migration baseline, use documented API contracts, and run tests/CI. The foundation has accessible frontend primitives, secure configuration conventions, basic observability, and tested permission/state contracts.

**Exit gate:** Fresh setup works; frontend, backend, and database checks pass; migrations apply to an empty database; health/readiness are observable; permission and state-machine contracts have owners and tests; no secrets are committed; production-critical legal/vendor/budget decisions have accountable owners and evidence or are explicitly launch-blocking.

---

## P0-01 — Resolve and track Phase 0 product decisions

**Status:** Proposed  
**Priority:** P0 — Required for phase gate  
**Tags:** `frontend`, `backend`, `db`

### Description

Maintain the canonical engineering decision register in Section 13 of [PRD.md](./PRD.md), using IDs DR-01 through DR-13. It must define the confirmed product direction and remaining validation for GST-exclusive prices, shipping tiers, the 5% GST assumption, inventory/payment reservation, low-stock behavior, role grants, order/payment/return states, provider adapters, India hosting constraints, performance/recovery objectives, support operations, accessibility, privacy, and retention.

Distinguish product defaults from items requiring external validation. In particular, do not claim a GST rate, invoice format, consumer return policy, data residency, provider free tier, service-level objective, or recovery objective is compliant/available until verified. Identify a decision owner, reviewer, target decision date, status, and evidence/source for each open item.

### Expected output

- PRD contains the canonical decision register with a status, accountable owner role, reviewer, target decision date, evidence/source, and production gate for each decision.
- Project plan and tickets reference decision IDs rather than maintaining competing copies of adjustable business values.
- Engineering contracts use one consistent interpretation of the current shipping, tax-display, inventory, role, and state assumptions.
- Production blockers have a named owner and a clear approval gate.

### Acceptance criteria

- GST-exclusive display and exact shipping thresholds are written once as the source of truth and referenced consistently.
- Tax, invoice, consumer policy, privacy/retention, hosting region, provider pricing/quotas, support ownership, budget, SLO, RPO, and RTO are clearly marked confirmed, proposed, or open validation; unverified items include an accountable owner role, reviewer, proposed target date, evidence requirement, and affected production gate.
- Proposed target dates are explicitly unapproved until a person is assigned to each owner role and the project sponsor confirms the schedule.
- The permission matrix is represented as data suitable for implementation and review; explicit grants and limited support access are unambiguous.
- Reservation/payment timeout, late-payment, cancellation, refund, and order states have no contradictory definitions across the PRD and project plan.
- No production-sensitive decision is silently converted into a legal or vendor guarantee.

**Dependencies:** None.

---

## P0-02 — Define modular application boundaries and workspace structure

**Status:** Complete — 2026-11-10
**Priority:** P0 — Foundation  
**Tags:** `frontend`, `backend`, `db`

### Description

Design a simple, maintainable workspace for a React/TypeScript frontend, FastAPI backend, PostgreSQL migrations, and shared API contract artifacts. Keep the system a modular monolith with clear domain ownership and test boundaries. Choose repository/package tooling only after checking current supported tooling and compatibility; do not introduce a monorepo framework or extra services without a demonstrated need.

Define where shared types are generated or consumed, how frontend/backend development commands work, how configuration differs across local/test/staging/production, and how migrations are run. Keep product-domain modules easy to add without creating empty speculative microservices.

### Expected output

- Written workspace/module layout and dependency direction.
- Runnable frontend and backend package manifests with pinned/reproducible dependency management appropriate to the chosen tools.
- Documented developer commands and naming conventions.

### Acceptance criteria

- Frontend, backend, and migration/test assets have clear locations and do not have cyclic or unclear ownership.
- A module can add a domain feature without importing UI code into the API or infrastructure-specific code into domain rules.
- Local development and CI use the same supported scripts/commands.
- Dependency/tool choices and material trade-offs are recorded; unused speculative components are excluded.

**Dependencies:** P0-01.

**Implementation:** [ARCHITECTURE.md](./ARCHITECTURE.md) documents workspace boundaries, dependency direction, API schema ownership, configuration, migration/test locations, and tool choices. The root npm workspace contains `apps/web`; `apps/api` is a separately locked Python package managed with `uv`. P0-03/P0-04 add the app entry points that make the declared run/build scripts executable; contract export and CI drift checks remain in their dedicated tickets.

---

## P0-03 — Bootstrap React and TypeScript application

**Status:** Complete — 2026-11-10  
**Priority:** P0 — Foundation  
**Tags:** `frontend`

### Description

Create the minimal React/TypeScript application entry point, routing foundation, environment-aware configuration, and production build. Establish a responsive global shell without implementing later-phase login, catalog, checkout, or staff workflows.

### Expected output

- Frontend starts locally and produces a deployable static/build artifact.
- A minimal landing/shell route with PUSTORA identity and a not-found route.
- Documented frontend development, build, and test commands.

### Acceptance criteria

- Type-check and production build pass from a clean dependency install.
- Environment-specific API base configuration is validated and contains no credentials.
- Routes have loading/error/not-found extension points without hardcoding role-specific product behavior.
- No backend secrets or privileged configuration are bundled into frontend assets.
- Layout adapts to narrow and wide viewports and has semantic landmarks.

**Dependencies:** P0-02.

**Implementation:** Created the Vite/React/TypeScript application in `apps/web` with React Router, a responsive PUSTORA landing shell, home/not-found routes, safe route-error and loading fallbacks, and eagerly validated public API-origin configuration. Added a public-only `.env.example`, frontend README, and focused route/config tests. Shared commands are `npm run web:dev`, `npm run web:typecheck`, `npm run web:test`, and `npm run web:build`.

---

## P0-04 — Bootstrap FastAPI application and API conventions

**Status:** Complete — 2026-11-10  
**Priority:** P0 — Foundation  
**Tags:** `backend`

### Description

Create the FastAPI application factory/entry point, versioned API namespace, configuration loading, request validation, and consistent error response conventions. Keep application startup testable and separate domain/application composition from route modules. Do not implement product endpoints from later phases.

### Expected output

- FastAPI service starts locally with a versioned API route namespace.
- Standard validation and application-error response shape is documented.
- Application construction can be exercised in tests without production secrets.

### Acceptance criteria

- App can start in a test environment with explicit test configuration.
- Validation errors and expected application errors have stable, non-sensitive response shapes.
- Unexpected errors are logged with a correlation identifier and return no stack trace or secret-bearing details to clients.
- API versioning and OpenAPI metadata are configured consistently.
- No authentication, catalog, payment, or order business endpoints are stubbed as success-shaped placeholders.

**Dependencies:** P0-02.

**Implementation:** Added the `create_app` factory and Uvicorn entry points, validated environment-backed settings, a `/api/v1/health` system route, UUID request correlation, stable validation/application/HTTP error envelopes, and unexpected-error handling that returns a generic 500 while logging only the request ID, method, route template, and exception class. OpenAPI, API conventions, and local setup are documented. Tests explicitly construct the app with test settings and do not require production secrets or infrastructure.

---

## P0-05 — Establish PostgreSQL connectivity and migration baseline

**Status:** Proposed  
**Priority:** P0 — Foundation  
**Tags:** `backend`, `db`

### Description

Set up the PostgreSQL driver/session lifecycle and a migration tool appropriate to the backend stack. Define how migrations are created, reviewed, applied, and checked in CI. Phase 0 should prove an empty database can be initialized; do not prematurely create all future product tables before their vertical slices.

### Expected output

- Configurable PostgreSQL connection for local/test environments.
- Versioned migration baseline and documented migration commands.
- Database health/readiness integration that does not expose credentials.

### Acceptance criteria

- A clean PostgreSQL database can be migrated to head and migration status can be checked.
- Migration execution is deterministic and is not triggered unexpectedly by importing application modules.
- Tests use isolated disposable/test databases and do not target production by default.
- Database sessions are correctly closed/rolled back on errors and are not shared across requests unsafely.
- No business schema is added without an accepted domain contract and phase scope.

**Dependencies:** P0-02, P0-04.

---

## P0-06 — Add validated configuration and secret-safe local defaults

**Status:** Proposed  
**Priority:** P0 — Security foundation  
**Tags:** `frontend`, `backend`, `db`

### Description

Define typed configuration for frontend API origin, backend runtime, PostgreSQL, Redis placeholder/connection conventions, logging, and future provider endpoints. Separate public configuration from server-only secrets. Add safe local examples and startup validation without committing real credentials.

### Expected output

- Typed environment/config schemas with clear required/optional settings.
- Safe example environment files and secret-management guidance.
- Startup errors that identify missing setting names without printing secret values.

### Acceptance criteria

- Invalid/missing required settings fail fast in the relevant environment.
- Frontend build-time configuration contains only public values.
- Backend secrets are loaded only server-side and are never logged or returned through health/config endpoints.
- Example files contain placeholders only; secret files are excluded from version control.
- Test configuration is explicit and cannot accidentally fall back to production credentials.

**Dependencies:** P0-03, P0-04, P0-05.

---

## P0-07 — Define and test authorization policy contract

**Status:** Proposed  
**Priority:** P0 — Security foundation  
**Tags:** `backend`, `db`

### Description

Represent the agreed role/capability matrix as a backend-owned policy definition with a deterministic decision interface. Include user identity, role/permission, resource ownership, order assignment, resource status, and requested action as policy inputs. Default to deny. For Phase 0, establish the policy contract and exhaustive test fixtures; persistence of user sessions and production role-administration flows belong to the identity phase.

### Expected output

- Versioned permission/capability definitions and role matrix matching the PRD.
- A pure policy decision interface that can be called from future route/service authorization.
- Automated table-driven allow/deny tests for every matrix entry and relevant attribute boundary.

### Acceptance criteria

- Super Admin, Admin, Catalog Manager, Order Manager, Fulfillment Staff, Support Agent, and Customer capabilities match the PRD matrix.
- Catalog Manager publishing requires an explicit grant; no implicit grant is introduced.
- Fulfillment Staff can update only assigned orders; assignment alone does not grant a role capability.
- Support access is limited to the active case and minimum necessary fields; cross-customer/unrelated record access is denied.
- Unlisted actions, missing principal/resource attributes, and invalid roles are denied by default.
- Tests include ownership, assignment, status/action mismatch, limited support scope, and every explicit “No” cell.
- No frontend-only permission check is treated as enforcement.

**Dependencies:** P0-01, P0-02.

---

## P0-08 — Specify shared domain and API contracts for future vertical slices

**Status:** Proposed  
**Priority:** P0 — Integration foundation  
**Tags:** `backend`, `db`, `frontend`

### Description

Document initial contracts for money/currency, UTC timestamps, pagination, error shapes, identifier format, API versioning, and state machines needed by checkout/order and inventory work. Treat this as a contract/design ticket, not implementation of checkout or inventory. Explicitly document where validation by tax/legal/operations is still needed.

### Expected output

- Contract document or schemas covering common API response/error conventions.
- Reviewed initial order/payment/fulfillment/return state transition diagrams or tables.
- Inventory reservation/ledger invariants and price/shipping/tax calculation inputs documented for later implementation.

### Acceptance criteria

- Money is represented without floating-point ambiguity and includes currency; launch currency is INR.
- Catalog price labeling and checkout total disclosure follow DR-01; shipping tier boundaries follow DR-01 and tax treatment follows DR-02.
- Shipping tier boundaries and tax display follow DR-01; tax calculation follows DR-02.
- Order price, shipping, tax, invoice template/version, and payment identifiers are understood as order-time snapshots where appropriate.
- State transitions identify actor/permission, idempotency behavior, and relevant failure/late-payment path.
- Inventory contract explains reservation, release, sold conversion, damage adjustment, and no-double-deduction/no-oversell invariants.
- Contracts mark unapproved tax, invoice, return, and provider assumptions as requiring review.

**Dependencies:** P0-01, P0-02.

---

## P0-09 — Publish and validate OpenAPI contract

**Status:** Proposed  
**Priority:** P0 — Integration foundation  
**Tags:** `frontend`, `backend`

### Description

Establish OpenAPI generation from the FastAPI service and a reproducible way for frontend developers and tests to validate against it. Avoid duplicating request/response types manually when a safe generation workflow is available. Keep only the Phase 0 endpoints in the contract.

### Expected output

- OpenAPI document generated or validated from the running app.
- Documented command to check contract changes.
- Frontend contract consumption/generation approach selected and recorded.

### Acceptance criteria

- OpenAPI is available in development/test and disabled or appropriately restricted in production per deployment policy.
- Contract generation/check is deterministic and fails CI on unintended drift.
- Error models and health endpoints are represented accurately.
- No future feature endpoint is represented as an implemented endpoint unless it exists.

**Dependencies:** P0-04, P0-08.

---

## P0-10 — Add frontend design tokens and accessible component baseline

**Status:** Proposed  
**Priority:** P0 — Frontend foundation  
**Tags:** `frontend`

### Description

Set up Tailwind CSS and shadcn/ui-compatible design foundations for PUSTORA: typography, color tokens, spacing, focus states, and a small set of reusable layout/form/button primitives. Establish WCAG 2.2 AA as the design target without building product flows.

### Expected output

- Theme tokens and reusable accessible primitives in the frontend.
- Responsive application shell demonstrating typography, focus, buttons, and form control states.
- Short component and accessibility usage guidance.

### Acceptance criteria

- Keyboard navigation and visible focus work throughout the shell.
- Components use semantic elements and accessible names/labels; ARIA is used only when native semantics are insufficient.
- Color pairs meet the project’s contrast target and are not the sole means of conveying state.
- Components render correctly at mobile and desktop widths and support reduced motion where applicable.
- Existing PUSTORA styling can be changed through tokens rather than one-off page overrides.

**Dependencies:** P0-03.

---

## P0-11 — Add shared frontend API client and UI state patterns

**Status:** Proposed  
**Priority:** P0 — Frontend integration foundation  
**Tags:** `frontend`

### Description

Create a small typed API client convention using the generated/validated backend contract. Define reusable loading, empty, error, retry, and forbidden-state patterns without implementing authentication or product endpoints. Make backend validation errors usable in accessible forms.

### Expected output

- Shared API client with configurable API base URL and typed error handling.
- Reusable accessible loading/error/empty/forbidden UI patterns.
- Test coverage using mocked API responses.

### Acceptance criteria

- Client handles network, non-JSON, validation, and server-error responses without treating failures as success.
- Error messages do not expose stack traces, secrets, or internal infrastructure detail.
- Retry is explicit and safe; mutations are not automatically retried without an idempotency contract.
- Error state is announced accessibly, and keyboard focus is managed appropriately.
- API client type checks against the published API contract.

**Dependencies:** P0-03, P0-09, P0-10.

---

## P0-12 — Implement health, readiness, and graceful failure behavior

**Status:** Proposed  
**Priority:** P0 — Operational foundation  
**Tags:** `backend`, `db`

### Description

Add separate liveness and readiness checks. Liveness reports that the process is running; readiness verifies required dependencies needed to serve requests (including PostgreSQL when configured), with bounded timeouts and safe responses. Redis may be optional in Phase 0 if no feature depends on it; report its state distinctly rather than making an unused optional service a false readiness blocker.

### Expected output

- Liveness/readiness endpoints and dependency status model.
- Frontend or operational smoke check for the service’s healthy/unavailable state.
- Tests for healthy, dependency-failure, and timeout behavior.

### Acceptance criteria

- Health endpoints do not reveal connection strings, credentials, exception text, or topology details.
- Dependency checks are bounded and do not create unbounded load.
- Liveness does not fail merely because a dependency is unavailable; readiness fails when a required dependency is unavailable.
- Optional dependencies are clearly distinguished from required dependencies.
- Startup and shutdown close resources cleanly.

**Dependencies:** P0-04, P0-05, P0-06.

---

## P0-13 — Add request correlation and safe observability hooks

**Status:** Proposed  
**Priority:** P0 — Operational/security foundation  
**Tags:** `backend`, `frontend`

### Description

Introduce structured, redacted request logging and request/correlation IDs across frontend-to-backend calls. Add basic metrics/error-tracking integration points behind configuration so vendors can be chosen later. Establish a denylist/redaction policy before logging request context.

### Expected output

- Structured server logs with correlation ID, route, status, and duration.
- Frontend request correlation propagation and user-safe error correlation display.
- Redaction rules and vendor-neutral metrics/error-reporting interfaces/configuration.

### Acceptance criteria

- Passwords, OTPs, cookies, authorization headers, refresh tokens, payment secrets, and request bodies containing sensitive data are not logged.
- Correlation IDs are validated/generated server-side and propagated to API responses.
- Logs do not include unnecessary PII; sampling and retention can be configured.
- Metrics hooks capture request count/latency/error count without high-cardinality user identifiers.
- Missing external monitoring credentials do not prevent safe local development; production startup policy is explicit.

**Dependencies:** P0-04, P0-06, P0-11.

---

## P0-14 — Create frontend, backend, and database test foundations

**Status:** Proposed  
**Priority:** P0 — Quality foundation  
**Tags:** `frontend`, `backend`, `db`

### Description

Select and configure test runners that fit the frontend/backend toolchains. Provide fast unit/component tests, API tests with dependency overrides, and database migration/integration checks against isolated test data. Create fixtures and patterns that make future authorization and transaction tests easy to add.

### Expected output

- Runnable frontend unit/component test command.
- Runnable backend unit/API test command.
- Migration smoke test against an isolated empty test database.
- Test data/fixture conventions that avoid shared mutable state.

### Acceptance criteria

- Tests run without production credentials or services.
- Database tests use a clearly isolated database and clean up deterministically.
- Tests cover app startup, validation/error responses, health/readiness, API contract, and accessible shell rendering.
- Permission-policy contract tests from P0-07 run in the default focused suite.
- Failing tests return non-zero and preserve diagnostic output without leaking test secrets.

**Dependencies:** P0-03, P0-04, P0-05, P0-07, P0-09, P0-10, P0-12.

---

## P0-15 — Establish continuous integration and quality gates

**Status:** Proposed  
**Priority:** P0 — Delivery foundation  
**Tags:** `frontend`, `backend`, `db`

### Description

Create CI checks for reproducible dependency installation, formatting/linting, frontend type-check/build, backend lint/type-check/tests, API contract drift, and database migration smoke tests. Use least-privilege CI permissions and avoid production secrets in pull-request jobs.

### Expected output

- CI workflow for frontend, backend, contract, and migration checks.
- Documented required checks and how contributors run the same checks locally.
- Clear failure output tied to the failing check.

### Acceptance criteria

- CI runs on proposed changes and blocks merge when required checks fail.
- CI can run from a clean checkout without production credentials.
- No credentials are embedded in workflow files or logs.
- Dependency versions/lockfiles are reproducible and checked in where the chosen ecosystem expects them.
- CI duration and caching are reasonable for the selected toolchain; caches do not contain secrets.
- No deployment or production data mutation is part of Phase 0 CI.

**Dependencies:** P0-02, P0-03, P0-04, P0-05, P0-09, P0-14.

---

## P0-16 — Document local setup, architecture, and operations baseline

**Status:** Proposed  
**Priority:** P0 — Handoff foundation  
**Tags:** `frontend`, `backend`, `db`

### Description

Document how to install prerequisites, configure local environment, start frontend/backend/database, run migrations, execute tests, inspect health, and troubleshoot common setup failures. Record architecture decisions and explicitly identify future services/providers as planned rather than already integrated.

### Expected output

- Concise local development guide.
- Architecture/module boundary note and decision log references.
- Database migration, test, and troubleshooting instructions.

### Acceptance criteria

- A developer without prior workspace state can follow the guide from a clean checkout.
- Commands match current manifests and CI rather than being aspirational.
- Required tools/versions are stated; optional services are clearly marked.
- Environment examples contain placeholders only.
- No unsupported claims about production deployment, vendor availability, legal compliance, or free-tier eligibility.

**Dependencies:** P0-02 through P0-15 as applicable; final acceptance is after CI exists.

---

## P0-17 — Demonstrate integrated Phase 0 gate

**Status:** Proposed  
**Priority:** P0 — Phase exit  
**Tags:** `frontend`, `backend`, `db`

### Description

Run the complete foundation from a clean environment and produce evidence for every Phase 0 exit criterion. Fix integration defects in Phase 0 tickets rather than starting Phase 1 work. Review unresolved decisions and confirm accountable owners.

### Expected output

- Clean-start validation record covering frontend, API, database migration, health/readiness, tests, and CI.
- Reviewed permission/state contracts and outstanding decision owners.
- Phase 0 demo showing frontend shell calling the local versioned API and graceful dependency failure.

### Acceptance criteria

- Fresh setup instructions work on a clean environment.
- Frontend and backend start locally; health/readiness accurately reflect dependency state.
- Empty database migrates to head; migration smoke tests pass.
- Lint/format, type-check, tests, build, and contract checks pass in CI.
- Permission matrix and state-machine contracts have deterministic tests.
- No secrets are committed or exposed in logs, browser bundles, health responses, or CI artifacts.
- Production-critical unresolved legal, provider, hosting, support, and budget decisions have owners and launch gates.
- Product features from Phase 1 or later have not been presented as complete.

**Dependencies:** P0-01 through P0-16.

---

## Suggested execution order

1. P0-01 product decisions and P0-02 architecture/workspace layout.
2. P0-03 frontend bootstrap and P0-04 backend bootstrap.
3. P0-05 database/migrations and P0-06 configuration/secrets.
4. P0-07 authorization contract and P0-08 domain/API contracts.
5. P0-09 OpenAPI; then P0-10 design/accessibility baseline and P0-11 API client.
6. P0-12 health/readiness and P0-13 observability.
7. P0-14 test foundations and P0-15 CI quality gates.
8. P0-16 setup documentation, followed by P0-17 clean-start phase gate.

Independent frontend and backend work may proceed in parallel after P0-02, but integration contracts and the database migration baseline must be agreed before cross-app integration.

## Out of scope for this Phase 0 backlog

- Login/signup, Google OIDC callbacks, OTP delivery, MFA enrollment, sessions, and password recovery.
- Product/catalog/content management, media upload, and demo PDF delivery.
- Cart, checkout, Razorpay payments, invoices, and live inventory reservation.
- Customer order history, staff fulfillment workflows, notifications, and support case product UI.
- Production hosting/vendor provisioning, live provider credentials, and production spend commitments.

These features belong to later end-to-end phases in [PROJECT_PLAN.md](./PROJECT_PLAN.md) and must not be partially implemented as Phase 0 placeholders.
