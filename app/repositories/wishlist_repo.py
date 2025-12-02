from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.models import WishlistItem


class WishlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID, bakery_id: UUID, note: Optional[str] = None) -> WishlistItem:
        item = WishlistItem(user_id=user_id, bakery_id=bakery_id, note=note)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_id(self, item_id: UUID) -> Optional[WishlistItem]:
        return self.db.query(WishlistItem).filter(WishlistItem.id == item_id).first()

    def list_by_user(self, user_id: UUID) -> List[WishlistItem]:
        return self.db.query(WishlistItem).filter(WishlistItem.user_id == user_id).order_by(WishlistItem.created_at.desc()).all()

    def update(self, item_id: UUID, note: Optional[str] = None, visited: Optional[bool] = None) -> Optional[WishlistItem]:
        item = self.get_by_id(item_id)
        if not item:
            return None
        if note is not None:
            item.note = note
        if visited is not None:
            item.visited = visited
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item_id: UUID) -> bool:
        item = self.get_by_id(item_id)
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True
