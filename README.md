# 🤖 AI Document Q&A Platform (RAG)

An AI-powered document Q&A platform that lets users upload documents (PDF/TXT) and ask questions in natural language. Built with **Retrieval-Augmented Generation (RAG)** using OpenAI, FastAPI, PostgreSQL + pgvector, and Next.js.

## 🏗️ Architecture

User uploads PDF → Text Extraction → Chunking → Embedding (OpenAI) → Store in pgvector
User asks question → Embed question → Vector similarity search → Retrieve top chunks → LLM generates answer


## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI |
| **AI/LLM** | OpenAI GPT-4o-mini, text-embedding-3-small |
| **Vector DB** | PostgreSQL + pgvector |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **Auth** | JWT (OAuth2 Password Flow) |
| **DevOps** | Docker, Docker Compose, GitHub Actions CI/CD |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key

### Run the app

# Clone the repo
git clone https://github.com/yourusername/ai-doc-qa-platform.git
cd ai-doc-qa-platform

# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Start everything
docker-compose up --build

- **Backend API**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login & get JWT token |
| POST | `/api/documents/upload` | Upload a document |
| GET | `/api/documents/` | List all documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| POST | `/api/query/` | Ask a question (RAG) |
| GET | `/api/query/history` | Get query history |

## 🧪 Running Tests

cd backend
pip install -r requirements.txt
pytest tests/ -v

## 📐 Design Decisions

1. **pgvector over Pinecone/Weaviate**: Chose pgvector to keep everything in PostgreSQL - simpler infrastructure, no external vector DB costs.
2. **Chunking Strategy**: Recursive character splitting with 1000-char chunks and 200-char overlap for context preservation.
3. **Embedding Model**: text-embedding-3-small for cost efficiency while maintaining quality.
4. **Sync Processing**: Documents are processed synchronously on upload for simplicity. For production, this would use a task queue (Celery/Redis).

## 🚀 Deployment (Public Access)

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for step-by-step instructions to deploy so anyone can access your app via a link (Railway, Vercel, Render, or VPS).
