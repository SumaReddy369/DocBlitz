import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer)
    upload_path = Column(String(500))
    total_chunks = Column(Integer, default=0)
    status = Column(String(50), default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer)
    embedding = Column(Text)
    metadata_ = Column("metadata", Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    document = relationship("Document", back_populates="chunks")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_chunks = Column(Text)
    confidence_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)