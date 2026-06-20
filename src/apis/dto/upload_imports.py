
import datetime
import uuid

from fastapi import File, HTTPException, UploadFile
from pydantic import BaseModel
from src.utils.enums import ImportStatus

ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # .xls
}


class UploadImportRequest:
    def __init__(self, file: UploadFile = File(...)):
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=422,
                detail="Only Excel files (.xlsx, .xls) are accepted.",
            )
        self.file = file


class UploadImportResponse(BaseModel):
    import_id: uuid.UUID
    status: ImportStatus
    created_at: datetime.datetime