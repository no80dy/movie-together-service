from redis.asyncio import Redis


redis_client: Redis | None = None


async def get_redis_client() -> Redis:
    return redis_client
