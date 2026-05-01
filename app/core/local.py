from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import APP_DIR, BACKEND_DIR


class LocalSettings(BaseSettings):
    LOCAL_DATABASE_URL: str = "sqlite:///./livedomain.db"

    APPLICATIONINSIGHTS_ENABLED: bool = False
    APPLICATIONINSIGHTS_CONNECTION_STRING: str | None = None

    PHOTO_STORAGE_BACKEND: str = "local"
    AZURE_STORAGE_CONNECTION_STRING: str | None = None
    AZURE_STORAGE_ACCOUNT_URL: str | None = None
    AZURE_STORAGE_CONTAINER_NAME: str = "livedomain-photos"
    AZURE_STORAGE_PUBLIC_BASE_URL: str | None = None

    FEATURE_MAINTENANCE_ENABLED: bool = False
    FEATURE_MAINTENANCE_MESSAGE: str = (
        "La plataforma esta en mantenimiento local. Algunas funciones pueden tardar."
    )
    FEATURE_NEW_FEATURES_BANNER_ENABLED: bool = False
    FEATURE_NEW_FEATURES_BANNER_MESSAGE: str = (
        "Nuevas caracteristicas disponibles en local."
    )

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", APP_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return self.LOCAL_DATABASE_URL

    @property
    def login_messages(self) -> list[dict[str, str]]:
        messages = []

        if self.FEATURE_MAINTENANCE_ENABLED:
            messages.append(
                {
                    "type": "maintenance",
                    "message": self.FEATURE_MAINTENANCE_MESSAGE,
                }
            )

        if self.FEATURE_NEW_FEATURES_BANNER_ENABLED:
            messages.append(
                {
                    "type": "new_features",
                    "message": self.FEATURE_NEW_FEATURES_BANNER_MESSAGE,
                }
            )

        return messages


@lru_cache
def get_local_settings() -> LocalSettings:
    return LocalSettings()


local_settings = get_local_settings()
