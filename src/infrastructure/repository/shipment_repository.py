from sqlalchemy import select, func

from src.domain.entities import CreateShipmentRecord, ShipmentFilter
from src.domain.entities.shipment_record import ShipmentRecord as ShipmentRecordEntity
from src.domain.repositories import IShipmentRepository
from src.infrastructure.tables import ShipmentRecord
from src.infrastructure.database import async_session


class ShipmentRepository(IShipmentRepository):

    async def add(self, entity: CreateShipmentRecord) -> None:
        async with async_session() as session:
            async with session.begin():
                shipment = ShipmentRecord(**entity.model_dump())
                session.add(shipment)
                await session.flush()
                await session.refresh(shipment)

    async def get_shipment_records(
        self, filters: ShipmentFilter, limit: int, offset: int
    ) -> tuple[list[ShipmentRecordEntity], int]:
        conditions = self._build_conditions(filters)

        total_subq = select(func.count()).select_from(ShipmentRecord).where(*conditions).scalar_subquery()

        stmt = (
            select(ShipmentRecord, total_subq.label("total"))
            .where(*conditions)
            .order_by(ShipmentRecord.id)
            .offset(offset)
            .limit(limit)
        )

        async with async_session() as session:
            result = await session.execute(stmt)
            rows = result.all()

        if not rows:
            return [], 0

        total = rows[0].total
        items = [
            ShipmentRecordEntity(
                id=row.ShipmentRecord.id,
                shipment_code=row.ShipmentRecord.shipment_code,
                customer_name=row.ShipmentRecord.customer_name,
                origin_city=row.ShipmentRecord.origin_city,
                destination_city=row.ShipmentRecord.destination_city,
                weight_kg=row.ShipmentRecord.weight_kg,
                price=row.ShipmentRecord.price,
                status=row.ShipmentRecord.status,
                delivery_date=row.ShipmentRecord.delivery_date,
            )
            for row in rows
        ]
        return items, total

    def _build_conditions(self, filters: ShipmentFilter) -> list:
        conditions = []
        if filters.status is not None:
            conditions.append(ShipmentRecord.status == filters.status)
        if filters.origin_city is not None:
            conditions.append(ShipmentRecord.origin_city == filters.origin_city)
        if filters.destination_city is not None:
            conditions.append(ShipmentRecord.destination_city == filters.destination_city)
        if filters.customer_name is not None:
            conditions.append(ShipmentRecord.customer_name == filters.customer_name)
        if filters.created_from is not None:
            conditions.append(ShipmentRecord.delivery_date >= filters.created_from)
        if filters.created_to is not None:
            conditions.append(ShipmentRecord.delivery_date <= filters.created_to)
        return conditions
