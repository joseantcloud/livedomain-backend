from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.cloud import cloud_settings
from app.core.local import local_settings
from app.core.paths import APP_DIR, BACKEND_DIR


class RuntimeSelector(BaseSettings):
    LOCAL: bool = True

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", APP_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


runtime_selector = RuntimeSelector()
active_environment_settings = (
    local_settings if runtime_selector.LOCAL else cloud_settings
)


class Settings(BaseSettings):
    APP_NAME: str = "LiveDomain API"
    ENVIRONMENT: str = "local"
    LOCAL: bool = runtime_selector.LOCAL

    DATABASE_URL: str = Field(
        default=active_environment_settings.database_url,
        validation_alias="APP_DATABASE_URL",
    )

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    FRONTEND_BASE_URL: str = "http://localhost:5173"
    LOGIN_MESSAGES: list[dict[str, str]] = Field(
        default_factory=list,
        validation_alias="APP_LOGIN_MESSAGES",
    )
    APPLICATIONINSIGHTS_ENABLED: bool = (
        active_environment_settings.APPLICATIONINSIGHTS_ENABLED
    )
    APPLICATIONINSIGHTS_CONNECTION_STRING: str | None = (
        active_environment_settings.APPLICATIONINSIGHTS_CONNECTION_STRING
    )
    PHOTO_STORAGE_BACKEND: str = active_environment_settings.PHOTO_STORAGE_BACKEND
    AZURE_STORAGE_CONNECTION_STRING: str | None = (
        active_environment_settings.AZURE_STORAGE_CONNECTION_STRING
    )
    AZURE_STORAGE_ACCOUNT_URL: str | None = (
        active_environment_settings.AZURE_STORAGE_ACCOUNT_URL
    )
    AZURE_STORAGE_CONTAINER_NAME: str = (
        active_environment_settings.AZURE_STORAGE_CONTAINER_NAME
    )
    AZURE_STORAGE_PUBLIC_BASE_URL: str | None = (
        active_environment_settings.AZURE_STORAGE_PUBLIC_BASE_URL
    )

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "no-reply@livedomain.com"
    SMTP_USE_TLS: bool = True

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", APP_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def get_login_messages() -> list[dict[str, str]]:
    return active_environment_settings.login_messages
