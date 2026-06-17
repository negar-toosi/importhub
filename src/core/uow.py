from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import Depends

from src.core.database import get_session, SessionDep
from src.app.repositories.import_repository import ImportRepository
from src.app.repositories.shipment_repository import ShipmentRepository
from src.app.repositories.import_error_repository import ImportErrorRepository
from abc import ABC, abstractmethod
class IUnitOfWork(ABC):
    import_repo = ImportRepository

class UnitOfWork:
    def __init__(self, db: SessionDep):
        self.db = db
        self.import_repo = ImportRepository(db)
        self.shipment_repo = ShipmentRepository(db)
        self.import_error_repo = ImportErrorRepository(db)

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def flush(self) -> None:
        await self.db.flush()


async def get_uow(db: SessionDep):
    uow = UnitOfWork(db)
    try:
        yield uow
    except Exception:
        await uow.rollback()
        raise


@asynccontextmanager
async def create_uow():
    """For use outside FastAPI (e.g. Celery tasks)."""
    gen = get_session()
    db = next(gen)
    uow = UnitOfWork(db)
    try:
        yield uow
    except Exception:
        await uow.rollback()
        raise
    finally:
        await gen.close()
