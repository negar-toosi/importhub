from uuid import UUID

from src.domain.entities.imports import Import
from src.domain.repositories import IImportRepository

class GetImportService:
    def __init__(self, import_repo: IImportRepository):
        self.import_repo = import_repo

    async def execute(self, import_id: UUID) -> Import:
        return await self.import_repo.get_by_id(import_id)
