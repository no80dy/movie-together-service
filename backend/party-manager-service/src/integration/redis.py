import redis.asyncio as aioredis


redis_client: aioredis.Redis | None = None


def get_redis_client() -> aioredis.Redis:
	return redis_client
