from src.domain.interfaces.file_storage import IFileStorage
from src.domain.interfaces.job_dispatcher import IImportDispatcher
from src.domain.repositories import IImportRepository, IImportErrorRepository, IShipmentRepository
from src.presentation.container import Container


def get_dispatcher() -> IImportDispatcher:
    return Container.dispatcher()


def get_file_storage() -> IFileStorage:
    return Container.file_storage()


def get_import_repository() -> IImportRepository:
    return Container.import_repository()


def get_import_error_repository() -> IImportErrorRepository:
    return Container.import_error_repository()


def get_shipment_repository() -> IShipmentRepository:
    return Container.shipment_repository()
