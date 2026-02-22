from typing import List, Dict
from app.config import get_settings

settings = get_settings()


class DocumentProcessor:
    """Handles text chunking for documents."""

    def __init__(self):
        self._splitter = None

    def _get_splitter(self):
        """Lazy load langchain splitter only when needed."""
        if self._splitter is None:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
        return self._splitter

    def chunk_document(self, pages: List[Dict]) -> List[Dict]:
        """Split document pages into smaller chunks for embedding."""
        chunks = []
        chunk_index = 0

        try:
            splitter = self._get_splitter()
        except ImportError:
            splitter = None

        for page in pages:
            if splitter:
                page_chunks = splitter.split_text(page["text"])
            else:
                text = page["text"]
                size = settings.CHUNK_SIZE
                overlap = settings.CHUNK_OVERLAP
                page_chunks = []
                start = 0
                while start < len(text):
                    page_chunks.append(text[start:start + size])
                    start += size - overlap

            for chunk_text in page_chunks:
                chunks.append({
                    "content": chunk_text,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index
                })
                chunk_index += 1

        return chunks