import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Column,
    Table,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


wordcloud_artifact_pdfs = Table(
    "wordcloud_artifact_pdfs",
    Base.metadata,
    Column(
        "wordcloud_id",
        UUID(as_uuid=True),
        ForeignKey("wordcloud_artifacts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "pdf_id",
        UUID(as_uuid=True),
        ForeignKey("pdf_documents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_wordcloud_artifact_pdfs_pdf", "pdf_id"),
)


class WordcloudArtifact(Base):
    __tablename__ = "wordcloud_artifacts"
    __table_args__ = (
        Index("ix_wordcloud_artifacts_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    interval_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    interval_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    pdfs: Mapped[list["PdfDocument"]] = relationship(  # noqa: F821
        secondary=wordcloud_artifact_pdfs
    )


WordcloudArtifactPdf = wordcloud_artifact_pdfs
