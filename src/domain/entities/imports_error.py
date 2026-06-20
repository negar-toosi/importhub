from uuid import UUID

from pydantic import BaseModel

class CreateImportError(BaseModel):
    import_id: UUID
    row_number: int
    error_message: str

class ImportError(BaseModel):
    id: int
    import_id: UUID
    row_number: int
    error_message: str