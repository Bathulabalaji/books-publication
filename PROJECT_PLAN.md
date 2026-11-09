# PUSTORA — Step-by-Step Project Plan

## Delivery rule

Work in sequential, integrated vertical slices. Every phase includes backend, frontend, persistence/integration where relevant, and automated tests. A phase is not complete when one side is done: it exits only after the end-to-end acceptance checks pass in a production-like environment and the docs/runbook are updated. Do not start the next phase while the current phase has a blocker.

Use a modular monolith initially: React/TypeScript web client, FastAPI API, managed PostgreSQL, Redis, and one background worker. Use S3-compatible object storage, an India-capable CDN, error tracking, metrics, and logs. Keep provider adapters explicit. The launch market is India, currency INR, brand PUSTORA, domain pustora.in; hosting region is India subject to vendor and legal review. Future marketplace support is a later product phase, not part of this single-publisher launch.

## Phase 0 — Product decisions and delivery foundation

**Outcome:** A runnable, observable, testable skeleton with agreed MVP decisions.

**Ticket backlog:** See [ticket-manager.md](./ticket-manager.md) for Phase 0 ticket IDs, dependencies, expected outputs, and acceptance criteria. Complete its exit-gate ticket before starting Phase 1.

- Use the PRD decision register (DR-01–DR-13) as the single source of truth for launch assumptions, validation status, accountable owner, reviewer, proposed/confirmed target date, evidence, and production gates. Proposed dates are not commitments; assign the accountable roles to people and approve dates at kickoff.
- Implement the attached permission matrix as the initial server-side ABAC policy and test every role/capability pair, including limited support views and assignment-scoped fulfillment.
- Define domain boundaries, API error conventions, order/payment/inventory state machines, design tokens, and environments.
- Workspace boundaries, dependency direction, API contract ownership, and package tooling are documented in [ARCHITECTURE.md](./ARCHITECTURE.md); the root npm workspace contains the web app, while the FastAPI package is independently locked with `uv`.
- Define the initial role bundles (Super Admin, Admin, Catalog Manager, Order Manager, Fulfillment Staff, Support Agent, Customer), default-deny ABAC policy, staff assignment rules, audit requirements, and privileged-role step-up MFA.
- Implement provider adapter behavior from DR-08 with local/sandbox delivery for development and verified fallback/deduplication semantics. Use free tiers/credits only when eligible; do not make production reliability depend on no-cost quotas.
- Evaluate Razorpay, object storage/CDN, monitoring, and India-region capabilities/pricing as part of the relevant launch validation; do not provision live credentials in Phase 0.
- Record the PRD Section 11 planning load bands and derive test profiles rather than treating them as SLAs.
- Validate the proposed load/SLO/recovery targets in DR-10 against measured load and chosen vendors. Set an approved monthly spend budget and the DR-10 alert thresholds before production.
- Resolve DR-11 through DR-13: assign support ownership, approve/publish proposed business hours and response targets, configure WhatsApp Business, and review contact-form privacy/retention/escalation handling.
- Complete accessibility, privacy, India consumer/tax/payment, security, and retention reviews with qualified specialists before production.
- Create React/TypeScript/Tailwind/shadcn and FastAPI application skeletons, PostgreSQL migrations, Redis connection conventions, health endpoints, config validation, and CI.
- Establish typed API contract generation or equivalent contract checks; add lint, format, type-check, unit, integration, and frontend test runners.
- Add structured redacted logging, request IDs, metrics hooks, secret handling, and safe local development settings.
- **Frontend:** P0-03 establishes a responsive React/Tailwind shell, keyboard skip link, semantic landmarks, home/not-found routes, and route loading/error fallbacks. Public API-origin config is validated at bootstrap; frontend checks run through shared npm scripts.
- **Backend:** P0-04 provides a testable FastAPI factory, validated `PUSTORA_` settings, `/api/v1` system-health route, server-generated request IDs, normalized validation/application/HTTP errors, and redacted unexpected-error logging. Database session/migration setup remains in P0-05.
- **Tests:** CI smoke test; P0-04 API factory, versioned health/OpenAPI, settings, validation, expected/unexpected errors and correlation; DB migration smoke; frontend shell tests.

**Exit gate:** Fresh setup instructions work; CI passes; migrations apply to an empty DB; both apps run locally; no secrets are committed; the permission matrix and state transitions have owners and tests; production-critical legal/vendor/budget decisions have accountable owners and dates.

## Phase 1 — Identity, sessions, MFA, and authorization foundation

**Outcome:** Users can safely register/sign in and the app/API consistently enforce identity and permissions.

- Implement only email/password, Google OIDC, and phone OTP through provider adapters. Use Argon2id for passwords; verify identifiers; handle safe account linking, rate limits, login monitoring, session management, recovery, and account enumeration defenses.
- Implement HttpOnly/Secure/SameSite cookies, CSRF defenses, refresh-token rotation/revocation, and one-time hashed recovery codes.
- Make customer MFA optional; require privileged-role step-up MFA and designated sensitive-action verification using a second independent supported factor: mobile OTP after email/password or Google sign-in, and password after mobile OTP sign-in. Do not grant privileged access without the independent factor or treat one phone OTP challenge as both primary authentication and a second factor.
- Implement OTP and transactional-email adapters using the selected providers and policies in DR-08; enforce the OTP security parameters defined in the PRD identity requirements. Use development sandboxes/local delivery; verify sender/domain, quotas, pricing, and eligibility before production.
- Implement explicit notification fallback semantics: fallback on definitive provider rejection/unavailability; on ambiguous timeout reconcile status first. Reuse the same active OTP challenge on fallback, and apply logical-notification idempotency to prevent duplicate email/SMS sends.
- Define principal attributes, permission bundles, role/assignment management model, default-deny policy evaluator, audit events, and purpose-specific response schemas.
- **Frontend:** Registration/login/provider flows, MFA setup/challenge/recovery, session/account security screens, accessible error handling, role-aware navigation and unauthorized/forbidden states.
- **Backend:** Identity/auth endpoints, secure session/token lifecycle, OIDC validation, OTP/MFA provider adapters, authorization dependencies/service checks, audit persistence, and staff/admin bootstrap policy.
- **Tests:** Unit and integration tests for credential/provider flows, optional customer versus mandatory privileged-role MFA, independent-factor enforcement for each login method, step-up verification and single-use recovery codes, account-linking, OTP expiry/replay/rate limits, session rotation/revocation, default deny, role/attribute boundaries, and sensitive response redaction.

**Exit gate:** Email/password, Google, and mobile OTP work in staging with sandbox providers; OTP policies and MFA requirements are enforced server-side; cross-account and cross-role tests prove denial; session recovery is operationally documented; no secrets or factors appear in logs.

## Phase 2 — Catalog, landing content, and admin publishing

**Outcome:** Visitors can browse real published books and authorized staff can manage the catalog and landing content.

- Define book, price, publication, inventory-ledger, media, banner, featured collection, testimonial, video feedback, review, and student-success-story models and migrations.
- Build public paginated catalog/detail APIs and admin CRUD APIs, with server-side authorization and validation.
- Add secure image/video upload workflow, metadata, ordering, alt text, limits, object storage/CDN adapter, and publication controls.
- **Frontend:** Landing page sections, catalog/search/filter/sort baseline, responsive product cards/detail shell, gallery, video, loading/empty/error states, and admin catalog/content screens. Only authorized admins can publish curated content.
- **Backend:** Catalog/content services and APIs, upload authorization, media metadata, public-only response models, pagination, audit events, storage adapter, and auditable stock adjustment operations.
- **Tests:** Public visibility and draft isolation, input/price validation, permissions for create/edit/publish, media type/size/auth checks, pagination, and API/component flows.

**Exit gate:** An authorized editor can create and publish a book with ordered media and adjust stock with actor/reason; a visitor sees only published content and correct prices; only authorized admins can publish featured/testimonial/review content; unauthorized users cannot mutate drafts; media is served through the approved storage path.

## Phase 3 — Demo book reader and protected sample delivery

**Outcome:** Readers can preview authorized sample material in a usable browser reader.

- Define sample-PDF limits, allowed page range/portion, access policy, retention, and acceptable anti-abuse controls; explicitly avoid claiming DRM.
- Implement PDF upload validation/scanning policy, private object storage, authorized short-lived delivery, and sample metadata.
- **Frontend:** “View demo book” CTA, accessible in-browser PDF reader, loading/failure states, page navigation, and responsive behavior.
- **Backend:** Sample upload/admin management, access-checked signed delivery or streaming endpoint, audit/security events, size/page limits, and cache policy.
- **Tests:** Correct sample access, unpublished/unauthorized denial, expired URL behavior, malformed/oversized file rejection, safe headers, and reader interaction.

**Exit gate:** A customer can view the intended sample; direct unauthorized access fails; the complete book is not accidentally exposed; upload and delivery limits are measured and documented.

## Phase 4 — Cart, checkout, Razorpay, and payment reconciliation

**Outcome:** A customer can place and securely pay for an order without trusting client totals or browser redirects.

- Finalize delivery address validation, order price snapshot, INR shipping tier calculation, GST treatment, inventory reservation TTL, order/payment state machine, idempotency strategy, and exception handling.
- Build cart and order-creation APIs with transactional consistency and authoritative server price calculation. Checkout requires authentication.
- Display catalog prices, GST, final payable amount, shipping, inventory, and payment expiry according to PRD decisions DR-01, DR-02, DR-04, and DR-05.
- Implement ledger-backed reservation, release, sold conversion, late-payment handling, and actor/reason-backed adjustments according to DR-04. Prevent overselling under concurrent checkout using transactional atomic updates/locking.
- Enforce the DR-05 no-backorder and low-stock rules server-side; exact display behavior follows the register.
- Implement invoice generation from immutable order and tax snapshots. Provide multiple invoice template options with admin selection and versioned templates; preserve the issued template version and invoice values. Obtain tax review for applicable GST, required fields, numbering, and final layouts before production.
- Apply cancellation, return, refund and state transitions according to DR-06. Enforce eligibility server-side; do not promise terms that remain subject to legal review.
- Integrate Razorpay sandbox first: server-created payment order, browser checkout, signature verification, verified webhook endpoint, durable event/idempotency handling, and reconciliation tooling.
- **Frontend:** Cart, quantity/removal, address and order summary with shipping/GST breakdown, Razorpay checkout handoff, pending/success/failure states, invoice template preview/selection for authorized admin, retry-safe UX, and support links.
- **Backend:** Cart/order/payment/invoice models and APIs, inventory ledger/reservation service, transaction boundaries, configurable shipping/tax calculation, invoice rendering/template versioning, gateway adapter, signature/webhook verification, asynchronous follow-up, and admin reconciliation view.
- **Tests:** Price tampering; GST-exclusive display and all DR-01 shipping boundaries; DR-02 tax calculation/rounding; duplicate cart/order submissions; concurrent stock reservation/no oversell; DR-04 reservation expiry/release and late payment with/without stock; DR-05 low-stock and no-backorder enforcement; payment success/failure/cancel; forged signature; invalid/duplicate/out-of-order webhook; DR-06 cancellation eligibility and return/refund state transitions; invoice snapshot/template versioning; refund bookkeeping; transactional rollback.

**Exit gate:** Sandbox purchases reconcile to exactly one correct order; forged or duplicate notifications cannot mark a payment paid twice; customer-facing totals match the server order snapshot; parallel checkout cannot oversell; expired/failed payments release reservations; invoices preserve their issued values/template; exception cases are visible to staff; tax and invoice decisions are approved before live payments. The cancellation and return policy is legally reviewed before launch.

## Phase 5 — Customer order history and staff fulfillment tracking

**Outcome:** Customers see their order timeline; staff can update only authorized orders with traceable events.

- Implement order history/detail APIs scoped to owner and staff permissions; establish legal status transitions and append-only tracking events.
- Implement assignment-aware staff queues and customer-safe status/location messages, actor/time recording, and admin correction audit flow.
- Integrate background notification processing with PostgreSQL delivery events for order confirmation, payment outcome, processing, dispatch, delivery, refund, and account-security events. Use provider choices/fallbacks from DR-08; keep marketing consent/unsubscribe separate.
- Add customer support entry points for support email, WhatsApp Business, and contact form, with restricted access to submissions and customer data.
- Implement the support operating model, hours, response targets, contact-form handling, and retention according to DR-11 through DR-13. Keep WhatsApp Business human-operated initially.
- **Frontend:** Customer orders list/detail/timeline, cancellation/refund status, accessible support links/contact form, and staff queue/order update screens; hide unavailable actions while handling server denials safely.
- **Backend:** Owner-scoped APIs, staff assignment/ABAC checks, status transition service, tracking event persistence, customer-safe DTOs, notification provider adapters/worker, durable delivery-event tracking, contact-form handling, and audit trail.
- **Tests:** Own-order access, IDOR/cross-customer denial, staff assigned/unassigned behavior, transition validity, cancellation policy by state, immutable history/correction, private-note redaction, notification retry/idempotency/consent separation, contact-form abuse controls, and concurrent updates.

**Exit gate:** A customer cannot retrieve another customer's order; a staff member cannot update out-of-scope orders; valid updates appear in the customer timeline with actor/time/location text; invalid transitions are rejected and audited; transactional messages are traceable without leaking secrets; support channels meet tested ownership, acknowledgement, escalation, privacy, and retention behavior.

## Phase 6 — Production readiness, security, accessibility, and launch

**Outcome:** The integrated storefront is supportable and safe to release to real customers.

- Complete end-to-end regression, dependency/security review, threat-model follow-ups, access review, and secrets/configuration review.
- Validate Google and DR-08 provider setup, Razorpay production configuration, webhook retries, inventory reconciliation, refund/support operations, backup/restore, data retention, and incident escalation.
- Add dashboards/alerts for availability, API errors/latency, auth abuse, webhook lag/reconciliation, queue failures, database capacity, provider quotas/delivery failures, and budget thresholds.
- Run WCAG 2.2 AA and responsive reviews, load tests against the agreed traffic bands, and recovery drills; tune measured bottlenecks. Validate keyboard-only navigation, labels/errors, contrast, screen-reader semantics, image alt text, captions/transcripts, and PDF alternatives where feasible.
- Run the campaign load profile and verify the proposed SLO/RPO/RTO targets in DR-10 against measured results and selected service tiers.
- Exercise support operations during and outside published business hours: contact acknowledgement, severity assignment, overdue escalation, WhatsApp Business handoff, retention/deletion, and privacy incident handling.
- **Frontend:** Complete keyboard/screen-reader/responsive review; production analytics with privacy controls; error/support guidance; release smoke tests.
- **Backend:** Harden deployment, database connection/pool limits, rate limits, worker retries/dead letters, backup/restore, observability, and rollout/rollback procedure.
- **Tests:** Full critical-path E2E, authorization matrix, security regression, accessibility, load/soak as sized, restore verification, and production smoke.

**Exit gate:** Owners sign off on launch checklist, support and incident runbooks, SLO/cost limits, privacy/legal/tax review, GST and invoice configuration, refund policy, and successful restore; critical security or payment issues are zero; rollback is tested.

## Phase governance

- Each phase begins with a short design/API contract review and ends with a demo plus evidence for every exit criterion.
- Keep a visible backlog; add new requirements to the PRD/backlog rather than expanding an in-flight slice without review.
- Use feature flags for risky rollout changes; never use flags as a substitute for authorization.
- Merge only with tests for changed behavior and the relevant frontend/backend checks green.
- Deploy to staging at each phase gate; do not expose incomplete payment, identity, or authorization behavior to production users.
- Record decisions, threat-model notes, API contracts, test strategy, and operational assumptions in repository docs as they become known.
- Revisit the single-publisher boundary when the growth/expansion band is approached. Start a separate marketplace phase with tenant isolation, publisher onboarding, publisher-scoped administration, commercial model, and migration strategy; do not infer marketplace readiness from publisher_id fields alone.
- Do not estimate calendar dates or cloud costs until team capacity, provider choice, traffic, media, and service-level assumptions are agreed.
