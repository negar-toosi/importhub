from src.domain.repositories import IImportRepository, IImportErrorRepository, IShipmentRepository
from src.infrastructure.config import settings
from src.infrastructure.file_storage import LocalFileStorage
from src.infrastructure.celery.import_dispatcher import CeleryImportDispatcher
from src.infrastructure.repository.import_repository import ImportRepository
from src.infrastructure.repository.import_error_repository import ImportErrorRepository
from src.infrastructure.repository.shipment_repository import ShipmentRepository


class Container:

    @staticmethod
    def dispatcher():
        return CeleryImportDispatcher()

    @staticmethod
    def file_storage():
        return LocalFileStorage(upload_dir=settings.UPLOAD_DIR)

    @staticmethod
    def import_repository() -> IImportRepository:
        return ImportRepository()

    @staticmethod
    def import_error_repository() -> IImportErrorRepository:
        return ImportErrorRepository()

    @staticmethod
    def shipment_repository() -> IShipmentRepository:
        return ShipmentRepository()
