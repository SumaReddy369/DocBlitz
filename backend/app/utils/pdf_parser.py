from typing import List, Dict
import io

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


def extract_text_from_pdf(file_content: bytes) -> List[Dict]:
    """Extract text from PDF file, returning text per page."""
    if PdfReader is None:
        raise ImportError("pypdf is not installed")

    reader = PdfReader(io.BytesIO(file_content))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "page_number": i + 1,
                "text": text.strip()
            })

    return pages


def extract_text_from_txt(file_content: bytes) -> List[Dict]:
    """Extract text from a plain text file."""
    text = file_content.decode("utf-8", errors="replace").strip()
    if not text:
        return []
    return [{"page_number": 1, "text": text}]