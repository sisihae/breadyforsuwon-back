from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid
from app.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kakao_id = Column(String(64), nullable=True, unique=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    name = Column(String(255), nullable=True)
    profile_image = Column(String(500), nullable=True)  # URL to profile image
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, kakao_id={self.kakao_id}, email={self.email})>"
