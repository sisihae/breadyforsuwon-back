from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.config import get_db
from app.models import Bakery
from app.repositories import BakeryRepository
from app.schemas import BakeryResponse, BakeryCreate, BakeryUpdate


router = APIRouter(prefix="/bakeries", tags=["bakeries"])


@router.get("/{bakery_id}", response_model=BakeryResponse)
async def get_bakery(
    bakery_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific bakery by ID"""
    repo = BakeryRepository(db)
    bakery = repo.get_by_id(bakery_id)
    if not bakery:
        raise HTTPException(status_code=404, detail="Bakery not found")
    return bakery


@router.get("", response_model=list[BakeryResponse])
async def get_all_bakeries(
    db: Session = Depends(get_db),
    district: str = Query(None, description="Filter by district"),
    category: str = Query(None, description="Filter by category"),
    rating: float = Query(None, ge=1.0, le=5.0, description="Minimum rating filter"),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all bakeries with optional filters (category, rating, district)"""
    repo = BakeryRepository(db)
    query = repo.db.query(Bakery)
    
    # Apply filters
    if district:
        query = query.filter(Bakery.district == district)
    
    if category:
        query = query.filter(Bakery.category == category)
    
    if rating is not None:
        query = query.filter(Bakery.rating >= rating)
    
    bakeries = query.limit(limit).all()
    return bakeries


@router.get("/top-rated", response_model=list[BakeryResponse])
async def get_top_rated(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
):
    """Get top-rated bakeries"""
    repo = BakeryRepository(db)
    return repo.get_top_rated(limit=limit)


@router.post("", response_model=BakeryResponse)
async def create_bakery(
    bakery: BakeryCreate,
    db: Session = Depends(get_db)
):
    """Create a new bakery"""
    repo = BakeryRepository(db)
    return repo.create(bakery)


@router.put("/{bakery_id}", response_model=BakeryResponse)
async def update_bakery(
    bakery_id: UUID,
    bakery_update: BakeryUpdate,
    db: Session = Depends(get_db)
):
    """Update a bakery"""
    repo = BakeryRepository(db)
    updated_bakery = repo.update(bakery_id, bakery_update)
    if not updated_bakery:
        raise HTTPException(status_code=404, detail="Bakery not found")
    return updated_bakery


@router.delete("/{bakery_id}")
async def delete_bakery(
    bakery_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a bakery"""
    repo = BakeryRepository(db)
    if not repo.delete(bakery_id):
        raise HTTPException(status_code=404, detail="Bakery not found")
    return {"message": "Bakery deleted successfully"}


@router.get("/search/by-name", response_model=list[BakeryResponse])
async def search_by_name(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
):
    """Search bakeries by name"""
    repo = BakeryRepository(db)
    return repo.search_by_name(q, limit=limit)
