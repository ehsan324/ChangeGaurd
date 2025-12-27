import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    redis_url: str

def get_settings() -> Settings:
    """
    Reads environment variables and
    returns an immutable Settings object.
    """
    return Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        database_url=os.getenv("DATABASE_URL", ""),
        redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),

    )