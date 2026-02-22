import os
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.routers import auth, documents, query
from app.database import engine, Base
from app import models  # noqa: F401 - registers models with Base

settings = get_settings()

# CORS: Add your deployment URL to CORS_ORIGINS env (comma-separated)
_cors_origins = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]
if extra := os.getenv("CORS_ORIGINS", ""):
    _cors_origins.extend(o.strip() for o in extra.split(",") if o.strip())

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered document Q&A platform using RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.on_event("startup")
def startup_event():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "AI Document Q&A Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Capture unhandled exceptions (not HTTPException) and return details."""
    if isinstance(exc, HTTPException):
        raise exc
    tb = traceback.format_exc()
    print(f"Unhandled error: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )