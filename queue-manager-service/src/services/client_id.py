from functools import lru_cache

from core.config import settings
from cryptography.fernet import Fernet
from schemas.entity import FilmTogether


class ClientIDService:
    """Client_id есть закодированная строка film_id + ' ' + user_id + ' ' + user_agent."""

    def __init__(self): ...

    @staticmethod
    def _encrypt(message: bytes, key: bytes) -> bytes:
        return Fernet(settings.client_id_key).encrypt(message)

    @staticmethod
    def _decrypt(token: bytes, key: bytes) -> bytes:
        return Fernet(settings.client_id_key).decrypt(token)

    @staticmethod
    def make_client_id(film_together: FilmTogether) -> str:
        """Создание уникального идентификатора для клиента."""
        film_together_dto = film_together.model_dump()
        film_id = film_together_dto.get("film_id")
        user_id = film_together_dto.get("user_id")
        user_agent = film_together_dto.get("user_agent")

        client_id_raw = (
            str(film_id) + " " + str(user_id) + " " + str(user_agent)
        )

        return ClientIDService._encrypt(
            bytes(client_id_raw, "utf-8"), settings.client_id_key
        ).decode("utf-8")

    @staticmethod
    def get_film_id_from_client_id(
        client_id: str,
    ) -> str:
        client_id_raw = ClientIDService._decrypt(
            bytes(client_id, "utf-8"), settings.client_id_key
        ).decode("utf-8")
        return client_id_raw.split(" ")[0]

    @staticmethod
    def get_user_id_from_client_id(
        client_id: str,
    ) -> str:
        client_id_raw = ClientIDService._decrypt(
            bytes(client_id, "utf-8"), settings.client_id_key
        ).decode("utf-8")
        return client_id_raw.split(" ")[1]

    @staticmethod
    def get_user_agent_from_client_id(
        client_id: str,
    ) -> str:
        client_id_raw = ClientIDService._decrypt(
            bytes(client_id, "utf-8"), settings.client_id_key
        ).decode("utf-8")
        return client_id_raw.split(" ")[2]


@lru_cache
def get_client_id_service():
    return ClientIDService()
