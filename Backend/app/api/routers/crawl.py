import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.crawl import (
    CrawlJobCreateRequest,
    CrawlJobListResponse,
    CrawlJobResponse,
    CrawledPageResponse,
)
from app.schemas.pdf import PdfListResponse, PdfResponse
from app.services import crawl_service

router = APIRouter()


@router.post("/jobs", status_code=201)
def create_job(
    payload: CrawlJobCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CrawlJobResponse:
    job = crawl_service.create_crawl_job(db, user, payload.start_url, payload.depth)
    return CrawlJobResponse.model_validate(job)


@router.get("/jobs")
def list_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CrawlJobListResponse:
    jobs = crawl_service.get_user_jobs(db, user.id)
    return CrawlJobListResponse(
        jobs=[CrawlJobResponse.model_validate(j) for j in jobs]
    )


@router.get("/jobs/{job_id}")
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CrawlJobResponse:
    job = crawl_service.get_job(db, user.id, job_id)
    return CrawlJobResponse.model_validate(job)


@router.get("/jobs/{job_id}/pages")
def get_job_pages(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[CrawledPageResponse]:
    pages = crawl_service.get_job_pages(db, user.id, job_id)
    return [CrawledPageResponse.model_validate(p) for p in pages]


@router.get("/jobs/{job_id}/pdfs")
def get_job_pdfs(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PdfListResponse:
    pdfs = crawl_service.get_job_pdfs(db, user.id, job_id)
    return PdfListResponse(pdfs=[PdfResponse.model_validate(p) for p in pdfs])
