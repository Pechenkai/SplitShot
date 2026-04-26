from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = _require_env("DATABASE_URL")
    test_database_url: str = _require_env("TEST_DATABASE_URL")


settings = Settings()
