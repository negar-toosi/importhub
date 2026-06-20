import datetime
import uuid
from sqlmodel import UUID, select
from abc import ABC, abstractmethod

from src.domain.entities import CreateImport, Import
from src.utils.enums import ImportStatus

class IImportRepository(ABC):
    @abstractmethod
    async def add(self, entity: CreateImport) -> Import:
        pass

    @abstractmethod
    async def get_by_id(self, import_id: UUID) -> Import:
        pass

    @abstractmethod
    async def set_processing(self, import_id: UUID) -> None:
        pass

    @abstractmethod
    async def set_completed(self, entity: Import) -> None:
        pass

    @abstractmethod
    async def set_failed(self, import_id: UUID) -> None:
        pass

