import os
import tempfile

from fastapi import APIRouter, Depends

from src.app.apis.dto.upload_imports import UploadImportRequest, UploadImportResponse
from src.app.process_import import process_file
from src.app.services import ImportServices
from src.core.database import SessionDep

router = APIRouter(prefix="/api/v1", tags=["imports"])

UPLOAD_DIR = "/tmp/importhub_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/imports", response_model=UploadImportResponse, status_code=201)
async def upload_import(session: SessionDep, request: UploadImportRequest = Depends()):
    file_suffix = os.path.splitext(request.file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix, dir=UPLOAD_DIR) as tmp:
        tmp.write(await request.file.read())
        file_path = tmp.name

    record = ImportServices.create_import(session=session)

    process_file.delay(file_path, str(record.id))

    return UploadImportResponse(
        import_id=record.id,
        status=record.status,
        created_at=record.created_at,
    )
