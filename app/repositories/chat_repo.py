from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.models import ChatHistory


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_history(self, user_message: str, bot_response: str, metadata_json: Optional[dict] = None) -> ChatHistory:
        entry = ChatHistory(user_message=user_message, bot_response=bot_response, metadata_json=metadata_json)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_by_id(self, history_id: UUID) -> Optional[ChatHistory]:
        return self.db.query(ChatHistory).filter(ChatHistory.id == history_id).first()

    def list_recent(self, limit: int = 100) -> List[ChatHistory]:
        return self.db.query(ChatHistory).order_by(ChatHistory.created_at.desc()).limit(limit).all()
