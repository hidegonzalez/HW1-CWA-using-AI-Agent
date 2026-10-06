import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CWA_API_KEY: str = os.getenv("CWA_API_KEY", "")
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "600"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
