from collections.abc import Generator

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.errors import error_response
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User

_bearer = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        error_response("invalid_token", "Invalid or expired token", status.HTTP_401_UNAUTHORIZED)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        error_response("user_not_found", "User not found", status.HTTP_401_UNAUTHORIZED)
    return user
