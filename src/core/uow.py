from collections.abc import Generator
from contextlib import contextmanager

from fastapi import Depends
from sqlmodel import Session

from src.core.database import engine, get_session
from src.app.repositories.import_repository import ImportRepository
from src.app.repositories.shipment_repository import ShipmentRepository
from src.app.repositories.import_error_repository import ImportErrorRepository


class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db
        self.import_repo = ImportRepository(db)
        self.shipment_repo = ShipmentRepository(db)
        self.import_error_repo = ImportErrorRepository(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def flush(self) -> None:
        self.db.flush()


def get_uow(db: Session = Depends(get_session)) -> Generator[UnitOfWork, None, None]:
    uow = UnitOfWork(db)
    try:
        yield uow
    except Exception:
        uow.rollback()
        raise


@contextmanager
def create_uow():
    """For use outside FastAPI (e.g. Celery tasks)."""
    with Session(engine) as db:
        uow = UnitOfWork(db)
        try:
            yield uow
        except Exception:
            uow.rollback()
            raise
