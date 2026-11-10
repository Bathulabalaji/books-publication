from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PUSTORA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["local", "test", "staging", "production"] = "local"
    service_name: str = Field(default="pustora-api", min_length=1, max_length=80)
    database_url: SecretStr | None = None

    @model_validator(mode="after")
    def validate_database_url(self) -> "Settings":
        if self.environment in {"staging", "production"} and self.database_url is None:
            raise ValueError("PUSTORA_DATABASE_URL is required in staging and production.")

        if self.database_url is not None:
            try:
                url = make_url(self.database_url.get_secret_value())
            except ArgumentError as exc:
                raise ValueError("PUSTORA_DATABASE_URL must be a valid PostgreSQL URL.") from exc

            if url.drivername != "postgresql+asyncpg" or not url.host or not url.database:
                raise ValueError(
                    "PUSTORA_DATABASE_URL must use postgresql+asyncpg and include "
                    "a host and database."
                )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
