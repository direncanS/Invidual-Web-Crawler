import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    SmallInteger,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"
    __table_args__ = (
        CheckConstraint("depth >= 1 AND depth <= 3", name="ck_crawl_jobs_depth"),
        Index("ix_crawl_jobs_user_created", "user_id", "created_at"),
        Index("ix_crawl_jobs_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_url: Mapped[str] = mapped_column(String, nullable=False)
    depth: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="queued"
    )
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="crawl_jobs")  # noqa: F821
    pages: Mapped[list["CrawledPage"]] = relationship(
        back_populates="crawl_job", cascade="all, delete-orphan"
    )
    pdf_documents: Mapped[list["PdfDocument"]] = relationship(  # noqa: F821
        back_populates="crawl_job", cascade="all, delete-orphan"
    )


class CrawledPage(Base):
    __tablename__ = "crawled_pages"
    __table_args__ = (
        UniqueConstraint("crawl_job_id", "url", name="uq_crawled_pages_job_url"),
        CheckConstraint(
            "depth_level >= 1 AND depth_level <= 3",
            name="ck_crawled_pages_depth_level",
        ),
        Index("ix_crawled_pages_job", "crawl_job_id"),
        Index("ix_crawled_pages_job_depth", "crawl_job_id", "depth_level"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    crawl_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    depth_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    crawl_job: Mapped["CrawlJob"] = relationship(back_populates="pages")
