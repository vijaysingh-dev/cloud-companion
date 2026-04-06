# app/services/redis.py

import json, logging
from typing import Optional, Any

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


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
        logger.debug("Redis connected")

    async def close(self):
        if self._client:
            await self._client.close()
            logger.debug("Redis disconnected")

    async def get(self, key: str) -> Optional[str]:
        value = await self.client.get(key)
        logger.debug(f"GET {key} → {'<None>' if value is None else repr(value[:80])}")
        return value

    async def set(self, key: str, value: str, ex: int = 0, **kwargs) -> Any:
        """
        Set a key. Returns the raw redis-py result so callers can inspect it.

        redis-py returns:
          True   — SET NX succeeded (key did not exist)
          None   — SET NX failed    (key already existed)
          'OK'   — plain SET succeeded
        """
        if ex > 0:
            kwargs["ex"] = ex

        result = await self.client.set(key, value, **kwargs)
        nx = kwargs.get("nx", False)
        ex_val = kwargs.get("ex", "—")
        logger.debug(
            f"SET {key} nx={nx} ex={ex_val} → {result!r}"
            + (f" value={repr(value[:60])}" if len(value) <= 60 else "")
        )
        return result

    async def delete(self, *keys: str) -> int:
        count = await self.client.delete(*keys)
        logger.debug(f"DEL {', '.join(keys)} → {count} removed")
        return count

    async def exists(self, *keys: str) -> int:
        count = await self.client.exists(*keys)
        logger.debug(f"EXISTS {', '.join(keys)} → {count}")
        return count

    async def expire(self, key: str, seconds: int) -> bool:
        result = await self.client.expire(key, seconds)
        logger.debug(f"EXPIRE {key} {seconds}s → {result}")
        return result

    async def ttl(self, key: str) -> int:
        result = await self.client.ttl(key)
        logger.debug(f"TTL {key} → {result}s")
        return result

    async def mget(self, *keys: str) -> list[Optional[str]]:
        values = await self.client.mget(*keys)
        hit_count = sum(1 for v in values if v is not None)
        logger.debug(f"MGET {len(keys)} keys → {hit_count} hits")
        return values

    async def keys(self, pattern: str) -> list[str]:
        result = await self.client.keys(pattern)
        logger.debug(f"KEYS {pattern!r} → {len(result)} matches")
        return result

    async def set_json(self, key: str, value: dict, ex: int = 0, **kwargs) -> Any:
        """Convenience: serialize dict → JSON string then SET."""
        return await self.set(key, json.dumps(value), ex=ex, **kwargs)

    async def get_json(self, key: str) -> Optional[dict]:
        """Convenience: GET then deserialize JSON string → dict."""
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"GET_JSON {key}: failed to decode — {e}")
            return None
