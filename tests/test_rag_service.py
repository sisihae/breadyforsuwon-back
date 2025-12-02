"""
Test example for RAG service
"""
import pytest
from sqlalchemy.orm import Session
from app.services import RAGService


@pytest.fixture
def rag_service(db: Session):
    return RAGService(db)


def test_search_bakeries(rag_service: RAGService):
    """Test bakery search functionality"""
    results = rag_service.search_bakeries(
        query="분위기 좋은 빵집",
        top_k=5
    )
    assert isinstance(results, list)
    assert len(results) <= 5


def test_chat(rag_service: RAGService):
    """Test chat functionality"""
    response = rag_service.chat(
        message="데이트하기 좋은 빵집 추천해줄래?",
        context_count=3
    )
    assert response.response
    assert isinstance(response.recommendations, list)


def test_search_by_district(rag_service: RAGService):
    """Test search with district filter"""
    results = rag_service.search_bakeries(
        query="카페 같은 분위기",
        district="영통구",
        top_k=5
    )
    # All results should be in the specified district
    for result in results:
        assert result.district == "영통구"
