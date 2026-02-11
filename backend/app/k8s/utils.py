import json


def parse_kubeconfig(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("kubeconfig must be valid JSON for this scaffold") from exc
