import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, QueryHistory
from app.schemas import QueryRequest, QueryResponse, QueryHistoryResponse, SourceChunk
from app.auth import get_current_user
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
def ask_question(
    query: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ask a question about uploaded documents."""
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        rag_service = RAGService()
        result = rag_service.query(
            db=db,
            question=query.question,
            document_id=query.document_id,
            top_k=query.top_k,
            owner_id=current_user.id
        )
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
            logger.warning("API rate limit / quota exceeded: %s", e)
            raise HTTPException(
                status_code=429,
                detail="API rate limit or quota exceeded. Please wait 1–2 minutes and try again.",
            )
        if "connection" in err_str or "apiconnectionerror" in err_str:
            logger.warning("AI API connection failed: %s", e)
            raise HTTPException(
                status_code=503,
                detail="Cannot reach Groq API. Check GROQ_API_KEY (no spaces), network, and firewall.",
            )
        logger.exception("Query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    history = QueryHistory(
        question=query.question,
        answer=result["answer"],
        source_chunks=json.dumps([s["id"] for s in result["sources"]]),
        confidence_score=result["confidence_score"],
        user_id=current_user.id,
        document_id=query.document_id
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    sources = [
        SourceChunk(
            content=s["content"],
            page_number=s.get("page_number"),
            chunk_index=s["chunk_index"],
            similarity_score=s["similarity_score"]
        )
        for s in result["sources"]
    ]

    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        query_id=history.id,
        confidence_score=result["confidence_score"]
    )


@router.get("/history", response_model=List[QueryHistoryResponse])
def get_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get query history for the current user."""
    history = db.query(QueryHistory).filter(
        QueryHistory.user_id == current_user.id
    ).order_by(QueryHistory.created_at.desc()).limit(50).all()
    return history