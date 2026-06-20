from src.aplication.process_import import ProcessImportService
from src.infrastructure.database import async_session
from src.infrastructure.repository import ImportRepository, ImportErrorRepository, ShipmentRepository


def build_process_import_service(import_id, file_path):
    import_repo = ImportRepository()
    error_repo = ImportErrorRepository()
    shipment_repo = ShipmentRepository()

    return ProcessImportService(
        import_id=import_id,
        file_path=file_path,
        import_repo=import_repo,
        import_error_repo=error_repo,
        shipment_record_repo=shipment_repo
    )