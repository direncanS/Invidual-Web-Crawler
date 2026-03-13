from fastapi import status
from sqlalchemy.orm import Session

from app.core.errors import error_response
from app.models.user import User


def get_profile(user: User) -> dict:
    return {
        "id": str(user.id),
        "nickname": user.nickname,
        "email": user.email,
    }


def update_profile(db: Session, user: User, nickname: str | None, email: str | None) -> dict:
    if nickname is None and email is None:
        error_response("no_fields_to_update", "No fields to update", status.HTTP_400_BAD_REQUEST)

    if nickname is not None:
        existing = db.query(User).filter(User.nickname == nickname, User.id != user.id).first()
        if existing:
            error_response("nickname_already_exists", "Nickname already taken", status.HTTP_400_BAD_REQUEST)
        user.nickname = nickname

    if email is not None:
        existing = db.query(User).filter(User.email == email, User.id != user.id).first()
        if existing:
            error_response("email_already_exists", "Email already registered", status.HTTP_400_BAD_REQUEST)
        user.email = email

    db.commit()
    db.refresh(user)
    return get_profile(user)
