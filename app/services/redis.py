import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings


class RedisService:
    def __init__(self):
        self._client: Redis | None = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis not initialized. Call connect() first.")
        return self._client

    async def connect(self):
        self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        if self._client:
            await self._client.close()

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: int = 0, *args, **kwargs):
        if ex > 0:
            kwargs.setdefault("ex", ex)

        await self.client.set(key, value, *args, **kwargs)

    async def delete(self, key: str, *args, **kwargs):
        await self.client.delete(key, *args, **kwargs)
