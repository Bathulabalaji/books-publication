# PUSTORA API

The backend is a testable FastAPI modular-monolith entry point. This foundation exposes only the system health route; authentication, catalog, payment, and order endpoints are added by their planned vertical slices rather than success-shaped placeholders.

## Requirements and setup

- Python `>=3.12,<3.15` and `uv`.
- From the repository root, synchronize the locked backend environment with `npm run api:sync`.
- Copy `apps/api/.env.example` to `apps/api/.env` for local settings. The file is ignored; the example contains no credentials.
- Settings use the `PUSTORA_` prefix. Supported environments are `local`, `test`, `staging`, and `production`; `PUSTORA_SERVICE_NAME` changes the health response label.
- Tests inject `Settings(environment="test")` explicitly. The current bootstrap requires no production credentials or external services.

## Commands

Run from the repository root:

| Command | Purpose |
|---|---|
| `npm run api:sync` | Synchronize dependencies from `apps/api/uv.lock` |
| `npm run api:dev` | Start the local reload-enabled API server |
| `npm run api:test` | Run backend tests |
| `npm run api:lint` | Run Ruff lint |
| `npm run api:format:check` | Verify Ruff formatting |

The API is available at `http://127.0.0.1:8000`; versioned system health is `GET /api/v1/health`, and the OpenAPI document is `/openapi.json`.

## Error contract

Errors use the stable envelope documented in [API conventions](../../contracts/API_CONVENTIONS.md). Validation responses include only safe field locations, error codes, and generic messages; they never echo submitted values. Unexpected failures return a generic 500 response while the server logs the request ID, method, route template, and exception class without logging exception text or request data.
