from functools import lru_cache
from typing import Any
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int
    api_key: str
    spreadsheet_id: str
    cache_fp: str
    log_fp: str
    update_interval: timedelta

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def getenv(key: str) -> Any:
    return get_settings().__getattribute__(key)
