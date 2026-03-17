import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings


class RedisService:
    def __init__(self):
        self.client: Redis | None = None

    async def connect(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        if self.client:
            await self.client.close()

    def _get_client(self) -> Redis:
        if not self.client:
            raise RuntimeError("Redis not connected")
        return self.client

    async def get(self, key: str):
        return await self._get_client().get(key)

    async def set(self, key: str, value: str, ttl: int = 0):
        client = self._get_client()

        if ttl > 0:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)
