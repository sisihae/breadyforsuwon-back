from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    bakery_id = Column(PG_UUID(as_uuid=True), ForeignKey("bakeries.id"), nullable=False, index=True)
    note = Column(Text, nullable=True)
    visited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="wishlist_items")
    bakery = relationship("Bakery", backref="wishlist_items")

    def __repr__(self):
        return f"<WishlistItem(id={self.id}, user_id={self.user_id}, bakery_id={self.bakery_id}, visited={self.visited})>"
