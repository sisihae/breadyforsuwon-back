from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories import BakeryRepository, VectorRepository, ChatRepository
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.schemas import ChatResponse, BakeryWithDistance, SearchQuery


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.bakery_repo = BakeryRepository(db)
        self.vector_repo = VectorRepository()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
    
    def search_bakeries(
        self,
        query: str,
        district: Optional[str] = None,
        bread_tags: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[BakeryWithDistance]:
        """Search bakeries using RAG
        
        Args:
            query: Search query
            district: Optional district filter
            bread_tags: Optional bread tag filters
            top_k: Number of results to return
            
        Returns:
            List of bakeries with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Build filters if district is specified
        filters = None
        if district:
            filters = {"district": {"$eq": district}}
        
        # Query vector DB
        vector_results = self.vector_repo.query(
            embedding=query_embedding,
            top_k=top_k * 2,  # Get more to filter by bread_tags
            filters=filters
        )
        
        if not vector_results:
            return []
        
        # Extract bakery IDs from vector results
        bakery_ids = [
            UUID(result["bakery_id"]) for result in vector_results
        ]
        
        # Get bakery details from RDB
        bakeries = self.bakery_repo.get_by_ids(bakery_ids)
        
        # Filter by bread tags if specified
        if bread_tags:
            bakeries = [
                b for b in bakeries
                if b.bread_tags and any(tag in b.bread_tags for tag in bread_tags)
            ]
        
        # Combine with scores
        results = []
        score_map = {result["bakery_id"]: result["score"] for result in vector_results}
        
        for bakery in bakeries[:top_k]:
            score = score_map.get(str(bakery.id), 0.0)
            results.append(
                BakeryWithDistance(
                    **bakery.__dict__,
                    similarity_score=score,
                    relevance_reason=f"쿼리와 {score:.1%} 유사도"
                )
            )
        
        # Sort by score descending
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return results
    
    def chat(
        self,
        message: str,
        district: Optional[str] = None,
        bread_tags: Optional[List[str]] = None,
        context_count: int = 5
    ) -> ChatResponse:
        """Chat with RAG
        
        Args:
            message: User message
            district: Optional district filter
            bread_tags: Optional bread tag filters
            context_count: Number of context documents to retrieve
            
        Returns:
            ChatResponse with answer and recommendations
        """
        # Search relevant bakeries
        search_results = self.search_bakeries(
            query=message,
            district=district,
            bread_tags=bread_tags,
            top_k=context_count
        )
        
        # Convert to BakeryResponse for LLM context
        bakery_responses = [
            BakeryWithDistance(**result.model_dump())
            for result in search_results
        ]
        
        # Generate response using LLM
        response_text = self.llm_service.generate_response(
            user_query=message,
            context_bakeries=bakery_responses
        )
        
        # Extract sources
        sources = [bakery.name for bakery in search_results]
        # Persist chat history (store user Q/A pair and metadata)
        try:
            chat_repo = ChatRepository(self.db)
            metadata_json = {
                "sources": sources,
                "bread_tags": bread_tags,
                "bakery_ids": [str(b.id) for b in search_results]
            }
            chat_repo.create_history(user_message=message, bot_response=response_text, metadata_json=metadata_json)
        except Exception:
            # Do not fail the chat if history persistence fails; just continue
            pass

        return ChatResponse(
            response=response_text,
            recommendations=search_results,
            sources_used=sources
        )
    
    def embedding_exists(self, bakery_id: str) -> bool:
        """Check if embedding exists for bakery"""
        return self.vector_repo.get_vector(bakery_id) is not None
