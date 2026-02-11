from typing import Any

import httpx

from app.core.config import get_settings


def query_prometheus(path: str, params: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    url = f"{settings.prometheus_base_url.rstrip('/')}{path}"
    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()
    return response.json()
