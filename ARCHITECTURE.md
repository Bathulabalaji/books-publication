# PUSTORA workspace architecture

## Architecture decision

Use one deployable React application and one modular FastAPI application. Keep the two package managers and dependency graphs independent: npm owns the frontend and `uv` owns the backend. Root npm scripts are the developer/CI entry points for invoking each package. PostgreSQL remains the business source of truth; persistence, Redis, workers, object storage, and vendor integrations are introduced in their owning tickets, not as empty services here.

The package boundaries are:

```text
apps/
  web/                 React + TypeScript storefront and staff UI
  api/                 FastAPI modular monolith, Python package and migrations
contracts/             API schema ownership and generated-client policy
```

## Dependency direction

- `apps/web` owns routes, feature composition, accessible UI, and the typed API client. Feature code may depend on app-level shared UI/API utilities; shared utilities must not import feature modules. The P0-03 shell uses React Router, Vite, Tailwind CSS, and route-level loading/error/not-found states.
- `apps/api` owns HTTP composition and domain modules. Its P0-04 application factory composes settings, versioned routers, request correlation, and normalized error handling. Route handlers translate HTTP input/output and call application services; domain rules must not depend on FastAPI, database drivers, or cloud/provider SDKs.
- Application services depend on domain rules and declared ports. Infrastructure adapters implement those ports and are composed at the API boundary. Do not let domain modules import another module's persistence internals.
- Keep persistence migrations under the API package and database-facing code in infrastructure adapters. Database schema changes are reviewed and versioned; do not make DDL a startup side effect.
- The browser consumes only documented API schemas. It must not import Python code, database models, provider SDKs, or server configuration.
- No shared runtime package is needed yet. Share API shapes through generated TypeScript from the backend OpenAPI document, not by duplicating handwritten DTOs or importing implementation models across runtimes.

### Backend module convention

When a product capability is implemented, group its domain, application, HTTP, and infrastructure code by capability inside the single API package. Keep cross-cutting infrastructure (configuration, database session lifecycle, logging) separate from product behavior. Add a module only when a real vertical slice needs it; do not pre-create marketplace or microservice packages.

### Frontend module convention

Use an app composition layer for bootstrap and routing, feature folders for user journeys, and a small shared layer for reusable UI, API transport, and cross-feature utilities. Components should not call persistence or provider services directly. Keep authorization decisions server-side; frontend role-aware rendering is only a usability layer.

## API contract ownership

The FastAPI application is the source of truth for OpenAPI. Once the API entry point is added, export its OpenAPI document to `contracts/openapi.json` using the API package's documented command; generate frontend TypeScript types from that artifact into the web package. Generated code is not hand-edited. Contract changes must update the schema and generated types together, and CI will check for drift when the contract-validation ticket is implemented.

Use versioned HTTP paths (`/api/v1/...`) and keep error, pagination, money, timestamp, and state contracts explicit. API contracts do not authorize a request: every backend operation must independently enforce identity, permissions, ownership, assignment, and resource state.

## Configuration and environments

Use the same application code in local, test, staging, and production environments; vary behavior only through validated environment configuration. Public frontend build configuration may contain public API origins, never secrets. Backend credentials and keys are server-only and must be provided through the environment's secret manager. Commit placeholders only; `.env` files and virtual environments are ignored.

Local tests must use explicit test settings and isolated resources. Production data, credentials, and provider endpoints must never be fallback defaults. Optional infrastructure should be replaceable behind narrow adapters. Region, vendor, pricing, and production retention decisions remain governed by the PRD decision register and are not selected by this workspace structure.

## Toolchain and commands

- Node.js `26.13.0` is the pinned local baseline in `.nvmrc`; the frontend declares compatibility with Node `>=22.12 <27`. npm workspaces require no additional monorepo tool.
- Frontend dependency versions are exact in `apps/web/package.json`; `package-lock.json` is the reproducible install source. Use `npm ci` from the workspace root.
- Python compatibility is `>=3.12,<3.15`; `apps/api/pyproject.toml` declares dependency ranges and `apps/api/uv.lock` pins the resolved graph. Use `npm run api:sync` to synchronize the backend environment.
- Root npm scripts are the shared local/CI command surface. Run `npm run workspace:check` to validate workspace dependencies and the backend lockfile, and `npm run api:sync` to synchronize its environment. `web:dev`, `web:build`, `web:typecheck`, and `web:test` run the frontend shell; `api:dev`, `api:test`, lint, and format checks invoke the FastAPI application and its checks. Frontend and backend setup/configuration are documented in [apps/web/README.md](./apps/web/README.md) and [apps/api/README.md](./apps/api/README.md).
- CI should call these same root scripts rather than maintaining a second set of shell commands. CI itself is introduced in its dedicated Phase 0 ticket.

## Test and migration locations

- Frontend tests live alongside the feature or shared module they exercise; end-to-end tests belong in the dedicated test layer once selected in Phase 0.
- Backend tests live in `apps/api/tests`, grouped by unit, API/integration, and policy concerns. Use isolated test configuration and never default to production data.
- Backend schema migrations live under `apps/api`; they are authored and applied by the migration tool selected in P0-05. Migrations are explicit commands, never import/startup side effects.

## Deliberate non-goals

This structure does not select a production hosting vendor/region, add PostgreSQL/Redis/queue containers, create provider credentials, establish a legal or tax policy, implement product endpoints, or split the API into services. Those decisions and implementations remain gated by the PRD and subsequent Phase 0/feature tickets.
