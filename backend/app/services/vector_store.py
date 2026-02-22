from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text


class VectorStoreService:
    """Handles vector similarity search using pgvector."""

    def similarity_search(
        self,
        db: Session,
        query_embedding: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
        owner_id: Optional[str] = None
    ) -> List[Dict]:
        """Find the most similar document chunks. Filters by owner when document_id is None."""
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        if document_id:
            sql = sql_text("""
                SELECT
                    dc.id, dc.content, dc.page_number, dc.chunk_index, dc.document_id,
                    1 - (dc.embedding::vector <=> CAST(:embedding AS vector)) as similarity_score
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE dc.document_id = :doc_id AND d.owner_id = :owner_id
                ORDER BY dc.embedding::vector <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """)
            results = db.execute(sql, {
                "embedding": embedding_str,
                "doc_id": document_id,
                "owner_id": owner_id or "",
                "top_k": top_k
            }).fetchall()
        else:
            sql = sql_text("""
                SELECT
                    dc.id, dc.content, dc.page_number, dc.chunk_index, dc.document_id,
                    1 - (dc.embedding::vector <=> CAST(:embedding AS vector)) as similarity_score
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.owner_id = :owner_id
                ORDER BY dc.embedding::vector <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """)
            results = db.execute(sql, {
                "embedding": embedding_str,
                "owner_id": owner_id or "",
                "top_k": top_k
            }).fetchall()

        return [
            {
                "id": str(row[0]),
                "content": row[1],
                "page_number": row[2],
                "chunk_index": row[3],
                "document_id": str(row[4]),
                "similarity_score": float(row[5])
            }
            for row in results
        ]