from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database - OBLIGATOIRE, doit être défini dans .env
    DATABASE_URL: str
    
    # API Keys - valeurs par défaut pour les headers
    API_KEY_HEADER: str = "X-API-Key"
    API_SECRET_HEADER: str = "X-API-Secret"
    
    # CORS - Origins autorisées (séparées par des virgules)
    # Valeur par défaut vide pour éviter les crashs, mais doit être configuré en production
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Retourne la liste des origines CORS."""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Log pour debug en production
        print(f"[Config] CORS Origins loaded: {origins}")
        return origins
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

DATABASE_URL = settings.DATABASE_URL
API_KEY_HEADER = settings.API_KEY_HEADER
API_SECRET_HEADER = settings.API_SECRET_HEADER
CORS_ORIGINS = settings.cors_origins_list
ENVIRONMENT = settings.ENVIRONMENT
