from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from src.utils.enums import ShipmentStatus


class ShipmentItem(BaseModel):
    id: int
    shipment_code: str
    customer_name: str
    origin_city: str
    destination_city: str
    weight_kg: Decimal
    price: Decimal
    status: ShipmentStatus
    delivery_date: date


class ShipmentRecordsResponse(BaseModel):
    items: list[ShipmentItem]
    page: int
    page_size: int
    total: int
