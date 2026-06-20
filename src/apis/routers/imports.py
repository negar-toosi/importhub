from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from src.apis.dto import GetImportResponse, GetImportErrorsResponse, ImportErrorItem
from src.apis.dto.upload_imports import UploadImportRequest, UploadImportResponse
from src.aplication.get_import_service import GetImportService
from src.aplication.upload_import_service import UploadImportService
from src.domain.interfaces.file_storage import IFileStorage
from src.domain.interfaces.job_dispatcher import IImportDispatcher
from src.domain.repositories import IImportRepository, IImportErrorRepository
from src.presentation.dependencies import (
    get_dispatcher,
    get_file_storage,
    get_import_repository,
    get_import_error_repository,
)

router = APIRouter(prefix="/api/v1/imports", tags=["imports"])


@router.post("/", response_model=UploadImportResponse, status_code=201)
async def upload_import(
    import_repo: IImportRepository = Depends(get_import_repository),
    dispatcher: IImportDispatcher = Depends(get_dispatcher),
    file_storage: IFileStorage = Depends(get_file_storage),
    request: UploadImportRequest = Depends(),
):
    content = await request.file.read()
    service = UploadImportService(
        import_repo=import_repo,
        file_storage=file_storage,
    )
    record = await service.execute(request.file.filename, content)
    await dispatcher.dispatch(record.id, record.file_path)

    return UploadImportResponse(
        import_id=record.id,
        status=record.status, #TODO: the status must give from celery
        created_at=record.created_at,
    )


@router.get("/{import_id}", response_model=GetImportResponse, status_code=200)
async def get_import(
    import_id: UUID,
    import_repo: IImportRepository = Depends(get_import_repository),
):
    service = GetImportService(import_repo=import_repo)
    record = await service.execute(import_id)

    return GetImportResponse(
        import_id=record.id,
        status=record.status,
        total_row=record.total_rows,
        success_count=record.success_count,
        failed_count=record.failed_count,
        created_at=record.created_at,
        finished_at=record.finished_at,
    )


@router.get("/{import_id}/errors", response_model=GetImportErrorsResponse, status_code=200)
async def get_import_errors(
    import_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    error_repo: IImportErrorRepository = Depends(get_import_error_repository),
):
    offset = (page - 1) * page_size
    items = await error_repo.get_by_import_id(import_id, limit=page_size, offset=offset)
    total = await error_repo.count_by_import_id(import_id)

    return GetImportErrorsResponse(
        items=[ImportErrorItem(row_number=e.row_number, error=e.error_message) for e in items],
        page=page,
        page_size=page_size,
        total=total,
    )

