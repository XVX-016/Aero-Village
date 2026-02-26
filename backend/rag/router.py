from dataclasses import dataclass


@dataclass
class RouteDecision:
    intent: str
    use_structured: bool
    use_vector: bool
    model: str


def route_question(question: str) -> RouteDecision:
    q = (question or "").strip().lower()

    if any(k in q for k in ["how many building", "building count", "total building", "buildings in project"]):
        return RouteDecision(intent="building_count", use_structured=True, use_vector=False, model="deepseek")

    if any(k in q for k in ["transformer", "transformer count", "electrical cluster"]):
        return RouteDecision(intent="transformer_count", use_structured=True, use_vector=False, model="deepseek")

    if any(k in q for k in ["sewage", "extend sewage", "sector", "drainage route"]):
        return RouteDecision(intent="sewage_planning", use_structured=True, use_vector=True, model="deepseek")

    if any(k in q for k in ["gap", "infrastructure gap", "missing infra", "shortfall"]):
        return RouteDecision(intent="infrastructure_gaps", use_structured=True, use_vector=True, model="deepseek")

    if any(k in q for k in ["proposal", "report", "summarize", "summary"]):
        return RouteDecision(intent="report_generation", use_structured=True, use_vector=True, model="qwen")

    return RouteDecision(intent="general", use_structured=True, use_vector=True, model="deepseek")

