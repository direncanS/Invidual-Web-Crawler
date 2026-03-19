import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PdfResponse(BaseModel):
    id: uuid.UUID
    source_url: str
    file_path: str
    sha256: Optional[str] = None
    downloaded_at: datetime
    crawl_job_id: uuid.UUID

    model_config = {"from_attributes": True}


class PdfListResponse(BaseModel):
    pdfs: list[PdfResponse]


class TopWordEntry(BaseModel):
    word: str
    count: int


class TopWordsResponse(BaseModel):
    pdf_id: uuid.UUID
    words: list[TopWordEntry]
