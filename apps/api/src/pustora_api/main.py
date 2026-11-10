import logging
from collections.abc import Mapping
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.exceptions import HTTPException as StarletteHTTPException

from pustora_api.api.v1.router import router as v1_router
from pustora_api.config import Settings, get_settings
from pustora_api.database import (
    create_database_engine,
    create_session_factory,
)
from pustora_api.errors import ApplicationError, error_response
from pustora_api.middleware import RequestIdMiddleware

logger = logging.getLogger("pustora.api")

VALIDATION_MESSAGES: Mapping[str, str] = {
    "missing": "Field is required.",
    "extra_forbidden": "Unexpected field.",
    "string_type": "A string value is required.",
    "int_type": "An integer value is required.",
    "float_type": "A numeric value is required.",
    "bool_type": "A boolean value is required.",
    "json_invalid": "The request body must be valid JSON.",
}


def _request_id(request: Request) -> str:
    return request.scope["state"]["request_id"]


def _validation_details(exc: RequestValidationError) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for issue in exc.errors():
        error_type = str(issue.get("type", "invalid"))
        details.append(
            {
                "location": [str(part) for part in issue.get("loc", ())],
                "code": error_type,
                "message": VALIDATION_MESSAGES.get(error_type, "Invalid value."),
            }
        )
    return details


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        try:
            yield
        finally:
            engine: AsyncEngine | None = application.state.db_engine
            if engine is not None:
                await engine.dispose()

    application = FastAPI(
        title="PUSTORA API",
        summary="API for the PUSTORA books publication platform.",
        description=(
            "Versioned HTTP API for PUSTORA. Business capabilities are added by vertical slice."
        ),
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    application.state.settings = app_settings
    application.state.db_engine = create_database_engine(app_settings)
    application.state.db_session_factory = (
        create_session_factory(application.state.db_engine)
        if application.state.db_engine is not None
        else None
    )
    application.add_middleware(RequestIdMiddleware)
    application.include_router(v1_router, prefix="/api/v1")

    @application.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                code=exc.code,
                message=exc.message,
                request_id=_request_id(request),
            ),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_response(
                code="VALIDATION_ERROR",
                message="Request validation failed.",
                request_id=_request_id(request),
                details=_validation_details(exc),
            ),
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code, message = {
            404: ("NOT_FOUND", "Resource not found."),
            405: ("METHOD_NOT_ALLOWED", "Method not allowed."),
        }.get(exc.status_code, ("HTTP_ERROR", "The request could not be completed."))
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(code=code, message=message, request_id=_request_id(request)),
            headers=exc.headers,
        )

    @application.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _request_id(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", "<unmatched>")
        logger.error(
            "Unhandled API error request_id=%s method=%s route=%s exception_type=%s",
            request_id,
            request.method,
            route_path,
            type(exc).__name__,
            extra={
                "request_id": request_id,
                "method": request.method,
                "route": route_path,
                "exception_type": type(exc).__name__,
            },
        )
        return JSONResponse(
            status_code=500,
            content=error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred.",
                request_id=request_id,
            ),
            headers={"X-Request-ID": request_id},
        )

    return application


app = create_app()
