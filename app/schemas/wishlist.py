from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class WishlistItemCreate(BaseModel):
    bakery_id: UUID


class WishlistItemUpdate(BaseModel):
    note: Optional[str] = None
    visited: Optional[bool] = None


class WishlistItemResponse(BaseModel):
    id: UUID
    user_id: UUID
    bakery_id: UUID
    bakery_name: str
    bakery_address: str
    bread_types: List[str]
    note: Optional[str]
    visited: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
