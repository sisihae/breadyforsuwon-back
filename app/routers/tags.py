from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import get_db
from app.repositories import BakeryRepository
from app.models import BreadTag
from app.schemas import BreadTagResponse, BakeryResponse


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[BreadTagResponse])
async def list_tags(db: Session = Depends(get_db)):
    """List all known bread tags"""
    tags = db.query(BreadTag).order_by(BreadTag.name).all()
    return tags


@router.get("/{tag_name}/bakeries", response_model=list[BakeryResponse])
async def bakeries_for_tag(
    tag_name: str,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
):
    """Return bakeries that sell the given bread tag"""
    repo = BakeryRepository(db)
    bakeries = repo.get_bakeries_by_tag(tag_name, limit=limit)
    if bakeries is None:
        raise HTTPException(status_code=404, detail="Tag not found or no bakeries")
    return bakeries
