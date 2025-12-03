from typing import List, Optional
from openai import OpenAI
from app.config.settings import settings
from app.schemas import BakeryResponse


class LLMService:
    """Service for LLM interactions (RAG)"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
        self.system_prompt = """당신은 수원 빵집 투어의 전문 가이드 AI입니다.
사용자의 질문에 대해 다음 가이드라인을 따르세요:

1. 사용자의 요구사항을 정확히 파악하세요 (분위기, 맛, 방문 목적 등)
2. 추천하는 빵집이 왜 좋은지 설명하세요
3. 친절하고 자연스러운 톤으로 답변하세요
4. 구체적인 정보 (주소, 특징)를 포함하세요

추천 빵집 정보가 주어질 때, 이를 활용하여 최적의 답변을 만드세요."""
    
    def generate_response(
        self,
        user_query: str,
        context_bakeries: List[BakeryResponse],
        temperature: float = 0.7
    ) -> str:
        """Generate RAG response using LLM
        
        Args:
            user_query: User's question
            context_bakeries: Retrieved bakeries from vector DB
            temperature: LLM temperature (0.0-2.0)
            
        Returns:
            Generated response string
        """
        # Format context
        context_text = self._format_context(context_bakeries)
        
        user_message = f"""다음은 사용자의 질문과 검색된 빵집 정보입니다.

【사용자 질문】
{user_query}

【검색된 빵집 정보】
{context_text}

이 정보를 바탕으로 사용자의 질문에 답변해주세요."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _format_context(self, bakeries: List[BakeryResponse]) -> str:
        """Format bakery information for context"""
        context_parts = []
        
        for i, bakery in enumerate(bakeries, 1):
            bakery_info = f"""
빵집 {i}. {bakery.name}
- 주소: {bakery.address}
- 위치: {bakery.district}
- 특징: {bakery.ai_summary if bakery.ai_summary else '정보 없음'}
"""
            context_parts.append(bakery_info)
        
        return "\n".join(context_parts)
    
    def generate_title_for_query(self, query: str) -> str:
        """Generate a short title for a query"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"다음 질문을 한 문장으로 요약해주세요: {query}"}
            ],
            max_tokens=50,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
