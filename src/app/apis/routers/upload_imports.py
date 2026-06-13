from fastapi import APIRouter, Depends

from src.app.apis.dto.upload_imports import UploadImportRequest, UploadImportResponse
from src.app.models import Import
from src.app.utils.enums import ImportStatus
from src.core.database import SessionDep
from src.app.services import ImportServices
router = APIRouter(prefix="/api/v1", tags=["imports"])


@router.post("/imports", response_model=UploadImportResponse, status_code=201)
async def upload_import(session: SessionDep, request: UploadImportRequest = Depends()):
    
    record = ImportServices.create_import(session=session)
    print("RECORD TYPE:", type(record))
    return UploadImportResponse(
        import_id=record.id,
        status=record.status,
        created_at=record.created_at,
    )
