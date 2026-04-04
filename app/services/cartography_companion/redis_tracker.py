import json
import logging
from typing import Optional
from datetime import datetime, timezone

from app.services.redis import RedisService

logger = logging.getLogger(__name__)

# Key patterns
_LOCK_KEY = "sync:lock:{account_id}:{service_key}"
_STATUS_KEY = "sync:status:{account_id}:{service_key}"
_PROGRESS_KEY = "sync:progress:{account_id}"  # hash of all in-progress services

LOCK_TTL_SECONDS = 600  # 10 min max for a single service sync
STATUS_TTL_SECONDS = 86400  # 24h — live status expires, Neo4j has the permanent record
INVALID_TTL = 3600  # 1 hour — bad keys shouldn't pollute status forever


class RedisSyncTracker:
    """
    Live sync state in Redis.
    - Distributed lock per account+service (prevents duplicate syncs)
    - Fast status reads without hitting Neo4j
    """

    def __init__(self, redis: RedisService):
        self.redis = redis

    def _lock_key(self, account_id: str, service_key: str) -> str:
        return _LOCK_KEY.format(account_id=account_id, service_key=service_key)

    def _status_key(self, account_id: str, service_key: str) -> str:
        return _STATUS_KEY.format(account_id=account_id, service_key=service_key)

    async def acquire_lock(
        self,
        account_id: str,
        service_key: str,
        sync_run_id: str,
    ) -> bool:
        """
        Returns True if lock acquired (safe to proceed).
        Returns False if another sync is already running for this service.
        Uses SET NX EX — atomic, no race condition.
        """
        key = self._lock_key(account_id, service_key)
        acquired = await self.redis.set(
            key,
            sync_run_id,
            nx=True,  # only set if not exists
            ex=LOCK_TTL_SECONDS,
        )
        return acquired is not None

    async def release_lock(self, account_id: str, service_key: str) -> None:
        key = self._lock_key(account_id, service_key)
        await self.redis.delete(key)

    async def set_invalid(self, account_id: str, service_key: str, reason: str) -> None:
        """Mark a service key as invalid (unknown/misconfigured) in Redis."""
        key = self._status_key(account_id, service_key)
        payload = {
            "status": "invalid",
            "error": reason,
            "recorded_at": datetime.utcnow().isoformat(),
        }
        await self.redis.set(key, json.dumps(payload), ex=INVALID_TTL)

    async def set_status(
        self,
        account_id: str,
        service_key: str,
        status: str,
        extra: Optional[dict] = None,
    ) -> None:
        key = self._status_key(account_id, service_key)
        payload = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **(extra or {}),
        }
        await self.redis.set(key, json.dumps(payload), ex=STATUS_TTL_SECONDS)

    async def get_status(
        self,
        account_id: str,
        service_key: str,
    ) -> Optional[dict]:
        key = self._status_key(account_id, service_key)
        val = await self.redis.get(key)
        return json.loads(val) if val else None

    async def get_statuses(
        self,
        account_id: str,
        service_keys: list[str],
    ) -> dict[str, dict]:
        """
        Bulk-fetch Redis state for a list of service keys.
        Returns {service_key: state_dict} for keys that have an entry.
        Keys with no Redis entry are omitted.
        """
        if not service_keys:
            return {}

        redis_keys = [self._status_key(account_id, k) for k in service_keys]
        values = await self.redis.client.mget(*redis_keys)

        result: dict[str, dict] = {}
        for service_key, val in zip(service_keys, values):
            if val:
                try:
                    result[service_key] = json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    pass
        return result

    async def get_all_statuses(self, account_id: str) -> dict[str, dict]:
        """Returns all cached service statuses for an account."""
        pattern = _STATUS_KEY.format(account_id=account_id, service_key="*")
        keys = await self.redis.client.keys(pattern)
        if not keys:
            return {}
        values = await self.redis.client.mget(*keys)
        result = {}
        for key, val in zip(keys, values):
            if val:
                service_key = key.decode().split(":")[-1]
                result[service_key] = json.loads(val)
        return result

    async def is_running(self, account_id: str, service_key: str) -> bool:
        key = self._lock_key(account_id, service_key)
        return await self.redis.client.exists(key) == 1
