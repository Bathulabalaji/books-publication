# Project agent instructions

This repository builds the Books Publication Platform. Read [PRD.md](./PRD.md) for product/security requirements and [PROJECT_PLAN.md](./PROJECT_PLAN.md) for the phase sequence and exit gates before making architectural changes.

## Delivery

- Deliver one end-to-end vertical slice at a time; each slice includes backend, frontend, persistence/integration as needed, and tests.
- Do not begin a later project phase while the current phase's exit criteria are unmet.
- Treat the PRD as the initial baseline, not a license to invent unresolved business policies. Call out decisions that block safe implementation.
- Prefer a modular monolith and explicit provider adapters. Do not add services or infrastructure without a measured need.

## Security and data handling

- Enforce authorization in API/service and data-query paths; UI hiding is not security. Deny by default and test cross-user, cross-role, and unassigned-resource access.
- Keep identity, MFA, session, payment, and order rules server-authoritative. Never trust browser totals, OAuth claims, payment redirects, or unsigned callbacks.
- Never store or log plaintext passwords, OTPs, MFA secrets, recovery codes, payment credentials, access tokens, or provider secrets.
- Validate uploads by content and size as well as metadata. Keep protected demo files private and use short-lived authorized delivery.
- Return purpose-specific data transfer objects; expose only data the requesting principal is allowed to see.
- Use migrations, transactional invariants, idempotency, secure secret management, and redacted structured logs.

## Engineering and validation

- Follow the repository's existing patterns and dependency manifests; do not introduce a framework or package without need.
- Add or update tests for behavior changes, especially authentication, authorization, payment, order transitions, and file access.
- Run the smallest relevant lint, type-check, test, or build command available; report validation not run and why.
- Keep API contracts, permission policy, state machines, and user-facing behavior documented when they change.
- Do not claim PDF DRM, carrier integration, compliance certification, or production readiness without evidence.
