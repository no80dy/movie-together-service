import json
import logging
from functools import lru_cache

from db.users import users_db
from models.models import User


class UserService:
    @staticmethod
    async def check_user_exist(
        username: str,
        password: str,
    ) -> User | None:
        if username in users_db:
            if password == users_db[username]["password"]:
                return User(**users_db[username])
        return None


@lru_cache()
def get_user_service() -> UserService:
    return UserService()
