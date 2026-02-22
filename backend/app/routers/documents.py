from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Document, DocumentChunk, QueryHistory
from app.schemas import DocumentResponse, DocumentListResponse
from app.auth import get_current_user
from app.utils.pdf_parser import extract_text_from_pdf, extract_text_from_txt
from app.config import get_settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])

ALLOWED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/x-pdf": "pdf",
    "text/plain": "txt",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _get_file_type(filename: str, content_type: str | None) -> str | None:
    """Resolve file type from content_type or filename."""
    if content_type and content_type in ALLOWED_FILE_TYPES:
        return ALLOWED_FILE_TYPES[content_type]
    if filename:
        lower = filename.lower()
        if lower.endswith(".pdf"):
            return "pdf"
        if lower.endswith(".txt"):
            return "txt"
    return None


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document."""
    file_type = _get_file_type(file.filename or "", file.content_type)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Use PDF or TXT. (got: {file.content_type or 'unknown'})"
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )

    settings = get_settings()
    provider = settings.AI_PROVIDER.lower()
    if provider == "openai" and (not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-your")):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY or use AI_PROVIDER=groq/gemini.",
        )
    if provider == "groq" and (not settings.GROQ_API_KEY or len(settings.GROQ_API_KEY) < 20):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Groq API key not configured. Get a FREE key at https://console.groq.com/keys and set GROQ_API_KEY.",
        )
    if provider == "gemini" and (not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-")):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key not configured. Get a FREE key at https://aistudio.google.com/apikey and set GEMINI_API_KEY.",
        )

    doc = Document(
        filename=file.filename or "document",
        file_type=file_type,
        file_size=len(content),
        owner_id=current_user.id,
        status="processing"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        if file_type == "pdf":
            pages = extract_text_from_pdf(content)
        else:
            pages = extract_text_from_txt(content)

        if not pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any text from the document"
            )

        from app.services.document_processor import DocumentProcessor
        from app.services.embedding_service import EmbeddingService

        processor = DocumentProcessor()
        chunks = processor.chunk_document(pages)

        embedding_service = EmbeddingService()
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(chunk_texts)

        for chunk, embedding in zip(chunks, embeddings):
            db_chunk = DocumentChunk(
                content=chunk["content"],
                chunk_index=chunk["chunk_index"],
                page_number=chunk["page_number"],
                embedding=str(embedding),
                document_id=doc.id
            )
            db.add(db_chunk)

        doc.total_chunks = len(chunks)
        doc.status = "ready"
        db.commit()
        db.refresh(doc)

    except Exception as e:
        import traceback
        traceback.print_exc()
        doc.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

    return doc


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all documents for the current user."""
    documents = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).order_by(Document.created_at.desc()).all()
    return DocumentListResponse(documents=documents, total=len(documents))


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document and its chunks."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Clear query_history references so we can delete the document
    db.query(QueryHistory).filter(QueryHistory.document_id == document_id).update(
        {"document_id": None}
    )
    db.delete(doc)
    db.commit()