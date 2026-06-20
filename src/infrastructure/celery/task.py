# infrastructure/celery/tasks.py

import asyncio
from uuid import UUID

from src.infrastructure.celery.setup import celery
from src.infrastructure.container import build_process_import_service

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)


@celery.task
def process_import_task(import_id: str, file_path: str):
    service = build_process_import_service(
        import_id=UUID(import_id),
        file_path=file_path,
    )
    _loop.run_until_complete(service.execute())