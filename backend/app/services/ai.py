from __future__ import annotations

from hashlib import sha256
from typing import Any

from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import AIRequest, AIPricing


class AIServiceError(RuntimeError):
    pass


def _calc_cost(prompt_tokens: int, completion_tokens: int, pricing: AIPricing | None) -> tuple[float, dict]:
    if pricing is None:
        return 0.0, {"prompt_per_1k": 0.0, "completion_per_1k": 0.0}
    prompt_cost = (prompt_tokens / 1000.0) * pricing.prompt_per_1k
    completion_cost = (completion_tokens / 1000.0) * pricing.completion_per_1k
    return round(prompt_cost + completion_cost, 8), {
        "prompt_per_1k": pricing.prompt_per_1k,
        "completion_per_1k": pricing.completion_per_1k,
    }


def analyze_incident(
    db: Session,
    *,
    user_id: int | None,
    incident_id: int,
    evidence: dict[str, Any],
    model: str = "gpt-4.1-mini",
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise AIServiceError("OPENAI_API_KEY not configured")

    prompt = (
        "You are an SRE assistant. Summarize incident evidence, list likely causes, "
        "and next investigation steps. Evidence:\n"
        f"{evidence}"
    )
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(model=model, input=prompt)

    output_text = response.output_text or ""
    usage = response.usage
    prompt_tokens = usage.input_tokens if usage else 0
    completion_tokens = usage.output_tokens if usage else 0
    total_tokens = prompt_tokens + completion_tokens

    pricing = db.scalar(select(AIPricing).where(AIPricing.model == model))
    total_cost, unit_costs = _calc_cost(prompt_tokens, completion_tokens, pricing)

    record = AIRequest(
        user_id=user_id,
        feature="incident_summary",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        total_cost=total_cost,
        unit_costs=unit_costs,
        input_hash=sha256(str(evidence).encode()).hexdigest(),
        output_ref=f"incident:{incident_id}",
    )
    db.add(record)
    db.commit()

    return {
        "summary": output_text,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": total_cost,
        },
    }
