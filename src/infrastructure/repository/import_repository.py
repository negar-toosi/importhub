from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.domain.entities import CreateImport, Import
from src.domain.repositories import IImportRepository
from src.infrastructure.tables import Import as import_table
from src.utils.enums import ImportStatus
from src.infrastructure.database import async_session
class ImportRepository(IImportRepository):
    # def __init__(self, async_session: async_sessionmaker[AsyncSession]) -> None:
    #     self._db_context = async_session


    async def add(self, entity: CreateImport) -> Import:
        async with async_session() as session:
            async with session.begin():
                import_obj = import_table(**entity.model_dump())
                session.add(import_obj)
                await session.flush()
                await session.refresh(import_obj)

                return Import(
                    id=import_obj.id,
                    status=import_obj.status,
                    total_row=import_obj.total_rows,
                    success_count=import_obj.success_count,
                    failed_count=import_obj.failed_count,
                    file_path=import_obj.file_path,
                    created_at=import_obj.created_at,
                    finished_at=import_obj.finished_at,
                )

    async def get_by_id(self, import_id: UUID) -> Import:
        async with async_session() as session:
            stmt = select(import_table).where(import_table.id == import_id)
            result = await session.execute(stmt)
            await session.commit()
            row = result.scalar_one_or_none()
            if row is None:
                raise HTTPException(
                    status_code=400,
                    detail="there is no import with this id"
                ) # TODO: error handling
            
            return Import(
                id=row.id,
                status=row.status,
                total_rows=row.total_rows,
                success_count=row.success_count,
                failed_count=row.failed_count,
                file_path=row.file_path,
                created_at=row.created_at,
                finished_at=row.finished_at,
            )

    async def set_processing(self, import_id: UUID) -> None:
        async with async_session() as session:
            async with session.begin():
                stmt = update(import_table).where(import_table.id == import_id).values(status=ImportStatus.PROCESSING)
                await session.execute(stmt)
                await session.commit()

    async def set_completed(self, entity: Import) -> None:
        async with async_session() as session:
            async with session.begin():
                stmt = update(import_table).where(import_table.id == entity.id).values(
                    status=ImportStatus.COMPLETED,
                    total_rows=entity.total_rows,
                    success_count=entity.success_count,
                    failed_count=entity.failed_count,
                    finished_at=datetime.now(),
                )
                await session.execute(stmt)
                await session.commit()

    async def set_failed(self, import_id: UUID) -> None:
        async with async_session() as session:
            async with session.begin():
                stmt = update(import_table).where(import_table.id == import_id).values(
                    status=ImportStatus.FAILED,
                    finished_at=datetime.now(),
                )
                await session.execute(stmt)
                await session.commit()


