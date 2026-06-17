import datetime
import uuid
from sqlmodel import UUID, select
from src.core.database import SessionDep
from src.app.models import Import
from src.app.utils.enums import ImportStatus


class ImportRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    def create(self,status: ImportStatus, file_path:str) -> Import:
        record = Import(
            status=status,
            file_path=file_path
        )
        self.db.add(record)
        self.db.flush()
        self.db.refresh(record)
        return record

    def get(self, import_id: uuid.UUID) -> Import:
        return self.db.exec(select(Import).where(Import.id == import_id)).one()

    def set_processing(self, import_id: uuid.UUID) -> None:
        record = self.get(import_id)
        record.status = ImportStatus.PROCESSING
        self.db.add(record)
        self.db.commit()

    def set_completed(self, import_id: uuid.UUID, total_rows: int, success_count: int, failed_count: int) -> None:
        record = self.get(import_id)
        record.status = ImportStatus.COMPLETED
        record.total_rows = total_rows
        record.success_count = success_count
        record.failed_count = failed_count
        record.finished_at = datetime.datetime.now()
        self.db.add(record)
        self.db.commit()

    def set_failed(self, import_id: uuid.UUID) -> None:
        record = self.get(import_id)
        record.status = ImportStatus.FAILED
        record.finished_at = datetime.datetime.now()
        self.db.add(record)
        self.db.commit()
