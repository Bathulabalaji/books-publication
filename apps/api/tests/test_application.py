import asyncio
import logging
from uuid import UUID

from _pytest.logging import LogCaptureFixture
from fastapi import Request
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pytest import MonkeyPatch
from sqlalchemy.exc import SQLAlchemyError

from pustora_api.config import Settings
from pustora_api.database import get_db_session
from pustora_api.errors import ApplicationError
from pustora_api.main import create_app


def test_health_route_is_versioned_and_uses_explicit_test_settings() -> None:
    client = TestClient(create_app(Settings(environment="test", service_name="test-api")))

    response = client.get("/api/v1/health", headers={"X-Request-ID": "caller-controlled-id"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "test-api"}
    assert UUID(response.headers["x-request-id"])
    assert response.headers["x-request-id"] != "caller-controlled-id"


def test_settings_load_from_environment_without_secret_fields(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv("PUSTORA_ENVIRONMENT", "test")
    monkeypatch.setenv("PUSTORA_SERVICE_NAME", "test-service")

    settings = Settings(_env_file=None)

    assert settings.environment == "test"
    assert settings.service_name == "test-service"
    assert not hasattr(settings, "secret_key")


def test_settings_reject_invalid_environment() -> None:
    try:
        Settings(environment="production-ish")
    except ValidationError as exc:
        assert any(error["loc"] == ("environment",) for error in exc.errors())
    else:
        raise AssertionError("Invalid environment should fail settings validation.")


def test_staging_and_production_require_database_url() -> None:
    for environment in ("staging", "production"):
        try:
            Settings(environment=environment)
        except ValidationError as exc:
            assert "PUSTORA_DATABASE_URL" in str(exc)
        else:
            raise AssertionError(f"{environment} must require PUSTORA_DATABASE_URL.")


def test_database_url_is_validated_and_secret_is_not_repr_exposed() -> None:
    settings = Settings(
        environment="local",
        database_url="postgresql+asyncpg://pustora:secret-value@localhost:5432/pustora_local",
    )

    assert "secret-value" not in repr(settings)

    try:
        Settings(environment="local", database_url="sqlite:///not-postgres.db")
    except ValidationError as exc:
        assert "postgresql+asyncpg" in str(exc)
    else:
        raise AssertionError("Non-PostgreSQL URLs must be rejected.")


def test_openapi_metadata_and_paths_are_versioned() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "PUSTORA API"
    assert schema["info"]["version"] == "0.1.0"
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/ready" in schema["paths"]
    assert not any(path in schema["paths"] for path in ("/login", "/books", "/orders"))


def test_validation_error_uses_stable_safe_envelope() -> None:
    app = create_app(Settings(environment="test"))

    @app.get("/api/v1/test-validation")
    async def validation_fixture(required: int) -> dict[str, int]:
        return {"required": required}

    response = TestClient(app).get(
        "/api/v1/test-validation",
        params={"required": "never-echo-this"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "request_id": response.headers["x-request-id"],
            "details": [
                {
                    "location": ["query", "required"],
                    "code": "int_parsing",
                    "message": "Invalid value.",
                }
            ],
        }
    }
    assert "never-echo-this" not in response.text


def test_application_error_uses_public_error_contract() -> None:
    app = create_app(Settings(environment="test"))

    @app.get("/api/v1/test-conflict")
    async def conflict_fixture() -> None:
        raise ApplicationError(
            code="CONFLICT",
            message="The operation cannot be completed.",
            status_code=409,
        )

    response = TestClient(app).get("/api/v1/test-conflict")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"
    assert response.json()["error"]["message"] == "The operation cannot be completed."
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_unexpected_error_is_redacted_logged_and_correlated(
    caplog: LogCaptureFixture,
) -> None:
    app = create_app(Settings(environment="test"))

    @app.get("/api/v1/test-crash")
    async def failure_fixture() -> None:
        raise RuntimeError("sensitive exception detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        with caplog.at_level(logging.ERROR, logger="pustora.api"):
            response = client.get("/api/v1/test-crash")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "request_id": response.headers["x-request-id"],
        }
    }
    assert "sensitive exception detail" not in response.text
    assert "sensitive exception detail" not in caplog.text
    assert response.headers["x-request-id"] in caplog.text
    error_record = next(record for record in caplog.records if record.name == "pustora.api")
    assert error_record.request_id == response.headers["x-request-id"]
    assert error_record.method == "GET"
    assert error_record.route == "/api/v1/test-crash"
    assert error_record.exception_type == "RuntimeError"


def test_not_found_response_does_not_expose_framework_detail() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert response.json()["error"]["message"] == "Resource not found."
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_readiness_without_database_is_a_safe_503() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATABASE_NOT_CONFIGURED"
    assert response.json()["error"]["message"] == "Database service is unavailable."
    assert "database_url" not in response.text


class FakeDatabaseConnection:
    async def execute(self, statement: object) -> None:
        self.statement = str(statement)


class FakeDatabaseConnectionContext:
    def __init__(self, *, error: Exception | None = None) -> None:
        self.error = error
        self.connection = FakeDatabaseConnection()
        self.closed = False

    async def __aenter__(self) -> FakeDatabaseConnection:
        if self.error is not None:
            raise self.error
        return self.connection

    async def __aexit__(self, *exc_info: object) -> None:
        self.closed = True


class FakeDatabaseEngine:
    def __init__(self, *, error: Exception | None = None) -> None:
        self.connection_context = FakeDatabaseConnectionContext(error=error)

    def connect(self) -> FakeDatabaseConnectionContext:
        return self.connection_context


def test_readiness_executes_query_and_returns_only_service_status() -> None:
    app = create_app(Settings(environment="test"))
    engine = FakeDatabaseEngine()
    app.state.db_engine = engine

    response = TestClient(app).get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pustora-api"}
    assert engine.connection_context.connection.statement == "SELECT 1"
    assert engine.connection_context.closed


def test_readiness_database_failure_is_redacted_and_logged(
    caplog: LogCaptureFixture,
) -> None:
    app = create_app(Settings(environment="test"))
    app.state.db_engine = FakeDatabaseEngine(
        error=SQLAlchemyError("postgres://user:secret@host/database"),
    )

    with caplog.at_level(logging.ERROR, logger="pustora.api"):
        response = TestClient(app).get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"
    assert "secret" not in response.text
    assert "secret" not in caplog.text
    assert response.headers["x-request-id"] in caplog.text


class FakeSession:
    def __init__(self) -> None:
        self.rollback_count = 0

    async def rollback(self) -> None:
        self.rollback_count += 1


class FakeSessionContext:
    def __init__(self) -> None:
        self.session = FakeSession()
        self.closed = False

    async def __aenter__(self) -> FakeSession:
        return self.session

    async def __aexit__(self, *exc_info: object) -> None:
        self.closed = True


class FakeSessionFactory:
    def __init__(self) -> None:
        self.context = FakeSessionContext()

    def __call__(self) -> FakeSessionContext:
        return self.context


def test_database_session_is_closed_after_successful_request() -> None:
    app = create_app(Settings(environment="test"))
    factory = FakeSessionFactory()
    app.state.db_session_factory = factory
    request = Request({"type": "http", "app": app, "state": {}})
    dependency = get_db_session(request)

    async def exercise_session() -> None:
        assert await anext(dependency) is factory.context.session
        try:
            await anext(dependency)
        except StopAsyncIteration:
            pass

    asyncio.run(exercise_session())

    assert factory.context.closed
    assert factory.context.session.rollback_count == 0


def test_database_session_rolls_back_and_closes_after_request_error() -> None:
    app = create_app(Settings(environment="test"))
    factory = FakeSessionFactory()
    app.state.db_session_factory = factory
    request = Request({"type": "http", "app": app, "state": {}})
    dependency = get_db_session(request)

    async def exercise_failed_session() -> None:
        assert await anext(dependency) is factory.context.session
        try:
            await dependency.athrow(RuntimeError("request failed"))
        except RuntimeError as exc:
            assert str(exc) == "request failed"

    asyncio.run(exercise_failed_session())

    assert factory.context.session.rollback_count == 1
    assert factory.context.closed


def test_database_session_fails_closed_when_not_configured() -> None:
    app = create_app(Settings(environment="test"))
    request = Request({"type": "http", "app": app, "state": {}})
    dependency = get_db_session(request)

    async def exercise_unconfigured_session() -> None:
        try:
            await anext(dependency)
        except ApplicationError as exc:
            assert exc.code == "DATABASE_NOT_CONFIGURED"
            assert exc.status_code == 503
        else:
            raise AssertionError("Database session must fail closed when no factory is configured.")

    asyncio.run(exercise_unconfigured_session())
