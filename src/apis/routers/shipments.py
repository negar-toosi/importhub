from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.apis.dto import ShipmentRecordsResponse, ShipmentItem
from src.domain.entities import ShipmentFilter
from src.domain.repositories import IShipmentRepository
from src.presentation.dependencies import get_shipment_repository
from src.utils.enums import ShipmentStatus

router = APIRouter(prefix="/api/v1/shipments", tags=["shipments"])


@router.get("/", response_model=ShipmentRecordsResponse, status_code=200)
async def list_shipments(
    status: Optional[ShipmentStatus] = Query(default=None),
    origin_city: Optional[str] = Query(default=None),
    destination_city: Optional[str] = Query(default=None),
    customer_name: Optional[str] = Query(default=None),
    created_from: Optional[date] = Query(default=None),
    created_to: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    shipment_repo: IShipmentRepository = Depends(get_shipment_repository),
):
    filters = ShipmentFilter(
        status=status,
        origin_city=origin_city,
        destination_city=destination_city,
        customer_name=customer_name,
        created_from=created_from,
        created_to=created_to,
    )
    offset = (page - 1) * page_size
    items, total = await shipment_repo.get_shipment_records(filters, limit=page_size, offset=offset)

    return ShipmentRecordsResponse(
        items=[
            ShipmentItem(
                id=s.id,
                shipment_code=s.shipment_code,
                customer_name=s.customer_name,
                origin_city=s.origin_city,
                destination_city=s.destination_city,
                weight_kg=s.weight_kg,
                price=s.price,
                status=s.status,
                delivery_date=s.delivery_date,
            )
            for s in items
        ],
        page=page,
        page_size=page_size,
        total=total,
    )
