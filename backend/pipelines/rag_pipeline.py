from sqlalchemy.orm import Session
from typing import Dict, Any

class RAGPipeline:
    def __init__(self, db: Session):
        self.db = db

    def ingest_policy(self, title: str, content: str, source: str = "Government Circular"):
        raise NotImplementedError(
            "RAG ingestion requires a configured embedding provider; mock embeddings are disabled."
        )

    def check_compliance(self, query: str) -> Dict[str, Any]:
        raise NotImplementedError(
            "RAG compliance checks require live embeddings/vector search; mock responses are disabled."
        )
