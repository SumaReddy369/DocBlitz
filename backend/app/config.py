import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI Document Q&A Platform"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/docqa")
    # AI Provider: "groq" (free), "gemini" (free), or "openai"
    AI_PROVIDER: str = "groq"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = ""

    @field_validator("GROQ_API_KEY", mode="before")
    @classmethod
    def clean_groq_key(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().replace(" ", "")
        return v or ""
    # Gemini chat model: gemini-1.5-flash (stable, free)
    GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-1.5-flash")
    # Groq chat model: llama-3.3-70b-versatile (Llama 3.3)
    GROQ_CHAT_MODEL: str = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
    # Groq embedding model (Groq uses nomic-embed-text-v1_5)
    GROQ_EMBEDDING_MODEL: str = "nomic-embed-text-v1_5"

    @field_validator("GROQ_EMBEDDING_MODEL", mode="before")
    @classmethod
    def normalize_embed_model(cls, v: str) -> str:
        if isinstance(v, str) and "v1.5" in v:
            return "nomic-embed-text-v1_5"  # Groq uses underscore
        return v or "nomic-embed-text-v1_5"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o-mini"


@lru_cache()
def get_settings():
    return Settings()