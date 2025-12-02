from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base


class BakeryVisitRecord(Base):
    __tablename__ = "bakery_visit_records"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    bakery_id = Column(PG_UUID(as_uuid=True), ForeignKey("bakeries.id"), nullable=False, index=True)
    visit_date = Column(Date, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    bread_purchased = Column(String(255), nullable=True)  # e.g., "크루아상, 바게트"
    review = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="visit_records")
    bakery = relationship("Bakery", backref="visit_records")

    def __repr__(self):
        return f"<BakeryVisitRecord(id={self.id}, user_id={self.user_id}, bakery_id={self.bakery_id}, rating={self.rating})>"
