from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestor Documental Social"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Proveedores de consulta documental
    PLACAPI_API_KEY: Optional[str] = None
    ARBOL_API_KEY: Optional[str] = None
    
    # Seguridad y Hashing (Ley 1581)
    DOC_HMAC_KEY: str = "local-insecure-hmac-key-for-dev-only"
    
    # Almacenamiento y bases de datos
    DATABASE_URL: str = "sqlite:///./dev.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    STORAGE_BUCKET_NAME: str = "gds-local-documents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
