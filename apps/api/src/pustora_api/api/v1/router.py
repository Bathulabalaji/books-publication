from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from pustora_api.config import Settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str


def current_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health(settings: Annotated[Settings, Depends(current_settings)]) -> HealthResponse:
    return HealthResponse(status="ok", service=settings.service_name)
