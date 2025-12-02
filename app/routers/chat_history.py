from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_db
from app.repositories import ChatRepository
from app.schemas.chat_history import ChatHistoryResponse


router = APIRouter(prefix="/chat/history", tags=["chat-history"])


@router.get("", response_model=list[ChatHistoryResponse])
async def list_chat_history(db: Session = Depends(get_db), limit: int = 100):
    repo = ChatRepository(db)
    entries = repo.list_recent(limit=limit)
    return entries
