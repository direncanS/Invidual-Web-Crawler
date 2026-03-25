import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WordcloudSingleRequest(BaseModel):
    pdf_id: uuid.UUID


class WordcloudMultiRequest(BaseModel):
    pdf_ids: list[uuid.UUID] = Field(min_length=2)


class WordcloudIntervalRequest(BaseModel):
    start_datetime: datetime
    end_datetime: datetime


class WordcloudResponse(BaseModel):
    id: uuid.UUID
    mode: str
    image_path: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
