import json
from typing import Any, Dict, List


SYSTEM_PROMPT = (
    "You are an infrastructure planning assistant for smart villages. "
    "Use ONLY the provided context. "
    'If data is missing, say exactly "Insufficient project data".'
)


def build_context_blob(
    project_id: str,
    intent: str,
    structured_context: Dict[str, Any],
    retrieved_docs: List[Dict[str, Any]],
) -> str:
    docs = [
        {
            "title": d.get("title"),
            "source": d.get("source"),
            "score": d.get("score"),
            "content": d.get("content"),
        }
        for d in retrieved_docs
    ]
    payload = {
        "project_id": project_id,
        "intent": intent,
        "structured": structured_context,
        "documents": docs,
    }
    return json.dumps(payload, indent=2)


def build_prompt(question: str, context_blob: str) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Project Context:\n{context_blob}\n\n"
        f"User Question:\n{question}\n\n"
        "Answer with concise, factual output. Include assumptions explicitly."
    )

