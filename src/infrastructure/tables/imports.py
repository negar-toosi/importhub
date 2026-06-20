import datetime
from typing import List
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database import Base
from sqlalchemy import Column, Integer, String, Enum,DateTime, Uuid, CheckConstraint
from src.utils.enums import ImportStatus

class Import(Base):
    __tablename__ = "imports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  
        nullable=False
    )
    status: Mapped[str] = mapped_column(Enum(ImportStatus))
    total_rows: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint("total_rows >= 0"),
        nullable=True
    )
    success_count: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint("success_count >= 0"),
        nullable=True
    )
    failed_count: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint("failed_count >= 0"),
        nullable=True
    )
    file_path: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow   # better than now()
    )
    finished_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    import_errors: Mapped[list["ImportError"]] = relationship(
        back_populates="import_"
    )