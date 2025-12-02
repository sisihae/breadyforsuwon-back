from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from app.models import Bakery, BreadTag
from app.schemas import BakeryCreate, BakeryUpdate


class BakeryRepository:
    """Repository for Bakery database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, bakery_id: UUID) -> Optional[Bakery]:
        """Get bakery by ID"""
        return self.db.query(Bakery).filter(Bakery.id == bakery_id).first()
    
    def get_by_name(self, name: str) -> Optional[Bakery]:
        """Get bakery by name"""
        return self.db.query(Bakery).filter(Bakery.name == name).first()
    
    def get_by_shop_id(self, shop_id: str) -> Optional[Bakery]:
        """Get bakery by shop_id"""
        return self.db.query(Bakery).filter(Bakery.shop_id == shop_id).first()
    
    def get_all(self) -> List[Bakery]:
        """Get all bakeries"""
        return self.db.query(Bakery).all()
    
    def get_by_district(self, district: str, limit: int = 100) -> List[Bakery]:
        """Get bakeries by district"""
        return self.db.query(Bakery).filter(Bakery.district == district).limit(limit).all()
    
    def get_top_rated(self, limit: int = 10) -> List[Bakery]:
        """Get top-rated bakeries"""
        return self.db.query(Bakery).order_by(Bakery.rating.desc()).limit(limit).all()
    
    def get_by_ids(self, bakery_ids: List[UUID]) -> List[Bakery]:
        """Get multiple bakeries by IDs"""
        return self.db.query(Bakery).filter(Bakery.id.in_(bakery_ids)).all()
    
    def get_by_bread_tags(self, tags: List[str], limit: int = 100) -> List[Bakery]:
        """Get bakeries by bread tags
        
        Args:
            tags: List of bread tags to filter (크로아상, 식빵, 파이 등)
            limit: Maximum number of results
            
        Returns:
            List of bakeries that have at least one matching tag
        """
        # Prefer relational tag lookup if BreadTag table exists
        if tags:
            # Try relational join: bakeries that have any of the provided tag names
            query = self.db.query(Bakery).join(Bakery.bread_tags_rel).filter(BreadTag.name.in_(tags)).distinct()
            return query.limit(limit).all()

        return []

    def get_bakeries_by_tag(self, tag_name: str, limit: int = 100) -> List[Bakery]:
        """Get bakeries that sell a specific bread tag (tag name)

        Falls back to ARRAY-based contains search if relational data is not populated.
        """
        # Relational lookup first
        tag = self.db.query(BreadTag).filter(BreadTag.name == tag_name).first()
        if tag:
            return tag.bakeries[:limit]

        # Fallback: ARRAY contains
        return self.db.query(Bakery).filter(Bakery.bread_tags.contains([tag_name])).limit(limit).all()
    
    def get_by_filters(
        self,
        district: Optional[str] = None,
        bread_tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        limit: int = 100
    ) -> List[Bakery]:
        """Get bakeries with multiple filters
        
        Args:
            district: Filter by district
            bread_tags: Filter by bread tags (AND logic - must have all tags)
            min_rating: Minimum rating
            limit: Maximum number of results
            
        Returns:
            List of filtered bakeries
        """
        query = self.db.query(Bakery)
        
        if district:
            query = query.filter(Bakery.district == district)
        
        if min_rating is not None:
            query = query.filter(Bakery.rating >= min_rating)
        
        if bread_tags:
            for tag in bread_tags:
                query = query.filter(Bakery.bread_tags.contains([tag]))
        
        return query.limit(limit).all()
    
    def create(self, bakery_data: BakeryCreate) -> Bakery:
        """Create a new bakery"""
        db_bakery = Bakery(**bakery_data.model_dump())
        self.db.add(db_bakery)
        self.db.commit()
        self.db.refresh(db_bakery)
        return db_bakery
    
    def update(self, bakery_id: UUID, bakery_data: BakeryUpdate) -> Optional[Bakery]:
        """Update a bakery"""
        db_bakery = self.get_by_id(bakery_id)
        if not db_bakery:
            return None
        
        update_data = bakery_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_bakery, key, value)
        
        self.db.commit()
        self.db.refresh(db_bakery)
        return db_bakery
    
    def delete(self, bakery_id: UUID) -> bool:
        """Delete a bakery"""
        db_bakery = self.get_by_id(bakery_id)
        if not db_bakery:
            return False
        
        self.db.delete(db_bakery)
        self.db.commit()
        return True
    
    def search_by_name(self, name_query: str, limit: int = 10) -> List[Bakery]:
        """Search bakeries by name (partial match)"""
        return self.db.query(Bakery).filter(
            Bakery.name.ilike(f"%{name_query}%")
        ).limit(limit).all()
