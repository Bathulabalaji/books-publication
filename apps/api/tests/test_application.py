import logging
from uuid import UUID

from _pytest.logging import LogCaptureFixture
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pytest import MonkeyPatch

from pustora_api.config import Settings
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


def test_openapi_metadata_and_paths_are_versioned() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "PUSTORA API"
    assert schema["info"]["version"] == "0.1.0"
    assert "/api/v1/health" in schema["paths"]
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
