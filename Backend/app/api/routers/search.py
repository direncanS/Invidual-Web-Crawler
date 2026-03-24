from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.pdf import PdfResponse
from app.schemas.search import WordSearchResponse
from app.services import search_service

router = APIRouter()


@router.get("/top-words")
def search_top_words(
    word: str = Query(min_length=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WordSearchResponse:
    pdfs = search_service.search_top_words(db, user.id, word)
    return WordSearchResponse(
        results=[PdfResponse.model_validate(p) for p in pdfs]
    )
