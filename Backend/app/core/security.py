from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from jose import JWTError

from app.core.config import settings

ALGORITHM = "HS256"

def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=settings.jwt_expires_seconds)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    """Decode a JWT and return the subject (user ID).

    Raises ``JWTError`` on invalid or expired tokens.
    """
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    sub: str | None = payload.get("sub")
    if sub is None:
        raise JWTError("Token missing 'sub' claim")
    return sub