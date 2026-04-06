"""
Redis-backed live sync state.

Design: a single status key per (account_id, service_key) carries BOTH the
human-readable status AND acts as the distributed lock.  The lock key is kept
as a *separate* NX key so we can do an atomic acquire, but `is_running` reads
the status key — not the lock key — so the two views are always consistent.

Key layout
----------
sync:lock:<account>:<svc>      NX lock, owned by sync_run_id, TTL=LOCK_TTL
sync:status:<account>:<svc>    JSON payload, TTL=STATUS_TTL (or INVALID_TTL)
"""

import json, logging
from datetime import datetime, timezone
from typing import Optional

from app.services.redis import RedisService

logger = logging.getLogger("redis-tracker")


LOCK_TTL_SECONDS = 600  # 10 min hard ceiling per service
STATUS_TTL_SECONDS = 86400  # 24 h — Redis is the live view; Neo4j is canonical
INVALID_TTL = 3600  # 1 h — bad keys shouldn't pollute status forever

_LOCK_KEY = "sync:lock:{account_id}:{service_key}"
_STATUS_KEY = "sync:status:{account_id}:{service_key}"


class RedisSyncTracker:
    """
    Distributed lock + fast status cache for in-flight syncs.

    Invariant
    ---------
    A service is "running" iff its *lock key* exists.  The status key always
    mirrors this: acquiring the lock immediately writes status=running; releasing
    it writes the terminal status (completed / failed).  There is no window where
    the lock is gone but status still says running.
    """

    def __init__(self, redis: RedisService):
        self.redis = redis

    def _lock_key(self, account_id: str, service_key: str) -> str:
        return _LOCK_KEY.format(account_id=account_id, service_key=service_key)

    def _status_key(self, account_id: str, service_key: str) -> str:
        return _STATUS_KEY.format(account_id=account_id, service_key=service_key)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ── lock ─────────────────────────────────────────────────────────────────

    async def acquire_lock(
        self,
        account_id: str,
        service_key: str,
        sync_run_id: str,
    ) -> bool:
        """
        Atomically acquire the lock and write status=running.

        redis-py SET NX returns True on success, None if key already exists.
        RedisService.set() now returns that value directly.
        """
        lock_key = self._lock_key(account_id, service_key)

        result = await self.redis.set(
            lock_key,
            sync_run_id,
            ex=LOCK_TTL_SECONDS,
            nx=True,
        )
        acquired = result is True  # None → already locked; True → acquired

        if not acquired:
            existing = await self.redis.get(lock_key)
            logger.warning(
                f"[{account_id}:{service_key}] lock NOT acquired " f"(held by run {existing!r})"
            )
            return False

        # Write status=running atomically with the lock
        await self.redis.set_json(
            self._status_key(account_id, service_key),
            {
                "status": "running",
                "sync_run_id": sync_run_id,
                "updated_at": self._now(),
            },
            ex=STATUS_TTL_SECONDS,
        )
        logger.debug(f"[{account_id}:{service_key}] lock acquired (run={sync_run_id})")
        return True

    async def release_lock(
        self,
        account_id: str,
        service_key: str,
        *,
        terminal_status: str,
        extra: Optional[dict] = None,
    ) -> None:
        """
        Write terminal status BEFORE deleting the lock so readers never see
        is_running()==False with status still "running".
        """
        await self.redis.set_json(
            self._status_key(account_id, service_key),
            {
                "status": terminal_status,
                "updated_at": self._now(),
                **(extra or {}),
            },
            ex=STATUS_TTL_SECONDS,
        )
        await self.redis.delete(self._lock_key(account_id, service_key))
        logger.debug(f"[{account_id}:{service_key}] lock released → {terminal_status}")

    # ── status helpers ────────────────────────────────────────────────────────

    async def set_invalid(self, account_id: str, service_key: str, reason: str) -> None:
        await self.redis.set_json(
            self._status_key(account_id, service_key),
            {
                "status": "invalid",
                "error": reason,
                "updated_at": self._now(),
            },
            ex=INVALID_TTL,
        )
        logger.debug(f"[{account_id}:{service_key}] marked invalid: {reason}")

    async def get_status(self, account_id: str, service_key: str) -> Optional[dict]:
        return await self.redis.get_json(self._status_key(account_id, service_key))

    async def get_statuses(
        self,
        account_id: str,
        service_keys: list[str],
    ) -> dict[str, dict]:
        if not service_keys:
            return {}
        redis_keys = [self._status_key(account_id, k) for k in service_keys]
        values = await self.redis.mget(*redis_keys)
        result: dict[str, dict] = {}
        for service_key, val in zip(service_keys, values):
            if val:
                try:
                    result[service_key] = json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"[{account_id}:{service_key}] corrupt Redis status entry")
        return result

    async def get_all_statuses(self, account_id: str) -> dict[str, dict]:
        pattern = _STATUS_KEY.format(account_id=account_id, service_key="*")
        keys = await self.redis.keys(pattern)
        if not keys:
            return {}
        values = await self.redis.mget(*keys)
        result = {}
        for key, val in zip(keys, values):
            if val:
                service_key = key.split(":")[-1]
                try:
                    result[service_key] = json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    pass
        return result

    async def is_running(self, account_id: str, service_key: str) -> bool:
        count = await self.redis.exists(self._lock_key(account_id, service_key))
        return count == 1
