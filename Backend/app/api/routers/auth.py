from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.services.auth_service import (
    register_user, login_user,
    create_reset_token, reset_password,
)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, payload.nickname, payload.email, payload.password)
    return {"id": str(user.id), "nickname": user.nickname, "email": user.email}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db, payload.email_or_nickname, payload.password)
    return {"access_token": token}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    create_reset_token(db, payload.email)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password_endpoint(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_password(db, payload.token, payload.new_password)
    return {"message": "Password has been reset successfully."}
