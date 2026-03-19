import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PdfDocument(Base):
    __tablename__ = "pdf_documents"
    __table_args__ = (
        UniqueConstraint(
            "crawl_job_id", "source_url", name="uq_pdf_documents_job_source"
        ),
        Index("ix_pdf_documents_user_downloaded", "user_id", "downloaded_at"),
        Index("ix_pdf_documents_crawl_job", "crawl_job_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    crawl_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_url: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    crawl_job: Mapped["CrawlJob"] = relationship(  # noqa: F821
        back_populates="pdf_documents"
    )
    top_words_stat: Mapped["PdfTopWordsStat | None"] = relationship(
        back_populates="pdf_document", uselist=False, cascade="all, delete-orphan"
    )


class PdfTopWordsStat(Base):
    __tablename__ = "pdf_top_words_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pdf_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pdf_documents.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    words_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    pdf_document: Mapped["PdfDocument"] = relationship(back_populates="top_words_stat")
