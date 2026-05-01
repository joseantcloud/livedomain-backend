from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import APP_DIR, BACKEND_DIR


class CloudSettings(BaseSettings):
    AZURE_SQLALCHEMY_DATABASE_URL: str | None = None
    AZURE_SQL_CONNECTION_STRING: str | None = None
    AZURE_SQL_SERVER: str | None = None
    AZURE_SQL_DATABASE: str | None = None
    AZURE_SQL_USERNAME: str | None = None
    AZURE_SQL_PASSWORD: str | None = None
    AZURE_SQL_DRIVER: str = "ODBC Driver 18 for SQL Server"

    APPLICATIONINSIGHTS_CONNECTION_STRING: str | None = None
    APPLICATIONINSIGHTS_ENABLED: bool = True

    PHOTO_STORAGE_BACKEND: str = "azure_blob"
    AZURE_STORAGE_CONNECTION_STRING: str | None = None
    AZURE_STORAGE_ACCOUNT_URL: str | None = None
    AZURE_STORAGE_CONTAINER_NAME: str = "livedomain-photos"
    AZURE_STORAGE_PUBLIC_BASE_URL: str | None = None

    APP_CONFIGURATION_ENABLED: bool = True
    APP_CONFIGURATION_CONNECTION_STRING: str | None = None
    APP_CONFIGURATION_ENDPOINT: str | None = None
    APP_CONFIGURATION_LABEL: str | None = None
    APP_CONFIGURATION_FAIL_FAST: bool = False
    APP_CONFIG_FEATURE_MAINTENANCE_KEY: str = "MaintenanceMode"
    APP_CONFIG_FEATURE_NEW_FEATURES_BANNER_KEY: str = "NewFeaturesBanner"

    FEATURE_MAINTENANCE_ENABLED: bool = False
    FEATURE_MAINTENANCE_MESSAGE: str = (
        "La plataforma esta en mantenimiento. Algunas funciones pueden tardar."
    )
    FEATURE_NEW_FEATURES_BANNER_ENABLED: bool = False
    FEATURE_NEW_FEATURES_BANNER_MESSAGE: str = (
        "Nuevas caracteristicas disponibles."
    )

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", APP_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        if self.AZURE_SQLALCHEMY_DATABASE_URL:
            return self.AZURE_SQLALCHEMY_DATABASE_URL

        if self.AZURE_SQL_CONNECTION_STRING:
            encoded_connection = quote_plus(self.AZURE_SQL_CONNECTION_STRING)
            return f"mssql+pyodbc:///?odbc_connect={encoded_connection}"

        required_values = [
            self.AZURE_SQL_SERVER,
            self.AZURE_SQL_DATABASE,
            self.AZURE_SQL_USERNAME,
            self.AZURE_SQL_PASSWORD,
        ]

        if all(required_values):
            encoded_password = quote_plus(self.AZURE_SQL_PASSWORD or "")
            encoded_driver = quote_plus(self.AZURE_SQL_DRIVER)
            return (
                f"mssql+pyodbc://{self.AZURE_SQL_USERNAME}:{encoded_password}"
                f"@{self.AZURE_SQL_SERVER}:1433/{self.AZURE_SQL_DATABASE}"
                f"?driver={encoded_driver}&Encrypt=yes&TrustServerCertificate=no"
            )

        raise ValueError(
            "Cloud requiere AZURE_SQLALCHEMY_DATABASE_URL, "
            "AZURE_SQL_CONNECTION_STRING o los valores AZURE_SQL_*."
        )

    def is_feature_enabled(self, feature_name: str, fallback: bool = False) -> bool:
        if not self.APP_CONFIGURATION_ENABLED:
            return fallback

        if not (
            self.APP_CONFIGURATION_CONNECTION_STRING
            or self.APP_CONFIGURATION_ENDPOINT
        ):
            return fallback

        try:
            from azure.appconfiguration.provider import SettingSelector, load

            load_options = {
                "feature_flags_enabled": True,
            }

            if self.APP_CONFIGURATION_CONNECTION_STRING:
                load_options["connection_string"] = (
                    self.APP_CONFIGURATION_CONNECTION_STRING
                )
            else:
                from azure.identity import DefaultAzureCredential

                load_options["endpoint"] = self.APP_CONFIGURATION_ENDPOINT
                load_options["credential"] = DefaultAzureCredential()

            if self.APP_CONFIGURATION_LABEL:
                load_options["feature_flag_selectors"] = [
                    SettingSelector(
                        key_filter="*",
                        label_filter=self.APP_CONFIGURATION_LABEL,
                    )
                ]

            config = load(**load_options)
            feature_flags = (
                config.get("feature_management", {})
                .get("feature_flags", {})
            )
            feature_flag = feature_flags.get(feature_name, {})

            return bool(feature_flag.get("enabled", fallback))
        except Exception:
            if self.APP_CONFIGURATION_FAIL_FAST:
                raise

            return fallback

    @property
    def login_messages(self) -> list[dict[str, str]]:
        maintenance_enabled = self.is_feature_enabled(
            self.APP_CONFIG_FEATURE_MAINTENANCE_KEY,
            fallback=self.FEATURE_MAINTENANCE_ENABLED,
        )
        new_features_enabled = self.is_feature_enabled(
            self.APP_CONFIG_FEATURE_NEW_FEATURES_BANNER_KEY,
            fallback=self.FEATURE_NEW_FEATURES_BANNER_ENABLED,
        )

        messages = []

        if maintenance_enabled:
            messages.append(
                {
                    "type": "maintenance",
                    "message": self.FEATURE_MAINTENANCE_MESSAGE,
                }
            )

        if new_features_enabled:
            messages.append(
                {
                    "type": "new_features",
                    "message": self.FEATURE_NEW_FEATURES_BANNER_MESSAGE,
                }
            )

        return messages


@lru_cache
def get_cloud_settings() -> CloudSettings:
    return CloudSettings()


cloud_settings = get_cloud_settings()
