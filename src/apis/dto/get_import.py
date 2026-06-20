import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from src.utils.enums import ImportStatus


class GetImportResponse(BaseModel):
    import_id: UUID = Field(...)
    status: ImportStatus = Field(...)
    total_row: Optional[int] 
    success_count: Optional[int] 
    failed_count: Optional[int] 
    created_at: datetime.datetime = Field(...)
    finished_at: Optional[datetime.datetime]
