from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends
from redis.asyncio import Redis

from .redis import get_redis_client


class IStorage(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, expired_time: int) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def close(self):
        pass


class RedisStorage(IStorage):
    def __init__(self, connection: Redis) -> None:
        self.connection = connection

    async def get(self, key: str) -> str | None:
        return await self.connection.get(key)

    async def set(self, key: str, value: Any, expired_time: int) -> None:
        await self.connection.set(key, value, expired_time)

    async def delete(self, key: str) -> None:
        await self.connection.delete(key)

    async def close(self):
        await self.connection.close()


@lru_cache
def get_storage(client: Redis = Depends(get_redis_client)) -> IStorage:
    return RedisStorage(client)
