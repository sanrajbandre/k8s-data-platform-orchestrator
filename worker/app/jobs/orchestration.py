from datetime import datetime

from celery import shared_task
from sqlalchemy import text

from app.db import engine


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def execute_resource_intent(
    self,
    intent_id: int,
    action: str = "apply",
    run_id: int | None = None,
) -> dict:
    started_at = datetime.utcnow()
    with engine.begin() as conn:
        if run_id is None:
            created = conn.execute(
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
            run_id = int(created.lastrowid)
        else:
            conn.execute(
                text(
                    """
                    UPDATE resource_runs
                    SET action=:action, started_at=:started_at, result='running', retry_count=:retry_count
                    WHERE id=:run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "action": action,
                    "started_at": started_at,
                    "retry_count": self.request.retries,
                },
            )
        conn.execute(
            text("UPDATE resource_intents SET status='running' WHERE id=:intent_id"),
            {"intent_id": intent_id},
        )

    try:
        # Placeholder for Kubernetes CR apply + readiness wait loop.
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE resource_intents SET status='applied' WHERE id=:intent_id"),
                {"intent_id": intent_id},
            )
            conn.execute(
                text(
                    """
                    UPDATE resource_runs
                    SET ended_at=:ended_at, result='success', retry_count=:retry_count
                    WHERE id=:run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "ended_at": datetime.utcnow(),
                    "retry_count": self.request.retries,
                },
            )
    except Exception as exc:
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE resource_intents SET status='failed' WHERE id=:intent_id"),
                {"intent_id": intent_id},
            )
            conn.execute(
                text(
                    """
                    UPDATE resource_runs
                    SET ended_at=:ended_at, result='failed', logs_ref=:logs_ref, retry_count=:retry_count
                    WHERE id=:run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "ended_at": datetime.utcnow(),
                    "logs_ref": str(exc)[:255],
                    "retry_count": self.request.retries,
                },
            )
        raise

    return {"intent_id": intent_id, "run_id": run_id, "status": "applied", "action": action}
