from typing import List, Optional, Dict, Any
from pinecone import Pinecone
from app.config.settings import settings


class VectorRepository:
    """Repository for Vector DB (Pinecone) operations"""
    
    def __init__(self):
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.pc.Index(settings.pinecone_index)
    
    def upsert_vector(
        self,
        bakery_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """Upsert (insert or update) a vector to Pinecone"""
        self.index.upsert(
            vectors=[
                (bakery_id, embedding, metadata)
            ]
        )
    
    def upsert_vectors(
        self,
        vectors: List[tuple]
    ) -> None:
        """Upsert multiple vectors to Pinecone
        
        Args:
            vectors: List of (id, embedding, metadata) tuples
        """
        self.index.upsert(vectors=vectors)
    
    def query(
        self,
        embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query similar vectors from Pinecone
        
        Args:
            embedding: Query embedding vector
            top_k: Number of top results to return
            filters: Optional metadata filters
            
        Returns:
            List of results with scores and metadata
        """
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filters
        )
        
        return [
            {
                "bakery_id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]
    
    def get_vector(self, bakery_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID"""
        result = self.index.fetch(ids=[bakery_id])
        if result and result.vectors:
            vector_data = result.vectors.get(bakery_id)
            if vector_data:
                return {
                    "id": bakery_id,
                    "values": vector_data.values,
                    "metadata": vector_data.metadata
                }
        return None
    
    def delete_vector(self, bakery_id: str) -> None:
        """Delete a vector by ID"""
        self.index.delete(ids=[bakery_id])
    
    def delete_vectors(self, bakery_ids: List[str]) -> None:
        """Delete multiple vectors by IDs"""
        self.index.delete(ids=bakery_ids)
    
    def update_metadata(
        self,
        bakery_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update metadata for a vector"""
        self.index.update(id=bakery_id, set_metadata=metadata)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return self.index.describe_index_stats()
