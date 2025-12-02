from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.config.database import get_db
from app.repositories.wishlist_repo import WishlistRepository
from app.repositories.bakery_repo import BakeryRepository
from app.schemas.wishlist import WishlistItemCreate, WishlistItemUpdate, WishlistItemResponse
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


@router.get("/wishlist", response_model=List[WishlistItemResponse])
def list_wishlist(current_user: UUID = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all wishlist items for the current user."""
    repo = WishlistRepository(db)
    items = repo.list_by_user(current_user)
    
    # Enrich items with bakery details
    bakery_repo = BakeryRepository(db)
    result = []
    for item in items:
        bakery = bakery_repo.get_by_id(item.bakery_id)
        if not bakery:
            continue
        
        # Extract bread types (tags)
        bread_types = []
        if bakery.bread_tags_rel:
            bread_types = [tag.name for tag in bakery.bread_tags_rel]
        
        result.append(WishlistItemResponse(
            id=item.id,
            user_id=item.user_id,
            bakery_id=item.bakery_id,
            bakery_name=bakery.name,
            bakery_address=bakery.address,
            bread_types=bread_types,
            note=item.note,
            visited=item.visited,
            created_at=item.created_at,
            updated_at=item.updated_at,
        ))
    
    return result


@router.post("/wishlist", response_model=WishlistItemResponse)
def create_wishlist_item(
    data: WishlistItemCreate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wishlist item for a bakery."""
    bakery_repo = BakeryRepository(db)
    bakery = bakery_repo.get_by_id(data.bakery_id)
    if not bakery:
        raise HTTPException(status_code=404, detail="Bakery not found")
    
    repo = WishlistRepository(db)
    item = repo.create(user_id=current_user, bakery_id=data.bakery_id)
    
    # Extract bread types
    bread_types = []
    if bakery.bread_tags_rel:
        bread_types = [tag.name for tag in bakery.bread_tags_rel]
    
    return WishlistItemResponse(
        id=item.id,
        user_id=item.user_id,
        bakery_id=item.bakery_id,
        bakery_name=bakery.name,
        bakery_address=bakery.address,
        bread_types=bread_types,
        note=item.note,
        visited=item.visited,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.patch("/wishlist/{item_id}", response_model=WishlistItemResponse)
def update_wishlist_item(
    item_id: UUID,
    data: WishlistItemUpdate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a wishlist item (note or visited status)."""
    repo = WishlistRepository(db)
    item = repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    
    if item.user_id != current_user:
        raise HTTPException(status_code=403, detail="Cannot modify another user's wishlist")
    
    item = repo.update(item_id, note=data.note, visited=data.visited)
    
    # Get bakery details
    bakery_repo = BakeryRepository(db)
    bakery = bakery_repo.get_by_id(item.bakery_id)
    
    bread_types = []
    if bakery and bakery.bread_tags_rel:
        bread_types = [tag.name for tag in bakery.bread_tags_rel]
    
    return WishlistItemResponse(
        id=item.id,
        user_id=item.user_id,
        bakery_id=item.bakery_id,
        bakery_name=bakery.name if bakery else "",
        bakery_address=bakery.address if bakery else "",
        bread_types=bread_types,
        note=item.note,
        visited=item.visited,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.delete("/wishlist/{item_id}")
def delete_wishlist_item(
    item_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a wishlist item."""
    repo = WishlistRepository(db)
    item = repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    
    if item.user_id != current_user:
        raise HTTPException(status_code=403, detail="Cannot delete another user's wishlist item")
    
    repo.delete(item_id)
    return {"ok": True}
