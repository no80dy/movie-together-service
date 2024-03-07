import os
from datetime import timedelta

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    PROJECT_NAME: str = "mock-auth"


settings = Settings()


# Настройка конфигурации библиотеки Async FastAPI JWT Auth
class JWTSettings(BaseModel):
    authjwt_secret_key: str = "secret"

    # Хранить и получать JWT токены из заголовков
    # authjwt_token_location: set = {'headers'}
    # authjwt_header_name: str = "Authorization"
    # authjwt_header_type: str = "Bearer"
    authjwt_token_location: set = {"cookies"}

    authjwt_access_token_expires: int = timedelta(minutes=10)
    authjwt_refresh_token_expires: int = timedelta(days=10)
    authjwt_cookie_csrf_protect: bool = False
