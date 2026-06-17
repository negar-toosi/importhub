import uuid
from src.app.models import ImportError
from src.core.database import SessionDep

class ImportErrorRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    def create(self, import_id: uuid.UUID, row_number: int, error_message: str) -> None:
        self.db.add(ImportError(
            import_id=import_id,
            row_number=row_number,
            error_message=error_message,
        ))
