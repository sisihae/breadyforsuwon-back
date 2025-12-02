from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class BakeryBase(BaseModel):
    """Base schema for Bakery"""
    name: str
    shop_id: Optional[str] = None
    rating: Optional[float] = None
    address: str
    tel: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    district: Optional[str] = None
    opening_hours: Optional[str] = None
    ai_summary: Optional[str] = None
    bread_tags: Optional[List[str]] = Field(
        default=None,
        description="빵 종류 태그 (예: ['크로아상', '식빵', '파이', '케이크'])"
    )


class BakeryCreate(BakeryBase):
    """Schema for creating a Bakery"""
    pass


class BakeryUpdate(BaseModel):
    """Schema for updating a Bakery"""
    name: Optional[str] = None
    rating: Optional[float] = None
    address: Optional[str] = None
    tel: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    district: Optional[str] = None
    opening_hours: Optional[str] = None
    ai_summary: Optional[str] = None
    bread_tags: Optional[List[str]] = Field(
        default=None,
        description="빵 종류 태그"
    )


class BakeryResponse(BakeryBase):
    """Schema for Bakery response"""
    id: UUID
    vector_db_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BakeryWithDistance(BakeryResponse):
    """Bakery response with similarity/distance score"""
    similarity_score: float = Field(..., description="Vector similarity score (0-1)")
    relevance_reason: Optional[str] = None


class SearchQuery(BaseModel):
    """Schema for search query"""
    query: str = Field(..., description="Search query for RAG")
    district: Optional[str] = None
    min_rating: Optional[float] = None
    bread_tags: Optional[List[str]] = Field(
        default=None,
        description="빵 종류로 필터링"
    )
    top_k: int = Field(default=5, ge=1, le=20)


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str
    district: Optional[str] = None
    bread_tags: Optional[List[str]] = Field(
        default=None,
        description="특정 빵 종류로 필터링"
    )
    context_count: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    """Schema for chat response"""
    response: str
    recommendations: list[BakeryWithDistance]
    sources_used: list[str] = Field(default_factory=list)


class BakeryWithScoreResponse(BaseModel):
    """Bakery with relevance score"""
    bakery: BakeryResponse
    score: float
