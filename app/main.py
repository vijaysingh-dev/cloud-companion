import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.api.v1.router import router as v1_router
from app.api.health import router as health_router
from app.core.application import init_api_app
from app.core.migrate import get_latest_migration_version
from app.core.config import settings

logger = logging.getLogger("cloud-companion")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_instance = await init_api_app()
    version = await get_latest_migration_version(app_instance.neo4j)
    if not version:
        raise RuntimeError("Database not migrated. Run `cc migrate` before starting APP.")

    app.state.app = app_instance

    try:
        yield
    finally:
        await app_instance.stop()


def create_application() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(LoggingMiddleware)

    setup_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
