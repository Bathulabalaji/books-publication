# PUSTORA API

The backend is a testable FastAPI modular-monolith entry point. This foundation exposes only the system health route; authentication, catalog, payment, and order endpoints are added by their planned vertical slices rather than success-shaped placeholders.

## Requirements and setup

- Python `>=3.12,<3.15` and `uv`.
- From the repository root, synchronize the locked backend environment with `npm run api:sync`.
- Install PostgreSQL locally or use an explicitly provisioned development database. The application does not create databases or run migrations on startup.
- Copy `apps/api/.env.example` to `apps/api/.env` and replace the local database placeholder. The file is ignored; never put production credentials in a checked-in file.
- Settings use the `PUSTORA_` prefix. Supported environments are `local`, `test`, `staging`, and `production`; `PUSTORA_DATABASE_URL` must be a PostgreSQL `postgresql+asyncpg` URL and is required for staging/production. `PUSTORA_SERVICE_NAME` changes the health response label.
- Database URLs are held as secret settings and are not returned by health endpoints or included in application logs. Tests inject `Settings(environment="test")` explicitly and use fakes; they never fall back to a configured or production database.

## Commands

Run from the repository root:

| Command | Purpose |
|---|---|
| `npm run api:sync` | Synchronize dependencies from `apps/api/uv.lock` |
| `npm run api:dev` | Start the local reload-enabled API server |
| `npm run api:db:upgrade` | Apply migrations through Alembic head on the configured database |
| `npm run api:db:current` | Check that the configured database is at all migration heads |
| `npm run api:db:history` | Show the migration history without changing the database |
| `npm run api:db:check` | Compare the current database schema with mapped metadata |
| `npm run api:db:revision -- --autogenerate -m "describe change"` | Generate a migration revision for reviewed metadata changes |
| `npm run api:test` | Run backend tests |
| `npm run api:lint` | Run Ruff lint |
| `npm run api:format:check` | Verify Ruff formatting |

The API is available at `http://127.0.0.1:8000`; liveness is `GET /api/v1/health`, database readiness is `GET /api/v1/ready`, and the OpenAPI document is `/openapi.json`. Readiness returns a normalized 503 if the database is unconfigured or unavailable. It never includes connection details.

## Database and migrations

- Alembic configuration and versioned revisions live under `apps/api/alembic.ini` and `apps/api/migrations`.
- The initial revision is deliberately empty: it establishes the Alembic version table and proves migration execution without introducing product schema before its domain contract.
- `upgrade head` and `current --check-heads` are explicit commands. Do not execute migrations during imports, application startup, health checks, or tests.
- `pustora_api.db.base.Base.metadata` is Alembic's metadata source. As domain tables are implemented, import their models into the Alembic environment before generating revisions.
- Generate revisions only after an accepted schema contract exists. Review generated DDL and data migration behavior; apply with the documented command in the intended environment.
- Async request sessions are closed after each request and rolled back if an exception escapes the request. They do not auto-commit; application services must commit explicit business transactions.
- Tests do not connect to `PUSTORA_DATABASE_URL`. Any future database integration suite must require a separately provisioned disposable database and reject production/staging targets before any migration or cleanup operation.
- Migration commands always act on the database named by `PUSTORA_DATABASE_URL`; verify the environment and target before running them. Never use an automated test to drop or reset a configured database.

## Error contract

Errors use the stable envelope documented in [API conventions](../../contracts/API_CONVENTIONS.md). Validation responses include only safe field locations, error codes, and generic messages; they never echo submitted values. Unexpected failures return a generic 500 response while the server logs the request ID, method, route template, and exception class without logging exception text or request data.
