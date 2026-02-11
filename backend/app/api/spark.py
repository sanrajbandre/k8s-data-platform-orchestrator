from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.deps import get_current_user, get_db
from app.core.rbac import enforce_namespace_access, require_perm
from app.db.models import ObservedResource, ResourceIntent, User
from app.db.schemas import ResourceIntentCreate, ResourceIntentOut
from app.services.spark import build_spark_application_template

router = APIRouter(prefix="/services/spark", tags=["spark"])


@router.get("/templates", dependencies=[Depends(require_perm("spark.deploy"))])
def spark_templates() -> dict:
    return {
        "templates": [
            {"name": "batch-default", "image": "ghcr.io/spark:4.0.0", "dynamicAllocation": True},
            {
                "name": "streaming-default",
                "image": "ghcr.io/spark:4.0.0",
                "dynamicAllocation": False,
            },
        ]
    }


@router.post("/applications", response_model=ResourceIntentOut, dependencies=[Depends(require_perm("spark.deploy"))])
def create_spark_app(
    payload: ResourceIntentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResourceIntentOut:
    enforce_namespace_access(db, user, payload.cluster_id, payload.namespace, "spark.deploy")

    spec = build_spark_application_template(
        name=payload.spec_json.get("name", "spark-app"),
        namespace=payload.namespace,
        spec=payload.spec_json,
    )

    intent = ResourceIntent(
        resource_type="sparkapplication",
        mode="operator",
        cluster_id=payload.cluster_id,
        namespace=payload.namespace,
        spec_json=spec,
        created_by=user.id,
        status="pending",
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)

    append_audit(
        db,
        actor=user,
        action="spark.intent.create",
        resource_kind="sparkapplication",
        resource_id=str(intent.id),
        diff_json={"cluster_id": intent.cluster_id, "namespace": intent.namespace},
        outcome="success",
        request=request,
    )
    return ResourceIntentOut.model_validate(intent)


@router.get("/applications", response_model=list[ResourceIntentOut], dependencies=[Depends(require_perm("spark.deploy"))])
def list_spark_apps(db: Session = Depends(get_db)) -> list[ResourceIntentOut]:
    rows = db.scalars(
        select(ResourceIntent).where(ResourceIntent.resource_type == "sparkapplication").order_by(ResourceIntent.id.desc())
    ).all()
    return [ResourceIntentOut.model_validate(r) for r in rows]


@router.get("/applications/{intent_id}", response_model=ResourceIntentOut, dependencies=[Depends(require_perm("spark.deploy"))])
def get_spark_app(intent_id: int, db: Session = Depends(get_db)) -> ResourceIntentOut:
    item = db.scalar(select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "sparkapplication"))
    if not item:
        raise HTTPException(status_code=404, detail="Spark intent not found")
    return ResourceIntentOut.model_validate(item)


@router.put(
    "/applications/{intent_id}",
    response_model=ResourceIntentOut,
    dependencies=[Depends(require_perm("spark.deploy"))],
)
def update_spark_app(
    intent_id: int,
    payload: ResourceIntentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResourceIntentOut:
    intent = db.scalar(
        select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "sparkapplication")
    )
    if not intent:
        raise HTTPException(status_code=404, detail="Spark intent not found")

    enforce_namespace_access(db, user, payload.cluster_id, payload.namespace, "spark.deploy")
    intent.cluster_id = payload.cluster_id
    intent.namespace = payload.namespace
    intent.spec_json = build_spark_application_template(
        name=payload.spec_json.get("name", "spark-app"),
        namespace=payload.namespace,
        spec=payload.spec_json,
    )
    intent.status = "pending"
    db.commit()
    db.refresh(intent)

    append_audit(
        db,
        actor=user,
        action="spark.intent.update",
        resource_kind="sparkapplication",
        resource_id=str(intent.id),
        diff_json={"cluster_id": intent.cluster_id, "namespace": intent.namespace},
        outcome="success",
        request=request,
    )
    return ResourceIntentOut.model_validate(intent)


@router.delete("/applications/{intent_id}", dependencies=[Depends(require_perm("spark.deploy"))])
def delete_spark_app(
    intent_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    intent = db.scalar(
        select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "sparkapplication")
    )
    if not intent:
        raise HTTPException(status_code=404, detail="Spark intent not found")

    db.delete(intent)
    db.commit()
    append_audit(
        db,
        actor=user,
        action="spark.intent.delete",
        resource_kind="sparkapplication",
        resource_id=str(intent_id),
        diff_json={},
        outcome="success",
        request=request,
    )
    return {"status": "deleted"}


@router.get("/applications/{intent_id}/status", dependencies=[Depends(require_perm("spark.deploy"))])
def spark_status(intent_id: int, db: Session = Depends(get_db)) -> dict:
    intent = db.scalar(
        select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "sparkapplication")
    )
    if not intent:
        raise HTTPException(status_code=404, detail="Spark intent not found")

    observed = db.scalar(
        select(ObservedResource).where(
            ObservedResource.cluster_id == intent.cluster_id,
            ObservedResource.namespace == intent.namespace,
            ObservedResource.resource_type == "sparkapplication",
            ObservedResource.resource_name == intent.spec_json.get("metadata", {}).get("name", "spark-app"),
        )
    )
    return {
        "intent_status": intent.status,
        "observed_status": observed.observed_json if observed else None,
    }
