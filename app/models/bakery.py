from sqlalchemy import Column, String, Float, Text, DateTime, UUID, Index
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.config.database import Base


class Bakery(Base):
    """Bakery Model for RDB"""
    
    __tablename__ = "bakeries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    shop_id = Column(String(50), nullable=True, unique=True) 
    rating = Column(Float, nullable=True)
    address = Column(Text, nullable=False)
    district = Column(String(50), nullable=True, index=True)  # 권선구, 영통구 등
    opening_hours = Column(String(255), nullable=True)
    
    # Legacy array column (kept for backward compatibility / backfill)
    bread_tags = Column(PG_ARRAY(String), nullable=True, default=list)

    # Relationship to BreadTag model (many-to-many). Use `bread_tags_rel` to
    # avoid name collision with the legacy `bread_tags` array column.
    bread_tags_rel = relationship("BreadTag", secondary="bakery_bread_tag", back_populates="bakeries")
    
    # Vector DB 연결
    vector_db_id = Column(String(255), nullable=True)
    
    # AI Summary (벡터DB에서 동기화)
    ai_summary = Column(Text, nullable=True)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 인덱스
    __table_args__ = (
        Index('idx_bakery_name', 'name'),
        Index('idx_bakery_district', 'district'),
        Index('idx_bakery_rating', 'rating'),
        Index('idx_bakery_shop_id', 'shop_id'),
    )
    
    def __repr__(self):
        return f"<Bakery(id={self.id}, name={self.name}, rating={self.rating})>"
