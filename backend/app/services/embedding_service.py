from typing import List
from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Handles text embedding - supports OpenAI, Google Gemini, or Groq (Llama 3.3)."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self._openai_client = None
        self._groq_client = None
        self._genai = None
        self._local_model = None

        if self.provider == "openai":
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                raise RuntimeError("OpenAI provider selected but openai package not installed")
        elif self.provider == "groq":
            # Groq embeddings return 404 - use local sentence-transformers (768 dims, no API)
            try:
                from sentence_transformers import SentenceTransformer
                self._local_model = SentenceTransformer("all-mpnet-base-v2")
            except ImportError:
                raise RuntimeError("Groq needs: pip install sentence-transformers")
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._genai = genai
            except ImportError:
                raise RuntimeError("Gemini provider selected but google-generativeai not installed")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if self.provider == "openai":
            response = self._openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        elif self.provider == "groq":
            return self._local_model.encode(text, convert_to_numpy=True).tolist()
        else:  # gemini - use gemini-embedding-001 (free tier)
            result = self._genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
            )
            return result["embedding"]

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if self.provider == "openai":
            response = self._openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
        elif self.provider == "groq":
            return self._local_model.encode(texts, convert_to_numpy=True).tolist()
        else:  # gemini - embed each text (free tier: 60 req/min)
            embeddings = []
            for text in texts:
                result = self._genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=text,
                )
                embeddings.append(result["embedding"])
            return embeddings
