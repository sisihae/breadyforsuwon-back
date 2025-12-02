from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class ChatHistoryCreate(BaseModel):
    user_message: str
    bot_response: str
    metadata_json: Optional[Dict] = None


class ChatHistoryResponse(BaseModel):
    id: UUID
    user_message: str
    bot_response: str
    metadata_json: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
