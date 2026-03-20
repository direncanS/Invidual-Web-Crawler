import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.errors import error_response
from app.models.user import User
from app.schemas.pdf import PdfListResponse, PdfResponse, TopWordsResponse, TopWordEntry
from app.services import pdf_service

router = APIRouter()


@router.get("/")
def list_pdfs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PdfListResponse:
    pdfs = pdf_service.get_user_pdfs(db, user.id)
    return PdfListResponse(pdfs=[PdfResponse.model_validate(p) for p in pdfs])


@router.get("/{pdf_id}")
def get_pdf(
    pdf_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PdfResponse:
    pdf = pdf_service.get_pdf(db, user.id, pdf_id)
    return PdfResponse.model_validate(pdf)


@router.get("/{pdf_id}/download")
def download_pdf(
    pdf_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileResponse:
    pdf = pdf_service.get_pdf(db, user.id, pdf_id)
    return FileResponse(
        path=pdf.file_path,
        media_type="application/pdf",
        filename=pdf.file_path.split("/")[-1],
    )


@router.get("/{pdf_id}/stats/top-words")
def get_top_words(
    pdf_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TopWordsResponse:
    stat = pdf_service.get_pdf_stats(db, user.id, pdf_id)
    if stat is None:
        error_response("not_ready", "Top words not yet computed", 409)
    words = [
        TopWordEntry(word=entry["word"], count=entry["count"])
        for entry in stat.words_json
        if isinstance(entry, dict)
    ]
    return TopWordsResponse(pdf_id=pdf_id, words=words)
