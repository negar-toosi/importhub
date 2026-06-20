import datetime
from sqlalchemy import (
    String,
    Integer,
    Date,
    Numeric,
    Enum,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database import Base
from src.utils.enums import ShipmentStatus


class ShipmentRecord(Base):
    __tablename__ = "shipment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    shipment_code: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    customer_name: Mapped[str] = mapped_column(String(50), nullable=False)

    origin_city: Mapped[str] = mapped_column(String, nullable=False)

    destination_city: Mapped[str] = mapped_column(String, nullable=False)

    weight_kg: Mapped[float] = mapped_column(
        Numeric(13, 3),
        CheckConstraint("weight_kg > 0"),
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Numeric(13, 3),
        CheckConstraint("price >= 0"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(Enum(ShipmentStatus), nullable=False)

    delivery_date: Mapped[datetime.date] = mapped_column(
        Date,
        default=datetime.date.today,
        nullable=False
    )