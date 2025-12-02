from typing import List
from openai import OpenAI
from app.config.settings import settings


class EmbeddingService:
    """Service for generating embeddings using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        # Sort by index to maintain order
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]
    
    def embed_bakery_content(self, bakery_data: dict) -> List[float]:
        """Generate embedding for bakery content
        
        Args:
            bakery_data: Dict with name, ai_summary, category, etc.
            
        Returns:
            Embedding vector
        """
        # Combine all relevant information for embedding
        content_parts = [
            bakery_data.get("name", ""),
            bakery_data.get("ai_summary", ""),
            bakery_data.get("category", ""),
            bakery_data.get("address", ""),
        ]
        
        content = " ".join([part for part in content_parts if part])
        return self.embed_text(content)
