from pydantic import BaseModel


class ImportErrorItem(BaseModel):
    row_number: int
    error: str


class GetImportErrorsResponse(BaseModel):
    items: list[ImportErrorItem]
    page: int
    page_size: int
    total: int
