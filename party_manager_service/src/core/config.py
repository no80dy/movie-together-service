import os.path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "party-manager-service"
    media_service_url: str = "http://localhost:8003/api/v1/hls"

    mongodb_url: str = "mongodb://localhost:27017/"
    mongodb_database_name: str = "partyDb"
    mongodb_notifications_collection_name: str = "parties"

    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_login: str
    rabbitmq_password: str

    jwt_secret_key: str = "secret"
    jwt_algorithm: str = "HS256"


settings = Settings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
