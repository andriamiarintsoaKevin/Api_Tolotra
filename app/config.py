from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "*" 

    # --- 1. SÉCURITÉ & JWT ---
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # --- 2. CONFIGURATION REDIS (OTP) ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None  # Utile si Redis a un mot de passe en prod

    # --- 3. GOOGLE OAUTH CLIENT IDS ---
    # Séparés par des virgules dans le .env (ex: GOOGLE_CLIENT_IDS="web_id,android_id")
    GOOGLE_CLIENT_IDS_RAW: str = ""

    @property
    def google_client_ids_list(self) -> List[str]:
        """Convertit la chaîne séparée par des virgules en liste nettoyée"""
        if not self.GOOGLE_CLIENT_IDS_RAW:
            return []
        return [client_id.strip() for client_id in self.GOOGLE_CLIENT_IDS_RAW.split(",") if client_id.strip()]

    @property
    def origins_list(self) -> List[str]:
        raw = self.ALLOWED_ORIGINS.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    # Configurer Pydantic pour tolérer d'éventuels champs supplémentaires ("ignore")
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings() # type: ignore
