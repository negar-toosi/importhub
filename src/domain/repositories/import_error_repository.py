from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import CreateImportError, ImportError


class IImportErrorRepository(ABC):
    @abstractmethod
    async def add(self, entity: CreateImportError) -> None:
        pass

    @abstractmethod
    async def get_by_import_id(self, import_id: UUID, limit: int, offset: int) -> list[ImportError]:
        pass

    @abstractmethod
    async def count_by_import_id(self, import_id: UUID) -> int:
        pass
