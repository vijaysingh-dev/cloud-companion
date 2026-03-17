import logging

from app.core.constants import AppMode

from app.services.redis import RedisService
from app.services.weaviate import WeaviateService

from app.services.neo4j import Neo4jService
from app.services.repositories.organization import OrganizationRepository


logger = logging.getLogger("cloud-companion")


class Repositories:
    def __init__(self, neo4j):
        self.organization = OrganizationRepository(neo4j)


class Application:
    def __init__(self, mode: AppMode):
        self.mode = mode

        self.neo4j = None
        self.weaviate = None
        self.redis = None

        self.started = False

    async def start(self):
        if self.started:
            return

        logger.info(f"Starting application (mode={self.mode})")

        self.neo4j = Neo4jService()
        await self.neo4j.connect()

        if self.mode in (AppMode.API, AppMode.CELERY):
            self.weaviate = WeaviateService()
            self.redis = RedisService()

            await self.weaviate.connect()
            await self.redis.connect()

        self.repo = Repositories(self.neo4j)

        self.started = True
        logger.info("Application started")

    async def stop(self):
        if not self.started:
            return

        logger.info("Stopping application")

        if self.neo4j:
            await self.neo4j.close()

        if self.weaviate:
            await self.weaviate.close()

        if self.redis:
            await self.redis.close()

        self.started = False
        logger.info("Application stopped")


# =========================
# Providers
# =========================

_api_app = Application(AppMode.API)
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
