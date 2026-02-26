import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict


class OllamaError(RuntimeError):
    pass


def _post_json(url: str, payload: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise OllamaError(f"Ollama request failed: {exc}") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise OllamaError("Ollama returned non-JSON response") from exc


def generate(prompt: str, model: str = "deepseek", ollama_url: str | None = None) -> str:
    base = (ollama_url or os.getenv("OLLAMA_URL") or "http://localhost:11434").rstrip("/")
    payload = {"model": model, "prompt": prompt, "stream": False}
    out = _post_json(f"{base}/api/generate", payload=payload, timeout=180)
    response = out.get("response")
    if not isinstance(response, str):
        raise OllamaError("Ollama response missing 'response' field")
    return response

