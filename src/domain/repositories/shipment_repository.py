from abc import ABC, abstractmethod

from src.domain.entities import CreateShipmentRecord, ShipmentRecord, ShipmentFilter


class IShipmentRepository(ABC):

    @abstractmethod
    async def add(self, entity: CreateShipmentRecord) -> None:
        pass

    @abstractmethod
    async def get_shipment_records(self, filters: ShipmentFilter, limit: int, offset: int) -> tuple[list[ShipmentRecord], int]:
        pass
