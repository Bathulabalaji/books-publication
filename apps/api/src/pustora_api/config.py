from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PUSTORA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    environment: Literal["local", "test", "staging", "production"] = "local"
    environment: Literal["local", "test", "staging", "production"] = "local"
    service_name: str = Field(default="pustora-api", min_length=1, max_length=80)


@lru_cache
def get_settings() -> Settings:
    return Settings()
