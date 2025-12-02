from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.schemas import SearchQuery, BakeryWithDistance
from app.services import RAGService


router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=list[BakeryWithDistance])
async def search(
    request: SearchQuery,
    db: Session = Depends(get_db)
):
    """Search bakeries with RAG
    
    의미 기반 검색으로 빵집을 찾습니다.
    
    Args:
        query: 검색 쿼리 (예: "분위기 좋은 빵집", "카페 같은 곳")
        district: 지역 필터 (선택, 예: "영통구")
        bread_tags: 빵 종류 필터 (선택, 예: ["크로아상", "파이"])
        min_rating: 최소 평점 필터 (선택)
        top_k: 반환할 결과 개수 (1-20, 기본값: 5)
    """
    try:
        rag_service = RAGService(db)
        results = rag_service.search_bakeries(
            query=request.query,
            district=request.district,
            bread_tags=request.bread_tags,
            top_k=request.top_k
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search: {str(e)}"
        )
