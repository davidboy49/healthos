from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://healthos:healthos@localhost:5432/healthos"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-change-me"
    token_encryption_key: str = "dev-token-key-change-me"
    garmin_client_id: str = ""
    garmin_client_secret: str = ""
    garmin_auth_url: str = "https://connect.garmin.com/oauthConfirm"
    garmin_token_url: str = "https://connect.garmin.com/oauth-service/oauth/access_token"
    garmin_api_base_url: str = "https://apis.garmin.com/wellness-api/rest"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

