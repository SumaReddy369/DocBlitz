from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: Optional[int] = None
    total_chunks: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class QueryRequest(BaseModel):
    question: str
    document_id: Optional[str] = None
    top_k: int = 5


class SourceChunk(BaseModel):
    content: str
    page_number: Optional[int] = None
    chunk_index: int
    similarity_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    query_id: str
    confidence_score: Optional[int] = None


class QueryHistoryResponse(BaseModel):
    id: str
    question: str
    answer: str
    created_at: datetime

    model_config = {"from_attributes": True}