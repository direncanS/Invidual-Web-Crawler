import logging

from app.core.celery_app import celery
from app.db.session import SessionLocal
from app.models.pdf import PdfDocument, PdfTopWordsStat
from app.services.pdf_service import extract_text, compute_top_words

logger = logging.getLogger(__name__)


@celery.task(name="app.tasks.pdf_tasks.process_pdf")
def process_pdf(pdf_id: str) -> None:
    db = SessionLocal()
    try:
        pdf = db.query(PdfDocument).filter(PdfDocument.id == pdf_id).first()
        if pdf is None:
            logger.error("PDF document %s not found", pdf_id)
            return

        try:
            text = extract_text(pdf.file_path)
            top_words = compute_top_words(text, n=10)
        except Exception:
            logger.exception("Failed to extract text from PDF %s", pdf_id)
            top_words = []

        stat = PdfTopWordsStat(
            pdf_id=pdf.id,
            words_json=top_words,
        )
        db.add(stat)
        db.commit()

    except Exception:
        logger.exception("process_pdf task failed for %s", pdf_id)
    finally:
        db.close()
