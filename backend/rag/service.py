import os
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from rag.context_builder import build_context_blob, build_prompt
from rag.llm_client import OllamaError, generate
from rag.router import route_question
from rag.structured import build_structured_context, infrastructure_gaps_summary
from rag.vector_store import ingest_document, retrieve_documents


class HybridRAGService:
    def __init__(self, db: Session, base_dir: Path):
        self.db = db
        self.base_dir = base_dir

    def ingest_policy(
        self,
        title: str,
        content: str,
        source: str = "Manual Upload",
        project_id: Optional[str] = None,
    ) -> int:
        return ingest_document(
            db=self.db,
            title=title,
            content=content,
            source=source,
            project_id=project_id,
        )

    def query(self, project_id: str, question: str) -> Dict[str, Any]:
        decision = route_question(question)
        resolved_model = self._resolve_model(decision.model)
        structured_context: Dict[str, Any] = {}
        docs = []

        if decision.use_structured:
            structured_context = build_structured_context(self.db, self.base_dir, project_id=project_id)
            if decision.intent == "infrastructure_gaps":
                structured_context["infrastructure_gaps"] = infrastructure_gaps_summary(structured_context)

        if decision.use_vector:
            docs = retrieve_documents(self.db, query=question, project_id=project_id, top_k=4)

        context_blob = build_context_blob(
            project_id=project_id,
            intent=decision.intent,
            structured_context=structured_context,
            retrieved_docs=docs,
        )
        prompt = build_prompt(question=question, context_blob=context_blob)
        answer: str
        try:
            answer = generate(prompt=prompt, model=resolved_model)
        except OllamaError as exc:
            answer = f"LLM unavailable: {exc}"

        return {
            "project_id": project_id,
            "intent": decision.intent,
            "model": resolved_model,
            "answer": answer,
            "analysis": {"justification": answer},
            "sources": {
                "structured": bool(structured_context),
                "documents": [
                    {"id": d.get("id"), "title": d.get("title"), "source": d.get("source"), "score": d.get("score")}
                    for d in docs
                ],
            },
        }

    @staticmethod
    def _resolve_model(logical_name: str) -> str:
        if logical_name == "qwen":
            return os.getenv("OLLAMA_MODEL_SUMMARY", "qwen")
        return os.getenv("OLLAMA_MODEL_REASONING", "deepseek")
