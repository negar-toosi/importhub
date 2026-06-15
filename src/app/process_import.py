import uuid
import pandas as pd
from sqlalchemy.exc import IntegrityError
from src.core.celery import celery
from src.core.uow import create_uow
from src.app.validator import ShipmentRecordValidator


@celery.task
def process_file(import_file: str, import_id_str: str):
    import_id = uuid.UUID(import_id_str)

    with create_uow() as uow:
        try:
            uow.import_repo.set_processing(import_id)
            uow.commit()

            df = pd.read_excel(import_file)
            success_count = 0
            failed_rows = set()

            for index, row in df.iterrows():
                row_number = index + 2  # +2: 1-based + header row

                errors = [
                    ShipmentRecordValidator.shipment_code(row.get("shipment_code")),
                    ShipmentRecordValidator.customer_name(row.get("customer_name")),
                    ShipmentRecordValidator.origin_city(row.get("origin_city")),
                    ShipmentRecordValidator.destination_city(row.get("destination_city")),
                    ShipmentRecordValidator.weight_kg(row.get("weight_kg")),
                    ShipmentRecordValidator.price(row.get("price")),
                    ShipmentRecordValidator.status(row.get("status")),
                ]
                row_errors = [e for e in errors if e is not None]

                if row_errors:
                    failed_rows.add(row_number)
                    for error_message in row_errors:
                        uow.import_error_repo.create(
                            import_id=import_id,
                            row_number=row_number,
                            error_message=error_message,
                        )
                    continue

                try:
                    uow.shipment_repo.create(
                        shipment_code=row["shipment_code"],
                        customer_name=row["customer_name"],
                        origin_city=row["origin_city"],
                        destination_city=row["destination_city"],
                        weight_kg=row["weight_kg"],
                        price=row["price"],
                        status=row["status"],
                        delivery_date=row["delivery_date"],
                    )
                    uow.flush()
                    success_count += 1
                except IntegrityError:
                    uow.rollback()
                    failed_rows.add(row_number)
                    uow.import_error_repo.create(
                        import_id=import_id,
                        row_number=row_number,
                        error_message=f"duplicate shipment_code: {row['shipment_code']}",
                    )

            uow.import_repo.set_completed(
                import_id=import_id,
                total_rows=len(df),
                success_count=success_count,
                failed_count=len(failed_rows),
            )
            uow.commit()

        except Exception:
            uow.rollback()
            with create_uow() as error_uow:
                error_uow.import_repo.set_failed(import_id)
                error_uow.commit()
            raise
