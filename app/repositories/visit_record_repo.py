from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.models import BakeryVisitRecord


class BakeryVisitRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID, bakery_id: UUID, visit_date, rating: int, bread_purchased: Optional[str] = None, review: Optional[str] = None) -> BakeryVisitRecord:
        record = BakeryVisitRecord(
            user_id=user_id,
            bakery_id=bakery_id,
            visit_date=visit_date,
            rating=rating,
            bread_purchased=bread_purchased,
            review=review
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, record_id: UUID) -> Optional[BakeryVisitRecord]:
        return self.db.query(BakeryVisitRecord).filter(BakeryVisitRecord.id == record_id).first()

    def list_by_user(self, user_id: UUID) -> List[BakeryVisitRecord]:
        return self.db.query(BakeryVisitRecord).filter(BakeryVisitRecord.user_id == user_id).order_by(BakeryVisitRecord.visit_date.desc()).all()

    def update(self, record_id: UUID, visit_date=None, rating: Optional[int] = None, bread_purchased: Optional[str] = None, review: Optional[str] = None) -> Optional[BakeryVisitRecord]:
        record = self.get_by_id(record_id)
        if not record:
            return None
        if visit_date is not None:
            record.visit_date = visit_date
        if rating is not None:
            record.rating = rating
        if bread_purchased is not None:
            record.bread_purchased = bread_purchased
        if review is not None:
            record.review = review
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record_id: UUID) -> bool:
        record = self.get_by_id(record_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True
