---
name: books-publication-platform
description: "Use when planning or implementing the Books Publication Platform: React/FastAPI vertical slices, identity and MFA, ABAC, book catalog/media, PDF demos, Razorpay checkout, orders, fulfillment, tests, and phase gates."
---

# Books Publication Platform workflow

Use this workflow for feature implementation, architecture changes, test planning, or reviews in this product.

## Required context

1. Read the root [PRD](../../../PRD.md) and [project plan](../../../PROJECT_PLAN.md).
2. Identify the active phase and its exit gate. If no phase is identified, use the earliest incomplete phase.
3. Inspect the existing code and reuse its patterns. Do not assume a scaffold or vendor integration exists.
4. Surface unresolved product/security decisions that prevent a safe implementation; do not silently invent policy.

## Implementation procedure

1. Define the complete user journey and API contract for the slice.
2. Implement the API, persistence and authorization rules first or in coordination with the UI; always enforce access server-side.
3. Implement the React experience, including loading, empty, error, forbidden, and responsive/accessibility states.
4. Add focused backend and frontend tests, including negative permission and failure-path tests.
5. Run the smallest relevant checks and verify the feature end-to-end in a production-like configuration where available.
6. Update product/API/operations docs when behavior or a phase decision changes.
7. Report the work, tests and outcomes, remaining risks, and whether the phase exit gate is satisfied.

## Non-negotiable safeguards

- Default-deny ABAC; scope customer data to the owner and staff work to explicit grants/assignments.
- Treat the server as authoritative for identity, authorization, prices, payment state, and order transitions.
- Verify OIDC and payment/webhook evidence on the server; use idempotency for retryable operations.
- Protect credentials, OTP/MFA material, provider secrets, and payment data from persistence/logging.
- Validate uploads, keep demos private by default, and use bounded short-lived access.
- Do not start work from a later project phase while the current phase is incomplete.
