from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from src.utils.enums import ImportStatus

class CreateImport(BaseModel):
    status: ImportStatus
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)

class Import(BaseModel):
    id: UUID
    status: ImportStatus
    total_rows: Optional[int] = None 
    success_count: Optional[int] = None
    failed_count: Optional[int] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None