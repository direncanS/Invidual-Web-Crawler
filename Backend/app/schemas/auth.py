from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    nickname: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email_or_nickname: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)