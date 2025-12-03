from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.config import get_db
from app.repositories import ChatRepository
from app.schemas.chat_history import ChatHistoryResponse


router = APIRouter(prefix="/chat/history", tags=["chat-history"])


@router.get("", response_model=list[ChatHistoryResponse])
async def list_chat_history(db: Session = Depends(get_db), limit: int = 100):
    repo = ChatRepository(db)
    entries = repo.list_recent(limit=limit)
    return entries


@router.get("/{id}", response_model=ChatHistoryResponse)
async def get_chat_history(id: UUID, db: Session = Depends(get_db)):
    repo = ChatRepository(db)
    history = repo.get_by_id(id)
    if not history:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return history


@router.delete("/{id}", status_code=204)
async def delete_chat_history(id: UUID, db: Session = Depends(get_db)):
    repo = ChatRepository(db)
    deleted = repo.delete_by_id(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return None
