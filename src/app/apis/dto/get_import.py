import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from src.app.utils.enums import ImportStatus


class GetImportResponse(BaseModel):
    import_id: UUID = Field(...)
    status: ImportStatus = Field(...)
    total_row: int = Field(...)
    success_count: int = Field(...)
    failed_count: int = Field(...)
    created_at: datetime.datetime = Field(...)
    finished_at: Optional[datetime.datetime]
