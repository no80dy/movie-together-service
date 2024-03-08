import json
import uuid
from abc import ABC, abstractmethod
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from integration.redis import get_redis_client


class ICache(ABC):
    @abstractmethod
    async def get(self, key: uuid.UUID):
        pass

    @abstractmethod
    async def set(self, key: uuid.UUID, value: dict):
        pass


class RedisCache(ICache):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client

    async def get(self, key: uuid.UUID):
        return await self.redis_client.get(str(key))

    async def set(self, key: uuid.UUID, value: dict):
        await self.redis_client.set(str(key), json.dumps(value))


def get_cache(
    redis_client: Annotated[aioredis.Redis, Depends(get_redis_client)],
):
    return RedisCache(redis_client)
