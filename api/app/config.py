"""Configuración de la aplicación desde variables de entorno (pydantic-settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    web_origin: str = "http://localhost:3000"

    jwt_secret: str = "dev-no-usar-en-prod"
    jwt_exp_hours: int = 12

    seed_admin_email: str = "admin@local.test"
    seed_admin_password: str = "admin1234"

    database_url: str = "sqlite+aiosqlite:///./gds.db"

    # Cifrado de identificaciones y huella de búsqueda (vacias => modo dev inseguro)
    doc_encryption_key: str = ""
    doc_hmac_key: str = ""

    document_storage_path: str = "./data/documents"

    placapi_api_key: str = ""
    placapi_base_url: str = "https://placapi.com/api"

    # Modo fixture: forzado si no hay credencial del proveedor (E8)
    use_fixtures: bool = False

    @property
    def providers_live(self) -> bool:
        return bool(self.placapi_api_key) and not self.use_fixtures


@lru_cache
def get_settings() -> Settings:
    return Settings()
