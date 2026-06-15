import datetime
from decimal import Decimal
from sqlmodel import Session
from src.app.models import ShipmentRecord
from src.app.utils.enums import ShipmentStatus


class ShipmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        shipment_code: str,
        customer_name: str,
        origin_city: str,
        destination_city: str,
        weight_kg: Decimal,
        price: Decimal,
        status: ShipmentStatus,
        delivery_date: datetime.date,
    ) -> None:
        record = ShipmentRecord(
            shipment_code=shipment_code,
            customer_name=customer_name,
            origin_city=origin_city,
            destination_city=destination_city,
            weight_kg=weight_kg,
            price=price,
            status=status,
            delivery_date=delivery_date,
        )
        self.db.add(record)
