import uuid

from sqlalchemy.orm import Session

from app.models.crawl import CrawlJob, CrawledPage
from app.models.pdf import PdfDocument
from app.models.user import User
from app.core.errors import error_response


def create_crawl_job(db: Session, user: User, start_url: str, depth: int) -> CrawlJob:
    job = CrawlJob(
        user_id=user.id,
        start_url=start_url,
        depth=depth,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    from app.tasks.crawl_tasks import execute_crawl_job

    execute_crawl_job.delay(str(job.id))
    return job


def get_user_jobs(db: Session, user_id: uuid.UUID) -> list[CrawlJob]:
    return (
        db.query(CrawlJob)
        .filter(CrawlJob.user_id == user_id)
        .order_by(CrawlJob.created_at.desc())
        .all()
    )


def get_job(db: Session, user_id: uuid.UUID, job_id: uuid.UUID) -> CrawlJob:
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user_id)
        .first()
    )
    if job is None:
        error_response("not_found", "Crawl job not found", 404)
    return job


def get_job_pages(db: Session, user_id: uuid.UUID, job_id: uuid.UUID) -> list[CrawledPage]:
    job = get_job(db, user_id, job_id)
    return (
        db.query(CrawledPage)
        .filter(CrawledPage.crawl_job_id == job.id)
        .order_by(CrawledPage.fetched_at)
        .all()
    )


def get_job_pdfs(db: Session, user_id: uuid.UUID, job_id: uuid.UUID) -> list[PdfDocument]:
    job = get_job(db, user_id, job_id)
    return (
        db.query(PdfDocument)
        .filter(PdfDocument.crawl_job_id == job.id)
        .order_by(PdfDocument.downloaded_at)
        .all()
    )
