import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "queue"

    redis_host: str = 'redis'
    redis_port: int = 6379

    rabbitmq_host: str = 'rabbitmq'
    rabbitmq_port: int = '5672'
    rabbitmq_login: str = 'user'
    rabbitmq_password: str = 'rabbitmq'

    jwt_secret_key: str = "secret"
    jwt_algorithm: str = "HS256"

    auth_service_url: str = "http://auth:8000/auth/api/v1/users"

    # sentry_dsn: str
    rabbitmq_exchange_name: str = 'films_queues'
    rabbitmq_queue_name: str = 'film_queue'


settings = Settings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
