from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


DEFAULT_DATABASE_URL = "postgresql+asyncpg://splitshot:splitshot@localhost:5432/splitshot"


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    test_database_url: str = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))


settings = Settings()
