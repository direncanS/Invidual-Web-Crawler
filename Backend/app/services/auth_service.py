import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import status
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import error_response
from app.core.security import create_access_token
from app.models.user import User, PasswordResetToken
from app.services.email_service import send_reset_email


def register_user(db: Session, nickname: str, email: str, password: str) -> User:
    if db.query(User).filter(User.nickname == nickname).first():
        error_response("nickname_already_exists", "Nickname already taken", status.HTTP_400_BAD_REQUEST)

    if db.query(User).filter(User.email == email).first():
        error_response("email_already_exists", "Email already registered", status.HTTP_400_BAD_REQUEST)

    user = User(
        nickname=nickname,
        email=email,
        password_hash=bcrypt.hash(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, email_or_nickname: str, password: str) -> str:
    if "@" in email_or_nickname:
        user = db.query(User).filter(User.email == email_or_nickname).first()
    else:
        user = db.query(User).filter(User.nickname == email_or_nickname).first()

    if user is None or not bcrypt.verify(password, user.password_hash):
        error_response("invalid_credentials", "Invalid email/nickname or password", status.HTTP_401_UNAUTHORIZED)

    return create_access_token(str(user.id))


def create_reset_token(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.reset_token_ttl_seconds)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    send_reset_email(user.email, raw_token)


def reset_password(db: Session, token: str, new_password: str) -> None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()

    if reset_token is None:
        error_response("reset_token_invalid", "Invalid reset token", status.HTTP_400_BAD_REQUEST)

    if reset_token.used_at is not None:
        error_response("reset_token_used", "Reset token already used", status.HTTP_400_BAD_REQUEST)

    if datetime.now(timezone.utc) > reset_token.expires_at:
        error_response("reset_token_expired", "Reset token has expired", status.HTTP_400_BAD_REQUEST)

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    user.password_hash = bcrypt.hash(new_password)
    reset_token.used_at = datetime.now(timezone.utc)
    db.commit()
