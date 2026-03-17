import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CrawlJobCreateRequest(BaseModel):
    start_url: str
    depth: int = Field(ge=1, le=3)


class CrawlJobResponse(BaseModel):
    id: uuid.UUID
    start_url: str
    depth: int
    status: str
    error_code: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CrawlJobListResponse(BaseModel):
    jobs: list[CrawlJobResponse]


class CrawledPageResponse(BaseModel):
    id: uuid.UUID
    url: str
    depth_level: int
    status_code: Optional[int] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}
