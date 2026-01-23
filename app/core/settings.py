from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    #app
    APP_NAME:str = "Commico"
    DEBUG:bool = False

    #OAuth
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    GITHUB_REDIRECT_URI: str | None = None

    #JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 120.0
    SECRET_KEY: str | None = None
    ALGORITHM: str = "HS256"

    #DB
    POSTGRES_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
