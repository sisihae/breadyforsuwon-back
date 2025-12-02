from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.config.database import get_db
from app.repositories.visit_record_repo import BakeryVisitRecordRepository
from app.repositories.bakery_repo import BakeryRepository
from app.schemas.visit_record import BakeryVisitRecordCreate, BakeryVisitRecordUpdate, BakeryVisitRecordResponse
from app.utils.auth import get_current_user_id
from app.config import settings

router = APIRouter()


def get_current_user(session: Optional[str] = Cookie(None)) -> UUID:
    """Dependency to extract user_id from session cookie."""
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = get_current_user_id(session)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@router.get("/visit-records", response_model=List[BakeryVisitRecordResponse])
def list_visit_records(current_user: UUID = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all visit records for the current user."""
    repo = BakeryVisitRecordRepository(db)
    records = repo.list_by_user(current_user)
    
    # Enrich records with bakery details
    bakery_repo = BakeryRepository(db)
    result = []
    for record in records:
        bakery = bakery_repo.get_by_id(record.bakery_id)
        if not bakery:
            continue
        
        result.append(BakeryVisitRecordResponse(
            id=record.id,
            user_id=record.user_id,
            bakery_id=record.bakery_id,
            bakery_name=bakery.name,
            bakery_address=bakery.address,
            visit_date=record.visit_date,
            rating=record.rating,
            bread_purchased=record.bread_purchased,
            review=record.review,
            created_at=record.created_at,
            updated_at=record.updated_at,
        ))
    
    return result


@router.post("/visit-records", response_model=BakeryVisitRecordResponse)
def create_visit_record(
    data: BakeryVisitRecordCreate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new visit record for a bakery."""
    bakery_repo = BakeryRepository(db)
    bakery = bakery_repo.get_by_id(data.bakery_id)
    if not bakery:
        raise HTTPException(status_code=404, detail="Bakery not found")
    
    repo = BakeryVisitRecordRepository(db)
    record = repo.create(
        user_id=current_user,
        bakery_id=data.bakery_id,
        visit_date=data.visit_date,
        rating=data.rating,
        bread_purchased=data.bread_purchased,
        review=data.review
    )
    
    return BakeryVisitRecordResponse(
        id=record.id,
        user_id=record.user_id,
        bakery_id=record.bakery_id,
        bakery_name=bakery.name,
        bakery_address=bakery.address,
        visit_date=record.visit_date,
        rating=record.rating,
        bread_purchased=record.bread_purchased,
        review=record.review,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.patch("/visit-records/{record_id}", response_model=BakeryVisitRecordResponse)
def update_visit_record(
    record_id: UUID,
    data: BakeryVisitRecordUpdate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a visit record."""
    repo = BakeryVisitRecordRepository(db)
    record = repo.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Visit record not found")
    
    if record.user_id != current_user:
        raise HTTPException(status_code=403, detail="Cannot modify another user's visit record")
    
    record = repo.update(
        record_id,
        visit_date=data.visit_date,
        rating=data.rating,
        bread_purchased=data.bread_purchased,
        review=data.review
    )
    
    # Get bakery details
    bakery_repo = BakeryRepository(db)
    bakery = bakery_repo.get_by_id(record.bakery_id)
    
    return BakeryVisitRecordResponse(
        id=record.id,
        user_id=record.user_id,
        bakery_id=record.bakery_id,
        bakery_name=bakery.name if bakery else "",
        bakery_address=bakery.address if bakery else "",
        visit_date=record.visit_date,
        rating=record.rating,
        bread_purchased=record.bread_purchased,
        review=record.review,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.delete("/visit-records/{record_id}")
def delete_visit_record(
    record_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a visit record."""
    repo = BakeryVisitRecordRepository(db)
    record = repo.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Visit record not found")
    
    if record.user_id != current_user:
        raise HTTPException(status_code=403, detail="Cannot delete another user's visit record")
    
    repo.delete(record_id)
    return {"ok": True}
