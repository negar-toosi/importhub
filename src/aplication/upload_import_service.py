from src.domain.entities import CreateImport
from src.domain.interfaces.file_storage import IFileStorage
from src.domain.repositories import IImportRepository
from src.utils.enums import ImportStatus


class UploadImportService:
    def __init__(self, import_repo: IImportRepository, file_storage: IFileStorage):
        self.import_repo = import_repo
        self.file_storage = file_storage

    async def execute(self, filename: str, content: bytes):
        file_path = await self.file_storage.save(filename, content)
        entity = CreateImport(
            status=ImportStatus.PENDING,
            file_path=file_path,
        )
        return await self.import_repo.add(entity=entity)
