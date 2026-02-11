from __future__ import annotations

import json
from datetime import datetime

import httpx
from celery import shared_task
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.jobs.notifications import send_email, send_slack, send_webhook


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def evaluate_alert_rules(self) -> dict:
    settings = get_settings()
    fired = 0

    with engine.begin() as conn:
        rules = conn.execute(
            text(
                """
                SELECT id, name, promql, threshold, severity, channels
                FROM alert_rules
                WHERE enabled = 1
                """
            )
        ).mappings().all()

    for rule in rules:
        try:
            response = httpx.get(
                f"{settings.prometheus_base_url.rstrip('/')}/api/v1/query",
                params={"query": rule["promql"]},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            value = 0.0
            data = payload.get("data", {}).get("result", [])
            if data:
                value = float(data[0]["value"][1])

            if value >= float(rule["threshold"]):
                fired += 1
                evidence = {
                    "rule": rule["name"],
                    "value": value,
                    "threshold": float(rule["threshold"]),
                    "prometheus": payload,
                    "captured_at": datetime.utcnow().isoformat(),
                }
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            INSERT INTO alert_firings (rule_id, value, evidence_json, fired_at)
                            VALUES (:rule_id, :value, :evidence, :fired_at)
                            """
                        ),
                        {
                            "rule_id": rule["id"],
                            "value": value,
                            "evidence": json.dumps(evidence),
                            "fired_at": datetime.utcnow(),
                        },
                    )
                    conn.execute(
                        text(
                            """
                            INSERT INTO incidents (rule_id, severity, state, evidence_json, created_at)
                            VALUES (:rule_id, :severity, 'open', :evidence, :created_at)
                            """
                        ),
                        {
                            "rule_id": rule["id"],
                            "severity": rule["severity"],
                            "evidence": json.dumps(evidence),
                            "created_at": datetime.utcnow(),
                        },
                    )

                channels = rule["channels"]
                if isinstance(channels, str):
                    try:
                        channels = json.loads(channels)
                    except json.JSONDecodeError:
                        channels = []
                send_webhook({"rule": rule["name"], "value": value, "severity": rule["severity"]})
                if "slack" in channels:
                    send_slack(f"Alert fired: {rule['name']} value={value}")
                if "email" in channels:
                    send_email(
                        subject=f"[Alert] {rule['name']}",
                        body=f"Rule {rule['name']} fired with value={value}",
                        to=[settings.smtp_user] if settings.smtp_user else [],
                    )
        except Exception:
            continue

    return {"fired": fired, "evaluated": len(rules)}
