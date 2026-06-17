import os
import tempfile
from uuid import UUID
from fastapi import APIRouter, Depends

from src.app.apis.dto.upload_imports import UploadImportRequest, UploadImportResponse
from src.app.process_import import process_file
from src.core.database import SessionDep
from src.app.utils.enums import ImportStatus
from src.app.repositories.import_repository import ImportRepository
from src.core.config import ROOT_DIR

router = APIRouter(prefix="/api/v1", tags=["imports"])

UPLOAD_DIR = os.path.join(ROOT_DIR, "importhub_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/imports", response_model=UploadImportResponse, status_code=201)
async def upload_import(session: SessionDep, request: UploadImportRequest = Depends()):
    file_suffix = os.path.splitext(request.file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix, dir=UPLOAD_DIR) as tmp:
        tmp.write(await request.file.read())
        file_path = tmp.name
    repository = ImportRepository(session)
    record = repository.create(status=ImportStatus.PENDING, file_path=file_path)
    session.commit()

    result = process_file.delay(file_path, str(record.id))

    celery_to_import_status = {
        "PENDING": ImportStatus.PENDING,
        "STARTED": ImportStatus.PROCESSING,
        "SUCCESS": ImportStatus.COMPLETED,
        "FAILURE": ImportStatus.FAILED,
    }
    status = celery_to_import_status.get(result.state)

    return UploadImportResponse(
        import_id=record.id,
        status=status,
        created_at=record.created_at,
    )