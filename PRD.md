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
- Display catalog prices exclusive of GST and label them clearly. Show GST and the final payable total in the cart/checkout before payment. Initial shipping tiers use merchandise subtotal in INR, before shipping and GST: below ₹499 costs ₹49; ₹499 through ₹999 costs ₹29; ₹1,000 and above is free. Revalidate the authoritative subtotal server-side.
- Use 5% GST as the initial product-tax assumption, subject to confirmation of applicable classification, place-of-supply, registration, and invoice rules by the publisher's tax advisor. Keep rates/configuration effective-dated and auditable rather than embedding tax arithmetic throughout the UI.
- Generate an invoice from an immutable order/tax snapshot. Provide multiple invoice template options, let an authorized admin select the active template, version templates, and preserve the template/version and legal values used for each issued invoice. Final invoice fields, numbering, and layouts require tax/legal review.
- Maintain a transactional inventory ledger rather than relying only on an editable stock number. Record every adjustment with actor, reason, time, quantity, and related order where applicable. Default reservation TTL is 15 minutes from checkout/payment-attempt creation; make it configurable. Release stock on verified payment failure or expiry. On verified payment, convert the active reservation to sold/committed stock without subtracting available stock a second time. Cancellation before dispatch releases eligible reservations/stock. Record damaged stock as an explicit negative adjustment. Prevent overselling using database transactions/locking or equivalent atomic updates.
- The payment attempt expires after 15 minutes unless Razorpay reports a verified success; a late success after reservation expiry must not silently oversell—place it into a reconciliation state and either re-reserve available stock atomically or initiate a refund. Never rely on the client redirect alone.
- Do not allow backorders in the initial release. When available stock is at or below a configurable threshold (default: 5), show a low-stock state; show exact counts only when the publisher explicitly enables it. Out-of-stock books cannot be purchased. Reservation and inventory changes must be atomic, including under concurrent checkout.
- Apply cancellation rules server-side: payment pending may be cancelled; paid orders may be cancelled until fulfillment has begun (before picking/packing). Once picking/packing starts, create a support/exception request rather than promising cancellation; fulfillment staff cannot decide refunds. After dispatch, ordinary cancellation is unavailable and the approved return policy applies. A cancellation/refund is not complete until the order/payment state and inventory ledger are reconciled.
- Initial return handling: accept a customer return/complaint request within seven calendar days of delivery for damaged, defective, incomplete, or wrong books, subject to evidence and applicable law. Change-of-mind returns are not offered by default for books; disclose the policy before purchase and validate it with India consumer-law counsel. Support records and reviews each request. When approved, provide return instructions and initiate refund after the return is received/verified, unless law or the approved exception process requires otherwise. Display refund states and a target of 5–7 business days after refund initiation, subject to the payment provider/bank; do not represent that target as guaranteed.
- Support channels for the initial release: support email, WhatsApp Business, and contact form. Publish business hours as Monday–Friday, 09:00–18:00 India Standard Time, excluding published holidays. Acknowledge normal requests within one business day and target an update/resolution within two business days; payment/account-security or suspected privacy incidents receive priority triage within four business hours. These are service targets, not a 24/7 guarantee. Assign a human owner to each case, record severity/status/timestamps, and escalate overdue/high-impact cases to the operations lead. Apply authorization and data-minimization rules to support access and submissions.
- Contact-form submissions should collect only contact details, order reference where relevant, and the issue description; show a privacy notice and avoid payment credentials or sensitive identity data. Retain the case and correspondence for 12 months after closure by default, then delete or anonymize unless a legal, tax, fraud, or dispute hold applies. Final retention schedule and WhatsApp Business access/retention require privacy/legal review. Initially use WhatsApp Business as a human-operated support channel, not an unreviewed automated bot.

### Notifications and customer feedback

- Use provider adapters so authentication and notification services do not depend directly on one vendor. Initial choices: MSG91 for production SMS OTP; Amazon SES for transactional email, with Resend as a configurable alternative. During development, use provider sandboxes/local delivery sinks. In production, use a provider's no-cost allowance only if the account is eligible and the current terms, sender verification, deliverability, and volume limits are suitable. Do not promise that OTP/SMS or email delivery is free or rely on a free tier for an availability commitment.
- Keep provider selection/configuration outside business logic. Support controlled migration between MSG91/another OTP provider and SES/Resend without changing auth or notification contracts. Verify domain/sender ownership (including SPF, DKIM, and DMARC where supported) before production sending.
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
- Initial statuses: `placed`, `payment_pending`, `paid`, `processing`, `dispatched`, `out_for_delivery`, `delivered`, `cancelled`, `payment_failed`, `refund_pending`, and `refunded`. Enforce valid transitions and document which roles may perform each.
- Track return/refund requests as a separate case lifecycle, not by overwriting shipment history: `requested`, `under_review`, `approved`, `rejected`, `return_in_transit`, `received`, `refund_initiated`, and `refund_completed`. Keep the customer-facing order timeline and return/refund case status linked and auditable.
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
- For media, retain original assets while published; regenerate derivatives where possible. Unpublish protected demo material immediately when removed from sale; delete unreferenced assets after a 30-day recovery window unless an order, dispute, or legal hold requires retention. Define separate retention for issued invoices/order records based on tax/legal advice.
- Retain support cases for 12 months after closure by default, subject to legal/dispute holds. Minimize diagnostic data and set explicit retention for application, access, and security logs before production; restrict access and do not retain credentials or OTP values.
- Maintain audit logs and security monitoring with access restrictions and retention controls.

### Reliability, performance, and accessibility

- Plan for the initial/growth/expansion traffic bands in Section 11. Load-test at 2x forecast peak concurrency for 30 minutes, then a short 3x peak-concurrency spike for five minutes to model campaign traffic and sudden bursts. These are test assumptions, not guaranteed capacity; revise from analytics and campaign plans.
- Initial service objectives: 99.9% monthly availability for storefront and core API (excluding documented planned maintenance and upstream provider outages); p95 API response below 500 ms for first-party non-media endpoints under the agreed load; storefront LCP at or below 2.5 seconds at the 75th percentile on representative mobile networks. Report upstream provider availability separately and show degraded checkout/notification state rather than success-shaped fallbacks. Payment correctness and authorization are correctness properties, not availability trade-offs. Instrument p50/p95/p99, error rates, and third-party dependency health.
- Initial recovery objectives: PostgreSQL RPO of at most 15 minutes and RTO of at most 4 hours. Use managed backups/PITR where available and prove recovery with scheduled restore drills; confirm that chosen provider/service tier can meet these objectives before launch.
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
- **Integrations:** Google OIDC, MSG91 SMS OTP, Amazon SES (or configured Resend alternative) for transactional email, and Razorpay behind provider adapters so business logic is not coupled to vendors.
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

For load testing, sustain 2x forecast peak concurrency for 30 minutes, then spike to 3x peak concurrency for five minutes. These are planning assumptions to validate, not SLAs. The initial SLO targets are 99.9% monthly storefront/core API availability (excluding documented planned maintenance and upstream provider outages), p95 under 500 ms for first-party non-media API calls at agreed load, and LCP ≤2.5 seconds at p75 on representative mobile networks; initial recovery targets are RPO ≤15 minutes and RTO ≤4 hours. Report upstream provider availability separately and verify provider/service tiers can support the targets.

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

## 13. Open decisions to resolve before implementation reaches production

1. Confirm final legal publisher name, brand assets, domain ownership/management, India hosting vendor/region, and data-residency requirements.
2. Obtain tax/legal review of the GST-exclusive display, book tax classification, shipping tax treatment, invoice numbering/required fields, and invoice templates.
3. Before production, have counsel validate the cancellation/return/refund policy, including seven-day defect/wrong-item request window, change-of-mind policy, disclosures, and statutory rights.
4. Approve customer MFA opt-in/step-up UX and recovery support SLA; confirm privileged-role MFA policy and which sensitive actions require re-verification. Privileged users must have a second independent supported factor available.
5. Confirm MSG91, Amazon SES, and Resend account eligibility, pricing/credits, sender/domain verification, OTP deliverability, rate limits, fallback behavior, and production quotas. Keep provider adapters/configuration switchable.
6. Confirm exact role permission matrix, who can grant/revoke Super Admin, and the bootstrap/recovery process for platform administrators.
7. Validate traffic/load assumptions, media storage/retention, SLO/RPO/RTO feasibility, and set a named monthly budget and alert owner.
8. Assign support owner and escalation contacts; configure WhatsApp Business; publish support hours and response targets; approve contact-form privacy notice and case retention.
9. Have qualified specialists confirm applicable accessibility, privacy, security, consumer-protection, tax, payment, and retention requirements before production.
