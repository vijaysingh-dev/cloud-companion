# app/core/applicaiton.py

import logging
from typing import Optional

from app.core.constants import AppMode
from app.services.neo4j import Neo4jService
from app.services.weaviate import WeaviateService
from app.services.redis import RedisService
from app.services.repositories import (
    OrganizationRepository,
    AccountRepository,
    APIKeyRepository,
    SyncRepository,
)

logger = logging.getLogger(__name__)


class Repositories:
    def __init__(self, neo4j: Neo4jService):
        self.organization = OrganizationRepository(neo4j)
        self.account = AccountRepository(neo4j)
        self.api_key = APIKeyRepository(neo4j)
        self.sync = SyncRepository(neo4j)


class Application:
    def __init__(self, mode: AppMode):
        self.mode = mode
        self._neo4j: Optional[Neo4jService] = None
        self._weaviate: Optional[WeaviateService] = None
        self._redis: Optional[RedisService] = None
        self.started = False

    @property
    def neo4j(self) -> Neo4jService:
        if self._neo4j is None:
            raise RuntimeError("Neo4j not initialized. Call start() first.")
        return self._neo4j

    @property
    def weaviate(self) -> WeaviateService:
        if self._weaviate is None:
            raise RuntimeError("Neo4j not initialized. Call start() first.")
        return self._weaviate

    @property
    def redis(self) -> RedisService:
        if self._redis is None:
            raise RuntimeError("Neo4j not initialized. Call start() first.")
        return self._redis

    async def start(self):
        if self.started:
            return
        logger.info(f"Starting application (mode={self.mode})")
        self._neo4j = Neo4jService()
        await self._neo4j.connect()

        self._redis = RedisService()
        await self.redis.connect()

        if self.mode in (AppMode.APP, AppMode.CELERY):
            self._weaviate = WeaviateService()
            await self.weaviate.connect()

        self.repo = Repositories(self.neo4j)
        self.started = True
        logger.info("Application started")

    async def stop(self):
        if not self.started:
            return
        logger.info("Stopping application")
        if self._neo4j:
            await self._neo4j.close()
        if self._weaviate:
            await self._weaviate.close()
        if self._redis:
            await self._redis.close()
        self.started = False
        logger.info("Application stopped")


# =========================
# Providers
# =========================
_api_app = Application(AppMode.APP)
_cli_app = Application(AppMode.CLI)


async def init_api_app():
    if not _api_app.started:
        await _api_app.start()
    return _api_app


def get_cli_app():
    return _cli_app


async def create_celery_app():
    app = Application(AppMode.CELERY)
    await app.start()
    return app
