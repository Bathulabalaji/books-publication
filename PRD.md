# PUSTORA — Books Publication Platform PRD

**Status:** Initial product definition with launch defaults  
**Audience:** Product, design, engineering, operations, and future implementation agents  
**Brand:** PUSTORA  
**Business category:** Publishing & Book Commerce  
**Launch market:** India; INR pricing and Razorpay payments  
**Domain:** pustora.in  
**Decision principle:** Deliver a secure, usable end-to-end vertical slice at each phase gate before starting the next phase.

## 1. Product summary

Build a responsive commerce and fulfillment platform for publishing and selling books. Readers can discover books, inspect image/video galleries, read a publisher-provided sample, purchase securely, and follow order progress. Administrators manage catalog content, users, permissions, and the platform. Fulfillment staff update assigned orders with timestamped status events and customer-facing location or dispatch notes.

The initial release is a single-publisher storefront with a modular design that can support more products, staff roles, and traffic without prematurely introducing microservices. The future direction may include multiple publishers, but marketplace tenancy, onboarding, revenue sharing, and publisher-level access control are explicitly out of the initial release. Admins initially arrange and deliver orders themselves; the system records and communicates the operational status rather than integrating a carrier.

## 2. Problem and outcomes

The publisher needs one reliable place to present books, accept and reconcile payments, and keep customers informed after purchase. Manual product presentation and order updates are difficult to scale and make it hard to provide consistent, trustworthy customer experiences.

### Outcomes

- Readers can discover, evaluate, buy, and track books using a mobile-friendly storefront.
- The publisher can manage product information and media without engineering support.
- Payment state is reconciled from verified gateway events, not just browser redirects.
- Fulfillment staff can update only the orders they are authorized to handle.
- Customer and staff interfaces expose only the data and actions appropriate to the user's permissions.
- The initial system is operable and testable, with clear security, cost, and growth controls.

### Initial success measures

Instrument these from launch; establish baselines before setting numeric targets:

- Product detail → add-to-cart and checkout conversion.
- Successful payment rate and payment/order reconciliation exceptions.
- Checkout completion time and checkout error rate.
- Percentage of paid orders with a first fulfillment update within the publisher's operating SLA.
- Customer support contacts about order status.
- Catalog publication errors, authentication abuse, and authorization-denial events.
- Availability and p95 latency for storefront, checkout, and order tracking.

## 3. Users and access model

| Persona | Primary needs | Default access |
|---|---|---|
| Visitor | Browse books, see reviews/testimonials, inspect a sample | Public catalog and published content only |
| Customer | Manage own account, cart, checkout, payment outcome, and orders | Own profile and own orders only |
| Fulfillment staff | Process assigned work and record delivery progress | Assigned orders and permitted status updates |
| Support agent | Handle customer questions and complaints | Minimum necessary customer/order details and support actions |
| Catalog manager | Draft and maintain products, pricing, and media | Catalog capabilities explicitly granted |
| Order manager | Manage all order workflows | Order management capabilities explicitly granted |
| Administrator | Manage platform operations, users, roles, catalog, and orders | Broad access, subject to audit and strong authentication |
| Super admin | Own platform-wide administration and recovery | All platform permissions; tightly controlled and audited |

Use **attribute-based authorization (ABAC)** with named roles as manageable bundles of permissions. A decision must consider the principal's permissions and attributes, the requested action, the resource, and relevant context (for example, order assignment and status). Deny by default. UI visibility is a usability feature, never the authorization boundary: every API action independently authorizes access and filters returned records. Do not return unauthorized records and rely on the client to hide them.

Initial permission families include `catalog.read`, `catalog.write`, `catalog.publish`, `content.manage`, `orders.read_own`, `orders.read_assigned`, `orders.read_all`, `orders.update_fulfillment`, `users.manage`, `roles.manage`, `support.read_limited`, `support.manage_cases`, `inventory.manage`, `invoices.manage_templates`, and `audit.read`. The role matrix below is the launch baseline. The last three operational rows extend the attached matrix to cover support, inventory, and invoice-template requirements in this PRD. “Granted” means the capability is individually granted to that account; “Limited” means purpose-limited fields/actions and must not be interpreted as unrestricted access.

| Capability | Super Admin | Admin | Catalog Manager | Order Manager | Fulfillment Staff | Support Agent | Customer |
|---|---|---|---|---|---|---|---|
| View catalog | Yes | Yes | Yes | Yes | No | Limited | Public catalog |
| Edit catalog | Yes | Yes | Yes | No | No | No | No |
| Publish books | Yes | Yes | By explicit grant | No | No | No | No |
| View all orders | Yes | Yes | No | Yes | No | Limited | No |
| View assigned orders | Yes | Yes | No | Yes | Yes | Limited | Own orders only |
| Update fulfillment | Yes | Yes | No | Yes | Assigned orders only | No | No |
| Manage users | Yes | Yes | No | No | No | No | Own profile only |
| Manage roles | Yes | Yes | No | No | No | No | No |
| View audit logs | Yes | By explicit grant | No | No | No | No | No |
| Manage support cases | Yes | Yes | No | No | No | Yes | Own requests only |
| Manage inventory | Yes | Yes | No | No | No | No | No |
| Manage invoice templates | Yes | Yes | No | No | No | No | No |

Super Admin and Admin retain the broad platform capabilities shown; sensitive actions remain audited, and privileged actions require step-up authentication. Support’s limited order view is restricted to information necessary to answer the active support request; it must not expose payment credentials, full authentication data, or unrelated customer records. A staff assignment is a resource attribute, not a substitute for checking the role’s permission. Role grants, revocations, and changes are audited. Enforce this matrix in backend authorization and query scoping; UI hiding alone is never authorization.

## 4. Core journeys

### 4.1 Identity and account security

1. A visitor registers with email/password, Google sign-in, or mobile number/OTP.
2. The account flow verifies ownership of the chosen identifier, prevents account enumeration, rate-limits attempts, and handles duplicate identities and recovery safely.
3. Supported sign-in methods are email/password, Google sign-in, and mobile OTP. MFA is not required for every customer; require step-up MFA for privileged staff/admin accounts and designated sensitive actions. Use the supported mobile OTP as the second factor where appropriate; do not silently count the same OTP challenge as both primary authentication and MFA.
4. Sessions can be viewed/revoked; logout, expiry, refresh rotation/revocation, and account recovery behave consistently across browser and API. Recovery codes, when issued, are stored hashed and are single-use.

### 4.2 Discover and evaluate books

1. A visitor sees a responsive landing page with curated banners, featured books, reviews, testimonials, and feedback media.
2. A visitor opens a product detail page with a primary image, thumbnail carousel, optional video, descriptive details, price, and availability.
3. A visitor opens a clearly labeled **View demo book** action. The sample is rendered in a browser-friendly reader with page navigation and reasonable protections against casual bulk access; no web delivery can prevent screenshots or all copying.

### 4.3 Purchase and follow an order

1. An authenticated customer adds an available book to a cart and sees quantities and a transparent price summary.
2. Checkout captures validated delivery details and creates a pending order/payment attempt using server-calculated prices. The system reserves stock for a configurable short period.
3. The customer completes Razorpay checkout. The server verifies payment signatures and webhook authenticity, handles retries idempotently, and updates order/payment state only from trusted evidence.
4. The customer sees the resulting order and a chronological, timestamped tracking timeline. Failed, abandoned, pending, refunded, and disputed payment outcomes must not appear as paid orders.

### 4.4 Manage catalog and fulfillment

1. Authorized staff create/edit products, pricing, publication state, and associated images, videos, and sample PDFs.
2. Uploads are validated and stored in object storage; large media is delivered through a CDN or short-lived signed URLs according to publication/access policy.
3. An authorized fulfillment user views only permitted orders and records a status, timestamp, and customer-facing message such as “Dispatched from Bengaluru.” The system records actor and time, and the customer sees a safe tracking event.
4. An administrator can manage roles, assignments, and operations with audited access.

## 5. Functional requirements

### Identity

- Support only email/password, Google OpenID Connect, and mobile OTP sign-in/registration for the initial release; keep provider integrations behind adapters.
- Require verified identifiers before sensitive account actions; link identities only after proving control of both.
- MFA is optional for ordinary customers and required for privileged staff/admin roles and designated sensitive operations. Require a second, independent supported factor for step-up: mobile OTP after email/password or Google sign-in; staff/admin who sign in with mobile OTP must also verify a password. Do not grant privileged access to an account without the required independent factor, and do not add authenticator-app methods in the initial scope.
- Store passwords with Argon2id; store OTPs and recovery codes only as secure hashes (use a server-keyed verifier for low-entropy OTPs), enforce expiry/attempt limits, compare safely, and make recovery codes single-use. Never store plaintext credentials or verification codes.
- Default OTP policy: generate six digits using a cryptographically secure random source, five-minute validity, 30–60-second resend cooldown, at most five verification attempts, and initially at most five sends per hour per identifier. Apply additional IP/device/identifier-based abuse limits and monitor login attempts. Tune limits from observed abuse and delivery reliability.
- Use HttpOnly, Secure, SameSite cookies, CSRF protection for cookie-authenticated state-changing requests, refresh-token rotation and revocation, session management, and secure transport in production.
- Do not reveal whether an account exists in login, recovery, or OTP responses. Avoid long-lived OTP or refresh-token material in logs and analytics.

### Orders, shipping, tax, inventory, and invoices

- Checkout is authenticated; guest checkout is not in the initial scope.
- Display catalog prices, GST, final payable amount, and shipping according to DR-01 and DR-02 in the decision register. This register is the sole source of truth for price-display and shipping calculation.
- Generate invoices according to DR-03. Preserve immutable order/tax values and the exact invoice template version used at issuance.
- Implement inventory reservation, payment timeout, low-stock, late-payment, cancellation, and refund behavior according to DR-04 through DR-06. Record every inventory movement with actor, reason, time, quantity, and related order; enforce reservation and availability changes atomically. Never rely on the client redirect alone for payment state.
- Support channels and service targets follow DR-11 through DR-13; these are not a 24/7 guarantee. Apply authorization and data-minimization rules to support access and submissions.
- Contact-form submissions collect only the fields and retention described in DR-11 through DR-13; show a privacy notice and avoid payment credentials or sensitive identity data. Initially use WhatsApp Business as a human-operated support channel, not an unreviewed automated bot.

### Notifications and customer feedback

- Use replaceable provider adapters for OTP and transactional email according to DR-08. Keep provider selection/configuration outside business logic and support migration without changing auth or notification contracts.
- Process notifications through a background worker; persist notification events and delivery state in PostgreSQL for operational tracking. Retry transient provider failures safely and avoid duplicate customer messages where possible. If a provider definitively rejects or is unavailable before accepting a message, route the same logical notification to the configured fallback using an idempotency key. For ambiguous timeouts, query/reconcile provider status before fallback to avoid duplicate OTPs or transactional mail. OTP fallback must send the same still-valid challenge, not create a second active code. Never log OTPs.
- Transactional notification events include account verification, password reset, order confirmation, payment success/failure, order processing, dispatch, delivery, refund updates, and important account-security alerts.
- Keep marketing consent separate from transactional messaging; support unsubscribe and consent history before any marketing sends.
- Only authorized admins may publish customer testimonials, video feedback, book reviews, student success stories, promotional banners, and featured-book collections. Customer-submitted content/moderation workflows are not in the initial scope.

### Storefront and content

- Responsive landing page with configurable sections and publishable/unpublishable banners, testimonials, review videos, feedback messages, and images.
- Search and basic sorting/filtering for the initial catalog; paginate results.
- Product page with multiple images, video, accessible gallery controls, inventory/sale state, and price/currency.
- Demo PDF upload and in-browser sample reader with page-level access control and configurable sample limits.
- Media metadata includes alt text, ordering, captions, and publication state.

### Cart, checkout, and payment

- Cart supports multiple books, quantity changes, removal, and clear price totals.
- The backend is authoritative for price, discount, stock/availability, shipping/tax policy, and order creation. Never trust client-supplied totals.
- Use an order/payment state machine with documented valid transitions.
- Razorpay integration uses server-created payment orders, signature verification, verified webhooks, idempotency, reconciliation, and safe secret management.
- Persist gateway identifiers and minimal transaction metadata; do not store card numbers, CVVs, or other payment credentials.
- Define operational paths for payment timeout, duplicate webhook, late success, cancellation, refund, and support reconciliation.

### Orders and fulfillment

- Customers see only their own orders and their own tracking events.
- Staff access is scoped by explicit permissions and, where applicable, assignment/organizational attributes.
- Order timeline events are append-only for operational history; corrections create a new event or audited administrative correction rather than silently rewriting history.
- Use the order/payment statuses, return/refund case lifecycle, and allowed transitions in DR-06. Keep return/refund cases separate from shipment history and link them auditably to the order.
- A tracking event contains status, customer-safe note, event time, actor, and optional location text. Do not expose private staff notes.
- Carrier APIs, live GPS, and automated shipping labels are not MVP requirements.

### Catalog administration and authorization

- Admin/catalog manager CRUD for book metadata, price, publication status, gallery/video media, and sample material.
- Validate uploaded file type using content inspection as well as declared MIME type; enforce size limits; use randomized object keys; restrict upload/download authorization; scan files where a suitable service is available.
- Manage staff roles, permissions, and order assignments through authorized admin functions.
- Apply authorization at API/service boundaries and at data-query boundaries. Keep response schemas purpose-specific and omit secrets and unrelated personal data.
- Record security-sensitive changes in an audit trail with actor, action, target, time, and safe before/after details. Never log credentials, OTPs, tokens, payment secrets, or unnecessary personal data.

## 6. Non-functional requirements

### Security and privacy

- Threat-model identity, account linking/recovery, admin access, media uploads, demo delivery, checkout, webhooks, and order access.
- Use TLS in transit, managed encryption at rest, secret management, least-privilege service credentials, and separate development/staging/production environments.
- Validate inputs, use parameterized database operations, apply output encoding, and configure security headers and a restrictive Content Security Policy.
- Protect authorization against IDOR/BOLA by checking ownership/assignment for every resource operation.
- Prevent CSRF where cookie authentication is used; use secure session rotation and revocation.
- Verify Google OIDC issuer, audience, signature, nonce, state, redirect URI, and PKCE as applicable. Never trust identity claims from the browser without server validation.
- Keep PII collection minimal and purpose-bound; publish privacy, shipping, cancellation/return/refund, grievance/support, and payment disclosures before checkout. Provide a documented process for account/data access, correction, deletion, consent withdrawal, retention holds, and privacy incident response.
- Review current India privacy/data-protection, consumer e-commerce, tax/invoicing, payment, and record-retention obligations with qualified specialists before production. This PRD is an engineering baseline, not a legal compliance determination.
- Apply media, support-case, invoice/order, and log retention according to DR-12 and DR-13. Restrict access and do not retain credentials or OTP values.
- Maintain audit logs and security monitoring with access restrictions and retention controls.

### Reliability, performance, and accessibility

- Use the proposed load profile and service/recovery objective candidates in DR-10. Treat them as engineering targets only until verified against measured load and selected vendor tiers; report upstream provider availability separately. Show degraded checkout/notification state rather than success-shaped fallbacks. Payment correctness and authorization are correctness properties, not availability trade-offs.
- Require a named owner to approve a monthly operating budget before production. Configure spend alerts at 50%, 75%, 90%, and 100% of that budget and service/provider quota alerts. Halt optional media processing or marketing sends before compromising authentication, payment reconciliation, backups, or security monitoring.
- Keep payment/order operations resilient to retries and partial failure. Use idempotency and background jobs for webhook processing, notifications, and media work.
- Use PostgreSQL as the source of truth; Redis is an ephemeral cache/queue/rate-limit aid, not the only copy of business state.
- Serve images/videos/PDFs from object storage/CDN rather than the application process. Resize/transcode asynchronously where appropriate.
- Meet WCAG 2.2 AA as a design and test target; support keyboard navigation, visible focus, captions/transcripts for video, semantic forms, and useful error messaging.
- Accessibility checks include full keyboard navigation, meaningful image alt text, labeled forms and clear validation, sufficient color contrast, accessible button names, video captions/transcripts, semantic HTML and ARIA only where needed, responsive/touch-friendly layouts, and an accessible alternative for PDF samples where feasible.
- Support backups, point-in-time recovery where available, restore drills, health checks, and operational alerts before launch.

## 7. Proposed architecture and boundaries

- **Web:** React and TypeScript, Tailwind CSS, and shadcn/ui. Use reusable, accessible design primitives and route-level permission-aware UX.
- **API:** Python/FastAPI with typed request/response schemas, service-layer business rules, explicit authorization dependencies, and versioned API contracts.
- **Data:** PostgreSQL for users/identities, catalog, media metadata, carts, orders, payment attempts, tracking events, roles/permissions, assignments, and audit records. Use migrations and transactional constraints.
- **Cache/async work:** Redis for rate limits, short-lived cache, and queue coordination. A background worker handles notifications, media processing, and webhook follow-up; durable business state remains in PostgreSQL.
- **Media:** S3-compatible object storage plus a CDN with suitable India coverage; keep object keys and metadata in Postgres. Separate public assets from protected demo material.
- **Integrations:** Google OIDC, OTP/email providers per DR-08, and Razorpay behind adapters so business logic is not coupled to vendors.
- **Operations:** Managed PostgreSQL, Redis, worker, error tracking, metrics, and logs. Hosting region is India subject to vendor capability and legal review. Use structured redacted logs, monitoring/alerts, backups, CI checks, and infrastructure-as-code when deployment environment is selected.

Start as a modular monolith (web app, API, worker) with clear domain modules; split services only when measured scale, team ownership, or reliability needs justify the operational cost.

## 8. Data and API principles

- Model identity separately from authentication methods so multiple verified sign-in methods can be safely linked to one account.
- Use stable IDs, UTC timestamps, explicit money/currency types, and database constraints for invariants.
- Use INR as the launch currency. Preserve price, shipping, tax, inventory reservation, and invoice snapshots needed to explain the final order amount.
- Make inventory movements and reservations auditable; distinguish available, reserved, and sold quantities so a payment confirmation does not deduct a reservation twice.
- Treat product price changes and order snapshots separately: a placed order retains the price and item description used at purchase.
- Make payment callbacks idempotent and preserve a verifiable payment-event trail.
- Paginate list APIs, bound query sizes, and avoid returning full user/order records when a smaller response will do.
- Use explicit response models for customer, staff, and admin contexts; avoid generic “return the ORM object” serialization.
- Version externally relied-on API contracts and document error shapes.

## 9. MVP scope and exclusions

### MVP

- Single publisher and storefront; responsive landing and catalog.
- Customer identity flows with optional customer MFA, mandatory privileged-role step-up MFA, account recovery, and role-aware sessions.
- Product gallery/video, public content sections, and demo PDF reader.
- Cart, checkout, Razorpay payment confirmation, and order history.
- Admin catalog/content management.
- Inventory ledger and reservations, configured shipping tiers, GST/invoice generation with admin-selected template, and customer support entry points.
- Provider-adapted OTP/email and durable notification-event tracking.
- Staff-scoped manual fulfillment updates and customer tracking timeline.
- ABAC foundations, audit events, automated tests, operational monitoring, backup/restore runbook.

### Explicitly later

- Multi-vendor marketplace, multiple publishers/tenants, multiple warehouses.
- Carrier integrations, live tracking, shipping label purchase, automated returns.
- Subscriptions, bundles, gift cards, loyalty, reviews with moderation workflows, advanced recommendations.
- Native mobile apps, multi-currency, international tax/shipping.
- DRM guarantees for PDF previews; browser-only controls cannot prevent copying.
- Microservices, Kubernetes, or a complex data warehouse without evidence they are needed.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Account takeover through weak recovery, OTP abuse, or identity-linking flaws | Threat model; rate limits; secure recovery; step-up MFA; verified linking; abuse monitoring and tests |
| Customer sees another user's order or staff sees unassigned work | Default-deny authorization; row/query scoping; API response filtering; cross-role negative tests |
| Payment marked paid from a spoofed redirect or duplicate/late webhook | Server verification, signed webhooks, idempotency, durable event records, reconciliation and exception alerts |
| PDF or media upload exposes malware, private content, or excessive bandwidth cost | Validate and scan uploads; private-by-default demos; short-lived access; size limits, CDN, quotas, lifecycle policies |
| Manual fulfillment status is inconsistent or misleading | Constrained state machine, actor/time audit, customer-safe message, correction history, operational ownership |
| MFA/SMS and media costs grow unexpectedly | Prefer low-cost factors where suitable; provider pricing review, quotas, rate limits, caching, image optimization, usage alerts |
| Reservation leaks or concurrent checkouts oversell stock | Transactional inventory reservations with expiry/release jobs, atomic capacity checks, idempotent payment transitions, and concurrency tests |
| GST/invoice configuration is incorrect or changes after an order | Obtain tax review, make tax settings effective-dated, preserve immutable order/invoice snapshots, and audit template/rate changes |
| Cancellation or return defaults conflict with consumer obligations | Publish clear pre-purchase terms; have qualified counsel validate stage rules, time windows, exceptions, and refund disclosures before production |
| Overengineering delays a usable release | Modular monolith, vertical slices, phase exit criteria, defer speculative integrations |
| Legal/tax/consumer requirements are missed | Confirm launch jurisdiction and consult qualified advisors before production; document policies and retention |

## 11. Cost and scalability strategy

Planning traffic assumptions (not guarantees or SLOs):

| Metric | Initial | Growth | Expansion |
|---|---:|---:|---:|
| Monthly visitors | 5,000 | 50,000 | 250,000 |
| Concurrent users | 50 | 200 | 1,000 |
| Books | 500 | 5,000 | 25,000 |
| Monthly orders | 500 | 5,000 | 25,000 |
| Publishers | 1 | 1 | Multiple |

Use traffic bands and the proposed load/SLO/recovery targets in DR-10. Validate them through measurement, restore drills, and provider evidence before calling them commitments.

There is not enough information to provide a credible monthly cost estimate because no monetary budget, media volume, or provider quotes were supplied. A named owner must approve a monthly budget before production; set spend alerts at 50%, 75%, 90%, and 100%, plus quota alerts for SMS, email, storage, and egress. Before sizing production services, estimate media storage/egress, OTP/email volume, peak traffic shape, orders/payment volume, retention, and support load.

Control cost without sacrificing core security:

- Begin with managed PostgreSQL, Redis, object storage/CDN, and a modest application/worker footprint; choose deployment region and provider after operational and data-residency review.
- Set budgets and alerts for compute, database, storage, egress, SMS, email, payment fees, logs, and backups.
- Use image resizing, video compression, CDN caching, bounded logs, database indexes based on measured query patterns, and retention/lifecycle policies.
- Keep dev/staging smaller than production; use synthetic/test credentials and payment sandbox environments.
- Use free tiers/credits only when eligible and suitable; record limits and an exit plan. Never depend on a free tier for production authentication, transactional messaging, backups, or required monitoring without verified quota and reliability.
- Track unit economics such as infrastructure cost per order and per active customer.
- Load-test anticipated peaks; add vertical/horizontal capacity based on metrics rather than estimates alone.
- Start with one React frontend, one modular FastAPI backend, managed PostgreSQL, Redis for cache/queues, one background worker, S3-compatible object storage, and an India-capable CDN. Add replicas or worker capacity based on observed bottlenecks.
- Design publisher ownership boundaries into catalog/order models where low-cost and non-disruptive, but defer marketplace onboarding, tenant isolation guarantees, publisher billing, and revenue sharing until a separately planned marketplace phase.

## 12. Acceptance criteria for initial release

- All critical customer/admin journeys can be completed in a production-like environment.
- Authentication and policy-based MFA/recovery, authorization isolation, payment verification, webhook idempotency, upload validation, inventory reservation/oversell prevention, invoice snapshots, and valid order transitions have automated tests.
- API denies unauthorized requests regardless of whether a UI control is hidden.
- Customer, fulfillment, catalog, and admin views have been tested with representative permissions and data.
- The payment sandbox has been exercised for success, failure, cancellation, duplicate webhook, and reconciliation exceptions.
- Accessibility, responsive layout, basic performance, restore, monitoring, and release runbooks have been reviewed.
- Production secrets, data handling, support/escalation ownership, applicable policies, and operational cost limits are approved.

## 13. Engineering decision register

This register is the canonical source for launch assumptions and unresolved decisions. Earlier sections reference decision IDs rather than restating adjustable values. Status meanings: **Confirmed default** = product direction supplied by the owner, not a claim of legal/vendor feasibility; **Proposed** = engineering/product recommendation awaiting owner approval; **Open validation** = external evidence or a named accountable decision is required. Proposed dates below are planning targets, not committed deadlines. Human names were not supplied, so owners are accountable roles and must be assigned to people at Phase 0 kickoff.

| ID | Decision area and canonical decision | Status | Accountable owner (person to assign) | Reviewer | Target decision date | Evidence/source and gate |
|---|---|---|---|---|---|---|
| DR-01 | **Price and shipping.** Catalog prices are GST-exclusive and must be labeled as such. Show GST and final payable amount before payment. Shipping is calculated from merchandise subtotal before shipping and GST: `< ₹499` = ₹49; `₹499–₹999` inclusive = ₹29; `≥ ₹1,000` = free. Server recalculates totals. | Confirmed default | Product Owner | Engineering Lead | Confirmed 2026-11-10; owner identity to assign | User requirements supplied 2026-11-10. Tax treatment of shipping remains DR-02. |
| DR-02 | **GST.** 5% is the initial product assumption only; tax category, applicable rate, shipping tax treatment, place of supply, registration, and calculation/display must be validated. Store effective-dated tax configuration; do not hard-code the assumption as law. | Open validation | Finance/Tax Owner (unassigned) | Qualified India tax advisor; Legal Counsel | Proposed 2026-12-15 (unapproved) | User's 5% assumption; no official classification/advice supplied. Production checkout gate. |
| DR-03 | **Invoices.** Support multiple invoice templates; an authorized admin selects the active version. Issued invoices retain immutable order/tax values and template version. Legal fields, numbering, and final templates require review. | Proposed; legal validation open | Product Owner + Finance/Tax Owner (unassigned) | Qualified India tax advisor; Legal Counsel | Proposed 2026-12-15 (unapproved) | Product requirement; no approved invoice design or tax advice supplied. Before production invoice issuance. |
| DR-04 | **Inventory reservation and payment timeout.** Proposed default is a configurable 15-minute reservation/payment-attempt TTL. Reserve at checkout; release on verified failure/expiry; verified payment converts reservation to sold without a second stock deduction. Late verified success re-reserves atomically if possible, otherwise enters reconciliation/refund. Never oversell or trust redirect state. | Proposed | Product Owner + Engineering Lead (unassigned) | Operations Lead | Proposed 2026-12-01 (unapproved) | E-commerce baseline proposed in PRD; validate with payment and fulfillment operations before Phase 4. |
| DR-05 | **Low stock and backorders.** Proposed default: no backorders; threshold 5 available units; display “low stock” and expose exact count only when explicitly enabled. Out-of-stock is not purchasable. | Proposed | Product Owner (unassigned) | Operations Lead | Proposed 2026-12-01 (unapproved) | Product/engineering recommendation; confirm merchandising behavior before catalog build. |
| DR-06 | **Order, payment, cancellation, returns, and refunds.** Payment attempt states: `created`, `pending`, `succeeded_verified`, `failed`, `expired`, `reconciliation_required`, `refund_pending`, `refunded`. Order states: `placed`, `payment_pending`, `paid`, `processing`, `dispatched`, `out_for_delivery`, `delivered`, `cancelled`, `payment_failed`, `reconciliation_required`, `refund_pending`, `refunded`. Return/refund case states: `requested`, `under_review`, `approved`, `rejected`, `return_in_transit`, `received`, `refund_initiated`, `refund_completed`. Proposed policy: cancel payment-pending and paid-before-picking/packing; after picking/packing route to support; after dispatch use approved return policy; accept damaged/defective/incomplete/wrong-book requests within 7 calendar days of delivery; no change-of-mind return by default. Initiate approved refund after return receipt/verification; 5–7 business days is an estimate, not a guarantee. | Proposed; consumer-law validation open | Product Owner + Operations Lead (unassigned) | Qualified India consumer-law counsel; Payment Operations | Proposed 2026-12-15 (unapproved) | Product conversation and proposed operational default; statutory rights and policy not legally reviewed. Before public terms/live orders. |
| DR-07 | **Authorization matrix.** Use the attached role/capability matrix in Section 3. Catalog publishing by Catalog Manager requires explicit per-user grant; fulfillment is assigned-order only; Support access is limited to active case and minimum necessary fields; all other access is denied by default. Matrix extensions for support-case, inventory, and invoice-template management are as shown. | Confirmed product baseline; owner assignment open | Product Owner (unassigned) | Security/Engineering Lead | Proposed 2026-11-17 (unapproved) | User-provided permission matrix image and requirements supplied 2026-11-10. Assign approver and Super Admin bootstrap owner before P0-07. |
| DR-08 | **Provider adapters and free options.** Initial integrations: MSG91 SMS OTP, Amazon SES transactional email, Resend as configurable alternative. Provider-neutral interfaces and safe fallback are required. Development uses sandboxes/local sinks. Use free credits/allowances only if eligible; production cannot rely on unverified free quotas. Sender/domain verification and current limits must be checked. | Open validation | Platform/Operations Lead (unassigned) | Security Lead; provider documentation/account owner | Proposed 2026-12-15 (unapproved) | Provider preference supplied by user; no account, quote, deliverability, or quota evidence supplied. Verify before production messaging. |
| DR-09 | **India hosting and data residency.** India is the preferred hosting region, subject to provider service availability, contractual terms, data-flow mapping, and legal/privacy review. Do not claim residency or compliance until verified. | Open validation | Engineering/Platform Lead (unassigned) | Privacy/Legal Counsel; selected vendor | Proposed 2026-12-15 (unapproved) | User's hosting preference; vendor and legal evidence not yet selected. Required before production data. |
| DR-10 | **Scale, SLO, recovery, and budget.** Planning bands remain Section 11. Proposed load test: 2x forecast peak concurrency for 30 minutes, then 3x for 5 minutes. Candidate targets: storefront/core API 99.9% monthly availability, first-party non-media API p95 <500 ms, mobile LCP ≤2.5 seconds at p75, PostgreSQL RPO ≤15 minutes/RTO ≤4 hours. These are engineering targets, not commitments, until measured and supported by selected service tiers. A monthly budget amount and alert owner are not set; alert at 50/75/90/100% once approved. | Open validation | Engineering/Platform Lead + Budget Sponsor (unassigned) | Operations/Finance; selected vendors | Proposed 2026-12-15 (unapproved) | Traffic assumptions supplied by user; target values are planning proposals. No load results, vendor tiers, budget amount, or restore evidence supplied. Production launch gate. |
| DR-11 | **Support operations.** Proposed hours: Monday–Friday, 09:00–18:00 IST, excluding published holidays. Targets: acknowledge normal cases within 1 business day and update/resolve within 2; priority-triage payment, account-security, or privacy incidents within 4 business hours. Assign a human case owner, severity/status, timestamps, and overdue escalation. WhatsApp Business is human-operated initially. | Proposed; owner/setup open | Customer Support/Operations Lead (unassigned) | Product Owner; Privacy/Legal Counsel | Proposed 2026-12-01 (unapproved) | User requested standard e-commerce operations; hours/targets are proposed defaults, not a staffed service commitment. Confirm staffing and channels before publishing. |
| DR-12 | **Accessibility, privacy, and retention.** WCAG 2.2 AA is the engineering target. Proposed support-case retention is 12 months after closure; unreferenced media deletion after a 30-day recovery window; invoice/order and log retention remain subject to legal/tax/security schedules. Provide privacy notice, rights/request handling, consent withdrawal, legal holds, and incident response. | Accessibility target confirmed; privacy/legal validation open | Design/Frontend Lead + Privacy Owner (unassigned) | Accessibility specialist; qualified India privacy/legal counsel | Proposed 2027-01-15 (unapproved) | User accessibility requirements; retention values are engineering proposals. No accessibility audit or legal retention schedule supplied. Before launch. |
| DR-13 | **Support/contact data handling.** Contact form collects only contact details, optional order reference, and issue; do not request credentials or payment details. Apply DR-11 case ownership and DR-12 retention/holds. | Proposed | Support/Operations Lead (unassigned) | Privacy Owner | Proposed 2026-12-01 (unapproved) | Product requirement and privacy-by-design proposal; approve notice and workflow before enabling form. |

### DR-06 state transition contract

These are proposed legal transitions; implement them as server-side state machines, not client-selected status strings. Every transition records actor/system source, timestamp, reason where relevant, and an idempotency/event reference.

- **Payment attempt:** `created → pending`; `pending → succeeded_verified | failed | expired | reconciliation_required`; a late verified success on a failed/expired attempt transitions it to `reconciliation_required`, then `refund_pending` (if stock cannot be atomically reserved) or `succeeded_verified` (if stock can be secured). `succeeded_verified → refund_pending → refunded`. Duplicate gateway events do not repeat transitions or inventory effects. A customer redirect never transitions payment to succeeded.
- **Order:** `placed → payment_pending`; `payment_pending → paid | payment_failed | cancelled | reconciliation_required`; `payment_failed → payment_pending` only by creating a new payment attempt; a late verified capture on a failed/cancelled order moves it to `reconciliation_required`; `reconciliation_required → paid` only after stock is secured, otherwise `refund_pending`; `paid → processing | refund_pending`; `processing → dispatched` when fulfillment dispatch is recorded, or `refund_pending` only if fulfillment has not begun and cancellation eligibility is rechecked; `dispatched → out_for_delivery → delivered`; cancellation after picking/packing is a support case, not an automatic transition; `refund_pending → refunded` only after verified refund outcome. A cancellation/refund is not complete until payment and stock are reconciled.
- **Return/refund case:** `requested → under_review → approved | rejected`; `approved → return_in_transit | received`; `return_in_transit → received`; `received → refund_initiated` when refund is approved; `refund_initiated → refund_completed` only after verified gateway outcome. Record exceptions as audited case events; never erase shipment or prior case history.
- Use a distinct reconciliation state/queue for late payment or inventory mismatch. It must not be represented as paid-and-fulfillable until inventory is secured, and must not be hidden from operations.

### Decision ownership and change control

- The **Product Owner** approves customer-facing defaults and prioritization; the **Engineering/Platform Lead** owns technical feasibility and contract consistency; **Operations** owns support, fulfillment, and service readiness; **Finance/Tax** and qualified counsel own their respective external validations.
- These are accountable roles, not names. Assign each role to a person and replace proposed dates with approved dates at Phase 0 kickoff. Until assigned, decisions remain open; do not interpret a proposed date as approval or release authorization.
- A decision changes only through an updated register row with date, decision-maker, rationale, and evidence. Update all linked contracts/tickets in the same change.
- Any row marked **Open validation** blocks the affected production capability, not unrelated local development. Tax/invoice rows block live tax/invoice issuance; return-policy validation blocks publication of final return terms; hosting/privacy rows block production personal data; vendor/quota rows block production messaging; SLO/RPO/RTO rows block production readiness claims.
