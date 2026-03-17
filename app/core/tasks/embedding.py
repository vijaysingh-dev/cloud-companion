from app.core.application import create_celery_app

from app.core.celery import celery
from app.core.tasks.base import BaseTask


@celery.task(bind=True, base=BaseTask)
def generate_embedding(self, resource_id: str):
    import asyncio

    async def run():
        app = await create_celery_app()

        try:
            data = await app.repo.organization.list_accounts(resource_id)

            # TODO:
            # humanize → embed → store

            return {"status": "done", "resource_id": resource_id}

        finally:
            await app.stop()

    return asyncio.run(run())
