from src.domain.interfaces import IImportDispatcher
from src.infrastructure.celery.task import process_import_task


class CeleryImportDispatcher(IImportDispatcher):


    async def dispatch(
            self,
            import_id,
            file_path

    ):

        process_import_task.delay(
            str(import_id),
            file_path
        )