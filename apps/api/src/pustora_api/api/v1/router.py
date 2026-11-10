import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from pustora_api.config import Settings
from pustora_api.database import check_database_connection
from pustora_api.errors import ApplicationError

router = APIRouter()
logger = logging.getLogger("pustora.api")


class HealthResponse(BaseModel):
    status: str
    service: str


def current_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health(settings: Annotated[Settings, Depends(current_settings)]) -> HealthResponse:
    return HealthResponse(status="ok", service=settings.service_name)


@router.get("/ready", response_model=HealthResponse, tags=["system"])
async def readiness(request: Request) -> HealthResponse:
    engine: AsyncEngine | None = request.app.state.db_engine
    if engine is None:
        raise ApplicationError(
            code="DATABASE_NOT_CONFIGURED",
            message="Database service is unavailable.",
            status_code=503,
        )
    try:
        await check_database_connection(engine)
    except SQLAlchemyError as exc:
        request_id = request.scope["state"]["request_id"]
        logger.error(
            "Database readiness check failed request_id=%s exception_type=%s",
            request_id,
            type(exc).__name__,
            extra={"request_id": request_id, "exception_type": type(exc).__name__},
        )
        raise ApplicationError(
            code="DATABASE_UNAVAILABLE",
            message="Database service is unavailable.",
            status_code=503,
        ) from exc

    settings: Settings = request.app.state.settings
    return HealthResponse(status="ok", service=settings.service_name)
