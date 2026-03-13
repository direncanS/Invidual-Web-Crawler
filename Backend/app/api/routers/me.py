from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import MeUpdateRequest
from app.services.user_service import get_profile, update_profile

router = APIRouter()


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return get_profile(user)


@router.put("/me")
def update_me(
    payload: MeUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_profile(db, user, payload.nickname, payload.email)
