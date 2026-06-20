import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Uuid

from src.infrastructure.tables.imports import Import

class ImportError(Base):
    __tablename__ = "import_errors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    import_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("imports.id"),
        nullable=False
    )

    row_number: Mapped[int] = mapped_column(Integer, nullable=False)

    error_message: Mapped[str] = mapped_column(String, nullable=False)

    import_: Mapped["Import"] = relationship(
        back_populates="import_errors"
    )