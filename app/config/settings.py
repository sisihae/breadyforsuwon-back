from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/breadyforsuwon"
    
    # Vector DB
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east1-aws"
    pinecone_index: str = "bakeries"
    
    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # App Config
    debug: bool = True
    app_name: str = "BreadyForSuwon"
    api_v1_prefix: str = "/api/v1"
    
    # JWT / Auth
    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_exp_seconds: int = 60 * 60 * 24 * 7  # 7 days
    session_cookie_name: str = "session"

    # Kakao OAuth
    kakao_client_id: str = ""
    kakao_client_secret: str = ""
    kakao_redirect_uri: str = "http://localhost:3000/auth/kakao/callback"
    frontend_url: str = "http://localhost:3000"
    
    # Embedding Settings
    embedding_dimension: int = 1536  # text-embedding-3-large
    top_k_results: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
