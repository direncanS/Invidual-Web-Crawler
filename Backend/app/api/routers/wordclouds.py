import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.wordcloud import (
    WordcloudIntervalRequest,
    WordcloudMultiRequest,
    WordcloudResponse,
    WordcloudSingleRequest,
)
from app.services import wordcloud_service

router = APIRouter()


@router.post("/single", status_code=201)
def create_single(
    payload: WordcloudSingleRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WordcloudResponse:
    artifact = wordcloud_service.create_single(db, user, payload.pdf_id)
    return WordcloudResponse.model_validate(artifact)


@router.post("/multi", status_code=201)
def create_multi(
    payload: WordcloudMultiRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WordcloudResponse:
    artifact = wordcloud_service.create_multi(db, user, payload.pdf_ids)
    return WordcloudResponse.model_validate(artifact)


@router.post("/interval", status_code=201)
def create_interval(
    payload: WordcloudIntervalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WordcloudResponse:
    artifact = wordcloud_service.create_interval(
        db, user, payload.start_datetime, payload.end_datetime
    )
    return WordcloudResponse.model_validate(artifact)


@router.get("/{artifact_id}/image")
def get_image(
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileResponse:
    image_path = wordcloud_service.get_image_path(db, user.id, artifact_id)
    return FileResponse(path=image_path, media_type="image/png")
