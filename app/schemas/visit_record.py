from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class BakeryVisitRecordCreate(BaseModel):
    bakery_id: UUID
    visit_date: date
    rating: int = Field(..., ge=1, le=5)
    bread_purchased: Optional[str] = None
    review: Optional[str] = None


class BakeryVisitRecordUpdate(BaseModel):
    visit_date: Optional[date] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    bread_purchased: Optional[str] = None
    review: Optional[str] = None


class BakeryVisitRecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    bakery_id: UUID
    bakery_name: str
    bakery_address: str
    visit_date: date
    rating: int
    bread_purchased: Optional[str]
    review: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
