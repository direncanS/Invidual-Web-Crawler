from pydantic import BaseModel

from app.schemas.pdf import PdfResponse


class WordSearchResponse(BaseModel):
    results: list[PdfResponse]
