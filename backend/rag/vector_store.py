from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models import RAGDocument


def _score_overlap(query: str, content: str) -> int:
    q_tokens = {t for t in (query or "").lower().split() if len(t) > 2}
    c_tokens = {t for t in (content or "").lower().split()}
    return len(q_tokens.intersection(c_tokens))


def ingest_document(
    db: Session,
    title: str,
    content: str,
    source: str = "Manual Upload",
    project_id: Optional[str] = None,
    chunk_size: int = 1200,
) -> int:
    text = (content or "").strip()
    if not text:
        return 0

    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    rows: List[RAGDocument] = []
    for idx, chunk in enumerate(chunks):
        meta: Dict[str, Any] = {"chunk_index": idx, "project_id": project_id}
        rows.append(
            RAGDocument(
                title=title,
                source=source,
                content=chunk,
                extra_metadata=meta,
            )
        )
    db.bulk_save_objects(rows)
    db.commit()
    return len(rows)


def retrieve_documents(db: Session, query: str, project_id: Optional[str], top_k: int = 4) -> List[Dict[str, Any]]:
    rows = db.query(RAGDocument).all()
    candidates: List[Dict[str, Any]] = []
    for row in rows:
        meta = row.extra_metadata or {}
        row_project = meta.get("project_id")
        if project_id and row_project not in (None, "", project_id):
            continue
        score = _score_overlap(query=query, content=row.content or "")
        if score <= 0:
            continue
        candidates.append(
            {
                "id": str(row.id),
                "title": row.title,
                "source": row.source,
                "content": row.content,
                "score": score,
            }
        )
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]

