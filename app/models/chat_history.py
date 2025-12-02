from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSON
from sqlalchemy.sql import func
import uuid
from app.config.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)  # e.g., {'sources': [...], 'bread_tags': [...], 'bakery_ids': [...]} 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, created_at={self.created_at})>"
