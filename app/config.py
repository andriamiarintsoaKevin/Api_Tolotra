from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "*"  # <-- 1. Déclarer le champ ici pour valider ALLOWED_ORIGINS

    @property
    def origins_list(self) -> List[str]:
        raw = self.ALLOWED_ORIGINS.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    # 2. Configurer Pydantic pour tolérer d'éventuels champs supplémentaires ("ignore")
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"  # Empêche Pydantic de planter si une clé inconnue est dans le .env
    )

settings = Settings() # type: ignore
