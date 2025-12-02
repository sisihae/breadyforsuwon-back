from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services import RAGService


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat endpoint with RAG
    
    빵집을 추천받는 챗봇 엔드포인트입니다.
    
    Args:
        message: 사용자의 질문 (예: "분위기 좋은 카페 같은 빵집")
        district: 지역 필터 (선택, 예: "영통구")
        bread_tags: 빵 종류 필터 (선택, 예: ["크로아상", "식빵"])
        context_count: 참고할 빵집 개수 (1-20, 기본값: 5)
    """
    try:
        rag_service = RAGService(db)
        response = rag_service.chat(
            message=request.message,
            district=request.district,
            bread_tags=request.bread_tags,
            context_count=request.context_count
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat: {str(e)}"
        )
