import hashlib
import os
import re
import uuid
from collections import Counter

import fitz
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import error_response
from app.core.stopwords import STOP_WORDS
from app.models.pdf import PdfDocument, PdfTopWordsStat
from app.storage.paths import pdf_dir


def download_pdf(
    url: str,
    user_id: uuid.UUID,
    crawl_job_id: uuid.UUID,
    db: Session,
) -> PdfDocument:
    resp = requests.get(url, timeout=settings.request_timeout_seconds)
    resp.raise_for_status()

    content = resp.content
    sha = hashlib.sha256(content).hexdigest()

    directory = pdf_dir(str(user_id), str(crawl_job_id))
    os.makedirs(directory, exist_ok=True)

    filename = os.path.basename(url.split("?")[0]) or "document.pdf"
    file_path = os.path.join(directory, filename)

    # Avoid collisions
    if os.path.exists(file_path):
        base, ext = os.path.splitext(filename)
        file_path = os.path.join(directory, f"{base}_{sha[:8]}{ext}")

    with open(file_path, "wb") as f:
        f.write(content)

    doc = PdfDocument(
        user_id=user_id,
        crawl_job_id=crawl_job_id,
        source_url=url,
        file_path=file_path,
        sha256=sha,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def extract_text(file_path: str) -> str:
    text_parts: list[str] = []
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


_WORD_RE = re.compile(r"[a-zA-ZäöüÄÖÜß]{2,}")


def compute_top_words(text: str, n: int = 10) -> list[dict]:
    words = _WORD_RE.findall(text.lower())
    filtered = [w for w in words if w not in STOP_WORDS]
    counts = Counter(filtered)
    top = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:n]
    return [{"word": word, "count": count} for word, count in top]


def get_user_pdfs(db: Session, user_id: uuid.UUID) -> list[PdfDocument]:
    return (
        db.query(PdfDocument)
        .filter(PdfDocument.user_id == user_id)
        .order_by(PdfDocument.downloaded_at.desc())
        .all()
    )


def get_pdf(db: Session, user_id: uuid.UUID, pdf_id: uuid.UUID) -> PdfDocument:
    pdf = (
        db.query(PdfDocument)
        .filter(PdfDocument.id == pdf_id, PdfDocument.user_id == user_id)
        .first()
    )
    if pdf is None:
        error_response("not_found", "PDF not found", 404)
    return pdf


def get_pdf_stats(db: Session, user_id: uuid.UUID, pdf_id: uuid.UUID) -> PdfTopWordsStat | None:
    pdf = get_pdf(db, user_id, pdf_id)
    return (
        db.query(PdfTopWordsStat)
        .filter(PdfTopWordsStat.pdf_id == pdf.id)
        .first()
    )
