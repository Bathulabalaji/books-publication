# API contracts

The FastAPI service owns the OpenAPI contract at `/openapi.json`. The initial versioned API shell and error conventions are documented in [API_CONVENTIONS.md](./API_CONVENTIONS.md). When the contract-validation ticket is implemented, export the versioned schema to `contracts/openapi.json` and generate TypeScript API types for `apps/web` from that file. Do not hand-maintain matching frontend DTOs or edit generated types directly.

Contract generation and drift checks will be wired into the shared root commands when the API bootstrap and contract-validation tickets are implemented. Until then, this directory defines ownership and dependency direction only; it is not a placeholder API schema.
