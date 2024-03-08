import os
from datetime import timedelta
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "auth"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    POSTGRES_PASSWORD: str = "123qwe"
    POSTGRES_HOST: str = "database"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "users"
    POSTGRES_USER: str = "postgres"
    POSTGRES_SCHEME: str = "postgresql+asyncpg"


settings = Settings()

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Настройка конфигурации библиотеки Async FastAPI JWT Auth
class JWTSettings(BaseModel):
    authjwt_secret_key: str = "secret"
    # Хранить и получать JWT токены из заголовков
    authjwt_token_location: set = {"headers"}
    authjwt_header_name: str = "Authorization"
    authjwt_header_type: str = "Bearer"
    authjwt_access_token_expires: int = timedelta(minutes=10)
    authjwt_refresh_token_expires: int = timedelta(days=10)
    authjwt_cookie_csrf_protect: bool = False


# Настройки для сервисов авторизации по протоколу Auth2.0
class AuthServersSettings(BaseSettings):
    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env.auth"),
        env_file_encoding="utf-8",
    )
