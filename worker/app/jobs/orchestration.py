from datetime import datetime

from celery import shared_task
from sqlalchemy import text

from app.db import engine


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def execute_resource_intent(self, intent_id: int, action: str = "apply") -> dict:
    started_at = datetime.utcnow()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO resource_runs (intent_id, action, started_at, result, retry_count)
                VALUES (:intent_id, :action, :started_at, 'running', :retry_count)
                """
            ),
            {
                "intent_id": intent_id,
                "action": action,
                "started_at": started_at,
                "retry_count": self.request.retries,
            },
        )

    # Placeholder for Kubernetes CR apply + readiness wait loop.
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE resource_intents
                SET status='applied'
                WHERE id=:intent_id
                """
            ),
            {"intent_id": intent_id},
        )

    return {"intent_id": intent_id, "status": "applied", "action": action}
