from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from src.utils.enums import ShipmentStatus


class CreateShipmentRecord(BaseModel):
    shipment_code: str
    customer_name: str = Field(max_length=50)
    origin_city: str
    destination_city: str
    weight_kg: Decimal = Field(gt=0)
    price: Decimal = Field(ge=0)
    status: ShipmentStatus
    delivery_date: date


class ShipmentRecord(BaseModel):
    id: int
    shipment_code: str
    customer_name: str
    origin_city: str
    destination_city: str
    weight_kg: Decimal
    price: Decimal
    status: ShipmentStatus
    delivery_date: date


class ShipmentFilter(BaseModel):
    status: Optional[ShipmentStatus] = None
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None
    customer_name: Optional[str] = None
    created_from: Optional[date] = None
    created_to: Optional[date] = None