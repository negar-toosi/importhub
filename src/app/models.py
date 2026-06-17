import datetime
from decimal import Decimal
from typing import Optional
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship, Fore
from src.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Enum, Date,DateTime, Uuid, CheckConstraint
from src.app.utils.enums import ShipmentStatus, ImportStatus


class ShipmentRecord(Base):
    __tablename__ = "shipment_records"
    id = Column(Integer, primary_key=True, index=True)
    shipment_code = Column(String, unique=True, index=True)
    customer_name =  Column(String, max_length=50)
    origin_city = Column(String)
    destination_city = Column(String)
    weight_kg = Column(Numeric(precision=13, decimal_return_scale=3), CheckConstraint("weight_kg > 0"))
    price = Column(Numeric(precision=13, decimal_return_scale=3), CheckConstraint("price >= 0"))
    status = Column(Enum(ShipmentStatus))
    delivery_date = Column(Date,default_factory=datetime.date.today)

class Import(Base):
    __tablename__ = "imports"
    id = Column(Uuid, default_factory=uuid.uuid4,primary_key=True )
    status = Column(Enum(ImportStatus))
    total_rows = Column(Integer, CheckConstraint("total_rows >= 0"), nullable=True)
    success_count = Column(Integer, CheckConstraint("success_count >= 0"), nullable=True)
    failed_count = Column(Integer,CheckConstraint("failed_count >= 0"),nullable=True)
    file_path = Column(String)
    created_at = Column(DateTime,default_factory=datetime.datetime.now)
    finished_at = Column(DateTime, nullable=True)

class ImportError(Base):
    __tablename__ = "import_errors"
    id : Mapped[int]= mapped_Column(primary_key=True, index=True) # type: ignore
    import_id: Mapped[Uuid] = mapped_column(ForeignKey("imports"))
    import: Mapped
    row_number: int
    error_message: str

