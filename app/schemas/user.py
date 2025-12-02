from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    kakao_id: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    kakao_id: Optional[str]
    email: Optional[EmailStr]
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
