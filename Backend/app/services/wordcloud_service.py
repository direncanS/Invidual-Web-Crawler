import uuid

from sqlalchemy.orm import Session

from app.core.errors import error_response
from app.models.pdf import PdfDocument
from app.models.wordcloud import WordcloudArtifact
from app.models.user import User


def create_single(db: Session, user: User, pdf_id: uuid.UUID) -> WordcloudArtifact:
    pdf = (
        db.query(PdfDocument)
        .filter(PdfDocument.id == pdf_id, PdfDocument.user_id == user.id)
        .first()
    )
    if pdf is None:
        error_response("not_found", "PDF not found", 404)

    artifact = WordcloudArtifact(user_id=user.id, mode="single")
    artifact.pdfs.append(pdf)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    from app.tasks.wordcloud_tasks import generate_wordcloud

    generate_wordcloud.delay(str(artifact.id))
    return artifact


def create_multi(db: Session, user: User, pdf_ids: list[uuid.UUID]) -> WordcloudArtifact:
    pdfs = (
        db.query(PdfDocument)
        .filter(PdfDocument.id.in_(pdf_ids), PdfDocument.user_id == user.id)
        .all()
    )
    if len(pdfs) != len(pdf_ids):
        error_response("not_found", "One or more PDFs not found", 404)

    artifact = WordcloudArtifact(user_id=user.id, mode="multi")
    artifact.pdfs.extend(pdfs)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    from app.tasks.wordcloud_tasks import generate_wordcloud

    generate_wordcloud.delay(str(artifact.id))
    return artifact


def create_interval(
    db: Session, user: User, start, end
) -> WordcloudArtifact:
    pdfs = (
        db.query(PdfDocument)
        .filter(
            PdfDocument.user_id == user.id,
            PdfDocument.downloaded_at >= start,
            PdfDocument.downloaded_at <= end,
        )
        .all()
    )
    if not pdfs:
        error_response("not_found", "No PDFs found in the given interval", 404)

    artifact = WordcloudArtifact(
        user_id=user.id,
        mode="interval",
        interval_start=start,
        interval_end=end,
    )
    artifact.pdfs.extend(pdfs)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    from app.tasks.wordcloud_tasks import generate_wordcloud

    generate_wordcloud.delay(str(artifact.id))
    return artifact


def get_image_path(
    db: Session, user_id: uuid.UUID, artifact_id: uuid.UUID
) -> str:
    artifact = (
        db.query(WordcloudArtifact)
        .filter(
            WordcloudArtifact.id == artifact_id,
            WordcloudArtifact.user_id == user_id,
        )
        .first()
    )
    if artifact is None:
        error_response("not_found", "Wordcloud artifact not found", 404)
    if artifact.image_path is None:
        error_response("not_ready", "Wordcloud image not yet generated", 409)
    return artifact.image_path
