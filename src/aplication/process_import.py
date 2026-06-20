
import datetime
from typing import Optional
from uuid import UUID

from src.domain.entities.imports import Import
from src.domain.entities.imports_error import CreateImportError
from src.domain.entities.shipment_record import CreateShipmentRecord
from src.domain.repositories import IImportRepository, IImportErrorRepository, IShipmentRepository

from sqlalchemy.exc import IntegrityError
from src.aplication.validator import ShipmentRecordValidator
from src.utils.enums import ImportStatus

class ProcessImportService:
    def __init__(
        self,
        import_id: UUID,
        file_path: str,
        import_repo: IImportRepository,
        import_error_repo: IImportErrorRepository,
        shipment_record_repo: IShipmentRepository,
    ) -> None:
        self._import_repo = import_repo
        self._import_error_repo = import_error_repo
        self._shipment_record_repo = shipment_record_repo
        self.file_path = file_path
        self.import_id = import_id
        self.success_count = 0
        self.failed_rows = set()
    
    async def execute(self):
        try:
            await self._import_repo.set_processing(self.import_id)
            df = self._read_excel(self.file_path)

            for index, row in df.iterrows():
                row_number = index + 2  # +2: 1-based + header row
                row_errors = self._failed_row(row)
                if row_errors:
                    for error_message in row_errors:
                        await self._add_error(row_number, error_message)
                    continue

                await self._add_shipment_record(row, row_number)

            await self._import_repo.set_completed(
                Import(
                    id=self.import_id,
                    status=ImportStatus.COMPLETED,
                    total_rows=len(df),
                    success_count=self.success_count,
                    failed_count=len(self.failed_rows),
                    finished_at=datetime.datetime.now()
                )
            )
        except Exception as ex:
            await self._import_repo.set_failed(self.import_id)
            raise ex

    def _read_excel(self, file_path: str) -> Optional[list]:
        import pandas as pd
        return pd.read_excel(file_path)

    def _failed_row(self, row) -> list:
        errors = [
                ShipmentRecordValidator.shipment_code(row.get("shipment_code")),
                ShipmentRecordValidator.customer_name(row.get("customer_name")),
                ShipmentRecordValidator.origin_city(row.get("origin_city")),
                ShipmentRecordValidator.destination_city(row.get("destination_city")),
                ShipmentRecordValidator.weight_kg(row.get("weight_kg")),
                ShipmentRecordValidator.price(row.get("price")),
                ShipmentRecordValidator.status(row.get("status")),
                ShipmentRecordValidator.delivery_date(row.get("delivery_date")),
            ]
        row_errors = [e for e in errors if e is not None]
        return row_errors
    async def _add_error(self, row_number:int, error_message: str) -> None:
        self.failed_rows.add(row_number)
        error = CreateImportError(
                import_id=self.import_id,
                row_number=row_number,
                error_message=error_message,
        )
        await self._import_error_repo.add(error)
    async def _add_shipment_record(self,row, row_number: int) -> None:
        try:
            entity = CreateShipmentRecord(**row.to_dict())
            await self._shipment_record_repo.add(entity)
            self.success_count += 1
        except IntegrityError:
            await self._add_error(
                row_number=row_number,
                error_message=f"duplicate shipment_code: {row['shipment_code']}"
            )  
