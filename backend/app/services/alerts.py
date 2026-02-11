from datetime import datetime
from typing import Any


def build_incident_evidence(prom_result: dict[str, Any], rule_name: str) -> dict[str, Any]:
    return {
        "rule": rule_name,
        "result": prom_result,
        "captured_at": datetime.utcnow().isoformat(),
    }
