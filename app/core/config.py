from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Family Tree API"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    SECRET_KEY: str
    DATABASE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
