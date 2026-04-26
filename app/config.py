from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def load_environment() -> None:
    """Load local .env values explicitly from application entrypoints."""

    load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is required")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings loaded from environment variables."""

    database_url: str
    test_database_url: str


def get_settings() -> Settings:
    return Settings(
        database_url=_required_env("DATABASE_URL"),
        test_database_url=os.getenv("TEST_DATABASE_URL") or _required_env("DATABASE_URL"),
    )


settings = get_settings()
