from uuid import UUID

from sqlalchemy import select, func

from src.domain.entities import CreateImportError
from src.domain.entities.imports_error import ImportError as ImportErrorEntity
from src.domain.repositories import IImportErrorRepository
from src.infrastructure.tables import ImportError
from src.infrastructure.database import async_session


class ImportErrorRepository(IImportErrorRepository):
    async def add(self, entity: CreateImportError) -> None:
        async with async_session() as session:
            async with session.begin():
                import_error = ImportError(**entity.model_dump())
                session.add(import_error)
                await session.flush()
                await session.refresh(import_error)

    async def get_by_import_id(
        self, import_id: UUID, limit: int, offset: int
    ) -> list[ImportErrorEntity]:
        async with async_session() as session:
            result = await session.execute(
                select(ImportError)
                .where(ImportError.import_id == import_id)
                .order_by(ImportError.row_number)
                .offset(offset)
                .limit(limit)
            )
            rows = result.scalars().all()

        return [
            ImportErrorEntity(
                id=row.id,
                import_id=row.import_id,
                row_number=row.row_number,
                error_message=row.error_message,
            )
            for row in rows
        ]

    async def count_by_import_id(self, import_id: UUID) -> int:
        async with async_session() as session:
            result = await session.execute(
                select(func.count()).select_from(ImportError).where(ImportError.import_id == import_id)
            )
            return result.scalar_one()