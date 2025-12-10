from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lgk_profile_db"
    API_KEY_HEADER: str = "X-API-Key"
    API_SECRET_HEADER: str = "X-API-Secret"

    class Config:
        env_file = ".env"


settings = Settings()

DATABASE_URL = settings.DATABASE_URL
API_KEY_HEADER = settings.API_KEY_HEADER
API_SECRET_HEADER = settings.API_SECRET_HEADER
