from src.utils.enums import ImportStatus


def map_celery_state(result) -> str:
    celery_to_import_status = {
        "PENDING": ImportStatus.PENDING,
        "STARTED": ImportStatus.PROCESSING,
        "SUCCESS": ImportStatus.COMPLETED,
        "FAILURE": ImportStatus.FAILED,
    }
    status = celery_to_import_status.get(result.state)
    return status
