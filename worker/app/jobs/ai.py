from celery import shared_task


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def analyze_incident(self, incident_id: int) -> dict:
    # Placeholder task. The API currently executes AI analysis synchronously.
    # This task can be switched on by posting incident snapshots to worker queues.
    return {"incident_id": incident_id, "status": "queued_for_analysis"}
