from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.celery_client import celery_app
from app.core.deps import get_current_user, get_db
from app.core.rbac import (
    enforce_namespace_access,
    ensure_any_permission,
    require_any_perm,
    require_perm,
    user_permission_set,
)
from app.db.models import ResourceIntent, ResourceRun, User
from app.db.schemas import ResourceRunOut
from app.services.orchestration import required_namespace_action, required_permission

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


@router.post(
    "/intents/{intent_id}/apply",
    response_model=ResourceRunOut,
    dependencies=[Depends(require_any_perm("k8s.write", "spark.deploy", "kafka.deploy"))],
)
def apply_intent(
    intent_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResourceRunOut:
    intent = db.scalar(select(ResourceIntent).where(ResourceIntent.id == intent_id))
    if intent is None:
        raise HTTPException(status_code=404, detail="Intent not found")

    perms = user_permission_set(db, user.id)
    ensure_any_permission(perms, (required_permission(intent.resource_type),))
    enforce_namespace_access(
        db,
        user,
        intent.cluster_id,
        intent.namespace,
        required_namespace_action(intent.resource_type),
    )

    run = ResourceRun(
        intent_id=intent.id,
        action="apply",
        started_at=datetime.now(UTC),
        result="queued",
        retry_count=0,
    )
    intent.status = "queued"
    db.add(run)
    db.commit()
    db.refresh(run)

    celery_app.send_task(
        "app.jobs.orchestration.execute_resource_intent",
        kwargs={"intent_id": intent.id, "action": "apply", "run_id": run.id},
    )

    append_audit(
        db,
        actor=user,
        action="orchestration.intent.apply",
        resource_kind="resource_intent",
        resource_id=str(intent.id),
        diff_json={"run_id": run.id, "resource_type": intent.resource_type},
        outcome="queued",
        request=request,
    )
    return ResourceRunOut.model_validate(run)


@router.get(
    "/intents/{intent_id}/runs",
    response_model=list[ResourceRunOut],
    dependencies=[Depends(require_perm("k8s.read"))],
)
def list_runs(
    intent_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ResourceRunOut]:
    intent = db.scalar(select(ResourceIntent).where(ResourceIntent.id == intent_id))
    if intent is None:
        raise HTTPException(status_code=404, detail="Intent not found")
    enforce_namespace_access(db, user, intent.cluster_id, intent.namespace, "k8s.read")

    rows = db.scalars(
        select(ResourceRun).where(ResourceRun.intent_id == intent_id).order_by(ResourceRun.id.desc())
    ).all()
    return [ResourceRunOut.model_validate(row) for row in rows]


@router.get(
    "/runs/{run_id}",
    response_model=ResourceRunOut,
    dependencies=[Depends(require_perm("k8s.read"))],
)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResourceRunOut:
    run = db.scalar(select(ResourceRun).where(ResourceRun.id == run_id))
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    intent = db.scalar(select(ResourceIntent).where(ResourceIntent.id == run.intent_id))
    if intent is not None:
        enforce_namespace_access(db, user, intent.cluster_id, intent.namespace, "k8s.read")

    return ResourceRunOut.model_validate(run)
