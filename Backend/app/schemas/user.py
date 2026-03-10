from pydantic import BaseModel, EmailStr
from typing import Optional

class MeUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None