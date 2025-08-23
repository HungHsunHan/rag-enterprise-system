from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../.env",  # Read from root directory
        env_ignore_empty=True,
        extra="ignore"
    )
    
    # API Settings
    PROJECT_NAME: str = "HR Internal Q&A System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT token signing"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/hr_chatbot",
        description="PostgreSQL database URL"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="List of allowed CORS origins"
    )
    
    # LLM API Configuration
    OPENROUTER_API_KEY: str = Field(
        default="",
        description="OpenRouter API key for LLM integration"
    )
    LLM_MODEL: str = Field(
        default="microsoft/phi-3-mini-128k-instruct:free",
        description="LLM model to use through OpenRouter"
    )
    
    # Embedding Model
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/paraphrase-MiniLM-L3-v2",
        description="Free sentence transformer model for embeddings"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=384,
        description="Dimension of embedding vectors"
    )
    
    # File Processing
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size for uploads in bytes"
    )
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".pdf", ".docx", ".txt"],
        description="Allowed file types for upload"
    )
    
    # Chunk Processing
    CHUNK_SIZE: int = Field(
        default=1000,
        description="Size of text chunks for processing"
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        description="Overlap between chunks"
    )
    
    @computed_field
    @property
    def is_cors_enabled(self) -> bool:
        return len(self.BACKEND_CORS_ORIGINS) > 0


settings = Settings()