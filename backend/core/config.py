from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/compliance_db"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    nvidia_api_key: str = ""
    qdrant_collection: str = "regulations_v1"
    enable_whatsapp: bool = True
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # LLM
    gemini_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    llm_model: str = "gemini-2.0-flash" 
    llm_provider: str = "gemini"  # "gemini" or "groq"
    hf_token: str = ""
    
    # App
    secret_key: str = "your-secret-key-change-in-production"
    environment: str = "development"
    allowed_origins: str | list[str] = ""

    # Clerk Authentication
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""
    clerk_audience: str = ""  # optional — set to match the `azp` claim if needed

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: any) -> list[str]:
        if isinstance(v, str):
            if not v:
                return []
            if v.startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [i.strip() for i in v.split(",")]
        return v
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Cache the settings object to avoid reloading from environment each time"""
    return Settings()


settings = get_settings()