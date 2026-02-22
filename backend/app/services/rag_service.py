from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

settings = get_settings()


class RAGService:
    """Retrieval-Augmented Generation - supports OpenAI, Google Gemini, or Groq (Llama 3.3)."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

        self._openai_client = None
        self._groq_client = None
        self._gemini_model = None
        if self.provider == "openai":
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.provider == "groq":
            from groq import Groq
            self._groq_client = Groq(api_key=settings.GROQ_API_KEY.strip())
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._gemini_model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)

    def _build_context(self, chunks: List[Dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            page_info = f" (Page {chunk['page_number']})" if chunk.get('page_number') else ""
            context_parts.append(f"[Source {i}{page_info}]:\n{chunk['content']}")
        return "\n\n---\n\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        return f"""You are an intelligent document assistant. Answer based ONLY on the provided context.

Rules:
1. Answer based ONLY on the context. Do not make up information.
2. If the context doesn't contain enough information, say so clearly.
3. Cite sources using [Source X] notation.
4. Be concise but thorough. Use markdown for readability.

Context from documents:
{context}

---

Question: {question}

Provide a detailed answer based on the context above. Cite sources using [Source X] notation."""

    def query(
        self,
        db: Session,
        question: str,
        document_id: Optional[str] = None,
        top_k: int = 5,
        owner_id: Optional[str] = None
    ) -> Dict:
        query_embedding = self.embedding_service.generate_embedding(question)

        relevant_chunks = self.vector_store.similarity_search(
            db=db,
            query_embedding=query_embedding,
            top_k=top_k,
            document_id=document_id,
            owner_id=owner_id
        )

        if not relevant_chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents.",
                "sources": [],
                "confidence_score": 0
            }

        context = self._build_context(relevant_chunks)
        prompt = self._build_prompt(question, context)

        if self.provider == "openai":
            response = self._openai_client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a document Q&A assistant. Answer based only on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            answer = response.choices[0].message.content
        elif self.provider == "groq":
            response = self._groq_client.chat.completions.create(
                model=settings.GROQ_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a document Q&A assistant. Answer based only on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            answer = response.choices[0].message.content
        else:  # gemini - use google-generativeai (stable)
            response = self._gemini_model.generate_content(prompt)
            answer = response.text if response.text else "I couldn't generate an answer."

        avg_similarity = sum(c["similarity_score"] for c in relevant_chunks) / len(relevant_chunks)
        confidence = min(int(avg_similarity * 100), 100)

        return {
            "answer": answer,
            "sources": relevant_chunks,
            "confidence_score": confidence
        }
