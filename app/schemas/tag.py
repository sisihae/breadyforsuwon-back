from pydantic import BaseModel
from typing import Optional


class BreadTagBase(BaseModel):
    name: str
    slug: Optional[str] = None
    # description was removed from the model; keep schemas minimal


class BreadTagResponse(BreadTagBase):
    id: int

    class Config:
        from_attributes = True
