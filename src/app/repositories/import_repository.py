import datetime
import uuid
from sqlmodel import Session, select
from src.app.models import Import
from src.app.utils.enums import ImportStatus


class ImportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self) -> Import:
        record = Import(status=ImportStatus.PENDING)
        self.db.add(record)
        self.db.flush()
        self.db.refresh(record)
        return record

    def _get(self, import_id: uuid.UUID) -> Import:
        return self.db.exec(select(Import).where(Import.id == import_id)).one()

    def set_processing(self, import_id: uuid.UUID) -> None:
        record = self._get(import_id)
        record.status = ImportStatus.PROCESSING
        self.db.add(record)

    def set_completed(self, import_id: uuid.UUID, total_rows: int, success_count: int, failed_count: int) -> None:
        record = self._get(import_id)
        record.status = ImportStatus.COMPLETED
        record.total_rows = total_rows
        record.success_count = success_count
        record.failed_count = failed_count
        record.finished_at = datetime.datetime.now()
        self.db.add(record)

    def set_failed(self, import_id: uuid.UUID) -> None:
        record = self._get(import_id)
        record.status = ImportStatus.FAILED
        record.finished_at = datetime.datetime.now()
        self.db.add(record)
