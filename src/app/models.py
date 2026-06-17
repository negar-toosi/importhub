import datetime
from decimal import Decimal
from typing import Optional
import uuid
from sqlmodel import Column, DateTime, Field, SQLModel, func, CheckConstraint
from src.app.utils.enums import ShipmentStatus, ImportStatus


class ShipmentRecord(SQLModel, table=True):
    __tablename__ = "shipment_records"
    id: int | None = Field(default=None, primary_key=True)
    shipment_code: str = Field(unique=True, index=True)
    customer_name: str = Field(max_length=50)
    origin_city: str = Field()
    destination_city: str = Field()
    weight_kg: Decimal = Field(max_digits=10, decimal_places=3, gt=0, sa_column_args=(CheckConstraint("weight_kg > 0"),))
    price: Decimal = Field(max_digits=10, decimal_places=3, ge=0, sa_column_args=(CheckConstraint("price >= 0"),))
    status: ShipmentStatus
    delivery_date: datetime.date = Field(default_factory=datetime.date.today)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
    )
    updated_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(), onupdate=func.now())
    )

class Import(SQLModel,table=True):
    __tablename__ = "imports"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    status: ImportStatus
    total_rows: int = Field(default=0, ge=0, sa_column_args=(CheckConstraint("total_rows >= 0"),))
    success_count: int = Field(default=0, ge=0, sa_column_args=(CheckConstraint("success_count >= 0"),))
    failed_count: int = Field(default=0, ge=0, sa_column_args=(CheckConstraint("failed_count >= 0"),))
    file_path: str
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
    )
    finished_at: Optional[datetime.datetime] = Field(default=None)

class ImportError(SQLModel, table=True):
    __tablename__ = "import_errors"
    id: int | None = Field(default=None, primary_key=True)
    import_id: uuid.UUID = Field(foreign_key="imports.id")
    row_number: int
    error_message: str

