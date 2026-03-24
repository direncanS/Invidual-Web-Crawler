import uuid

from sqlalchemy.orm import Session

from app.models.pdf import PdfDocument, PdfTopWordsStat


def search_top_words(
    db: Session, user_id: uuid.UUID, word: str
) -> list[PdfDocument]:
    word_lower = word.lower()
    stats = (
        db.query(PdfTopWordsStat)
        .join(PdfDocument, PdfTopWordsStat.pdf_id == PdfDocument.id)
        .filter(PdfDocument.user_id == user_id)
        .all()
    )
    matching_pdf_ids: list[uuid.UUID] = []
    for stat in stats:
        words_list = stat.words_json
        if isinstance(words_list, list):
            for entry in words_list:
                if isinstance(entry, dict) and entry.get("word", "").lower() == word_lower:
                    matching_pdf_ids.append(stat.pdf_id)
                    break

    if not matching_pdf_ids:
        return []

    return (
        db.query(PdfDocument)
        .filter(PdfDocument.id.in_(matching_pdf_ids))
        .all()
    )
