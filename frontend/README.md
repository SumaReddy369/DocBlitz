# AI Document Q&A Platform (RAG)

A full-stack document intelligence platform that enables users to upload PDF/TXT documents and ask natural language questions. Built with a **Retrieval-Augmented Generation (RAG)** pipeline that extracts, chunks, embeds, and retrieves document context to generate accurate AI-powered answers.

## Architecture

```
┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Upload  │───▶│  Extract  │───▶│  Chunk   │───▶│  Embed   │───▶│  Store   │
│  PDF/TXT │    │   Text    │    │  Text    │    │ (OpenAI) │    │ pgvector │
└──────────┘    └───────────┘    └──────────┘    └──────────┘    └──────────┘

┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │───▶│  Embed    │───▶│  Vector  │───▶│ Retrieve │───▶│  LLM     │
│ Question │    │  Query    │    │  Search  │    │ Top-K    │    │ Answer   │
└──────────┘    └───────────┘    └──────────┘    └──────────┘    └──────────┘
```

## Tech Stack

| Layer        | Technology                                    |
|-------------|-----------------------------------------------|
| Backend     | Python 3.11, FastAPI, SQLAlchemy               |
| AI/LLM      | OpenAI GPT-4o-mini, text-embedding-3-small    |
| Vector DB   | PostgreSQL 16 + pgvector                       |
| Frontend    | Next.js 15, TypeScript, Tailwind CSS           |
| Auth        | JWT with OAuth2 Password Flow                  |
| DevOps      | Docker, Docker Compose, GitHub Actions CI/CD   |

## Features

- **Document Upload & Processing** — Upload PDF or TXT files with automatic text extraction, chunking, and embedding generation
- **Semantic Search** — Vector similarity search using pgvector with cosine distance
- **RAG Pipeline** — Context-aware answers grounded in document content with source citations
- **Authentication** — Secure JWT-based user authentication
- **Query History** — Track all questions and answers per user
- **Responsive UI** — Dark-themed chat interface with drag-and-drop file upload

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints (auth, documents, query)
│   │   ├── services/         # Business logic (RAG, embeddings, vector store)
│   │   ├── utils/            # PDF parsing utilities
│   │   ├── auth.py           # JWT authentication
│   │   ├── config.py         # Environment configuration
│   │   ├── database.py       # Database connection
│   │   ├── models.py         # SQLAlchemy ORM models
│   │   └── schemas.py        # Pydantic validation schemas
│   └── tests/                # Unit tests
├── frontend/
│   └── src/
│       ├── app/              # Next.js app router pages
│       ├── components/       # React components (Chat, Upload, etc.)
│       └── lib/              # API client
└── docker-compose.yml        # Multi-container orchestration
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key ([get one here](https://platform.openai.com/api-keys))

### Setup

```bash
git clone https://github.com/SumaReddy369/ai-doc-qa-platform.git
cd ai-doc-qa-platform

# Create backend/.env with your OpenAI key
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY

# Start all services
docker-compose up --build
```

### Access

| Service      | URL                          |
|-------------|------------------------------|
| Frontend    | http://localhost:3000         |
| Backend API | http://localhost:8000         |
| API Docs    | http://localhost:8000/docs    |

## API Endpoints

| Method | Endpoint                 | Description              | Auth |
|--------|--------------------------|--------------------------|------|
| POST   | `/api/auth/register`     | Register new user        | No   |
| POST   | `/api/auth/login`        | Login & get JWT token    | No   |
| GET    | `/api/auth/me`           | Get current user profile | Yes  |
| POST   | `/api/documents/upload`  | Upload & process document| Yes  |
| GET    | `/api/documents/`        | List user's documents    | Yes  |
| GET    | `/api/documents/{id}`    | Get document details     | Yes  |
| DELETE | `/api/documents/{id}`    | Delete a document        | Yes  |
| POST   | `/api/query/`            | Ask a question (RAG)     | Yes  |
| GET    | `/api/query/history`     | Get query history        | Yes  |

## How the RAG Pipeline Works

1. **Document Ingestion** — PDF/TXT files are uploaded, text is extracted using `pypdf`
2. **Chunking** — Text is split into overlapping chunks (1000 chars, 200 overlap) using recursive character splitting
3. **Embedding** — Each chunk is embedded using OpenAI's `text-embedding-3-small` model (1536 dimensions)
4. **Storage** — Chunks and embeddings are stored in PostgreSQL with pgvector extension
5. **Query** — User questions are embedded and compared against stored chunks using cosine similarity
6. **Generation** — Top-K relevant chunks are passed as context to GPT-4o-mini, which generates a cited answer

## Design Decisions

- **pgvector over Pinecone/Weaviate** — Keeps everything in a single PostgreSQL instance, reducing infrastructure complexity and cost
- **Recursive Character Splitting** — Preserves semantic coherence better than fixed-size splitting
- **text-embedding-3-small** — Balances cost and quality for document retrieval
- **Synchronous Processing** — Simplified architecture for document upload; production version would use Celery + Redis for async processing

## Running Tests

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate
pip install -r requirements.txt
pytest tests/ -v
```

## Future Improvements

- [ ] Async document processing with Celery + Redis
- [ ] Support for DOCX, Markdown, and HTML files
- [ ] Streaming responses using Server-Sent Events
- [ ] Multi-document cross-referencing in answers
- [ ] Document access sharing between users
- [ ] Rate limiting and usage tracking