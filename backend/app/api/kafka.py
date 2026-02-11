from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.deps import get_current_user, get_db
from app.core.rbac import enforce_namespace_access, require_perm
from app.db.models import ObservedResource, ResourceIntent, User
from app.db.schemas import KafkaIntentCreate, ResourceIntentOut
from app.services.kafka import KafkaValidationError, migration_precheck_report, validate_kafka_mode

router = APIRouter(prefix="/services/kafka", tags=["kafka"])


@router.get("/templates", dependencies=[Depends(require_perm("kafka.deploy"))])
def kafka_templates() -> dict:
    return {
        "templates": [
            {
                "name": "kraft-default",
                "kafka_mode": "kraft",
                "kafka_version": "4.0.0",
                "strimzi_version": "0.46.0",
            },
            {
                "name": "legacy-zk",
                "kafka_mode": "legacy_zookeeper",
                "kafka_version": "3.8.1",
                "strimzi_version": "0.45.1",
                "legacy": True,
            },
        ]
    }


@router.post("/clusters", response_model=ResourceIntentOut, dependencies=[Depends(require_perm("kafka.deploy"))])
def create_kafka_cluster(
    payload: KafkaIntentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResourceIntentOut:
    enforce_namespace_access(db, user, payload.cluster_id, payload.namespace, "kafka.deploy")

    try:
        validate_kafka_mode(payload.kafka_mode, payload.kafka_version, payload.strimzi_version)
    except KafkaValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    intent = ResourceIntent(
        resource_type="kafka",
        mode=payload.kafka_mode,
        cluster_id=payload.cluster_id,
        namespace=payload.namespace,
        spec_json={
            **payload.spec_json,
            "kafka_version": payload.kafka_version,
            "strimzi_version": payload.strimzi_version,
            "kafka_mode": payload.kafka_mode,
        },
        created_by=user.id,
        status="pending",
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)

    append_audit(
        db,
        actor=user,
        action="kafka.intent.create",
        resource_kind="kafka",
        resource_id=str(intent.id),
        diff_json={"kafka_mode": payload.kafka_mode, "kafka_version": payload.kafka_version},
        outcome="success",
        request=request,
    )
    return ResourceIntentOut.model_validate(intent)


@router.get("/clusters", response_model=list[ResourceIntentOut], dependencies=[Depends(require_perm("kafka.deploy"))])
def list_kafka_clusters(db: Session = Depends(get_db)) -> list[ResourceIntentOut]:
    rows = db.scalars(
        select(ResourceIntent).where(ResourceIntent.resource_type == "kafka").order_by(ResourceIntent.id.desc())
    ).all()
    return [ResourceIntentOut.model_validate(r) for r in rows]


@router.get("/migration-assistant", dependencies=[Depends(require_perm("kafka.deploy"))])
def migration_assistant(cluster_name: str, namespace: str) -> dict:
    return migration_precheck_report(cluster_name, namespace)


@router.get("/clusters/{intent_id}", response_model=ResourceIntentOut, dependencies=[Depends(require_perm("kafka.deploy"))])
def get_kafka_cluster(intent_id: int, db: Session = Depends(get_db)) -> ResourceIntentOut:
    item = db.scalar(select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "kafka"))
    if not item:
        raise HTTPException(status_code=404, detail="Kafka intent not found")
    return ResourceIntentOut.model_validate(item)


@router.put("/clusters/{intent_id}", response_model=ResourceIntentOut, dependencies=[Depends(require_perm("kafka.deploy"))])
def update_kafka_cluster(
    intent_id: int,
    payload: KafkaIntentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResourceIntentOut:
    intent = db.scalar(select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "kafka"))
    if not intent:
        raise HTTPException(status_code=404, detail="Kafka intent not found")

    enforce_namespace_access(db, user, payload.cluster_id, payload.namespace, "kafka.deploy")
    try:
        validate_kafka_mode(payload.kafka_mode, payload.kafka_version, payload.strimzi_version)
    except KafkaValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    intent.mode = payload.kafka_mode
    intent.cluster_id = payload.cluster_id
    intent.namespace = payload.namespace
    intent.spec_json = {
        **payload.spec_json,
        "kafka_version": payload.kafka_version,
        "strimzi_version": payload.strimzi_version,
        "kafka_mode": payload.kafka_mode,
    }
    intent.status = "pending"
    db.commit()
    db.refresh(intent)

    append_audit(
        db,
        actor=user,
        action="kafka.intent.update",
        resource_kind="kafka",
        resource_id=str(intent.id),
        diff_json={"kafka_mode": intent.mode, "namespace": intent.namespace},
        outcome="success",
        request=request,
    )
    return ResourceIntentOut.model_validate(intent)


@router.delete("/clusters/{intent_id}", dependencies=[Depends(require_perm("kafka.deploy"))])
def delete_kafka_cluster(
    intent_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    intent = db.scalar(select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "kafka"))
    if not intent:
        raise HTTPException(status_code=404, detail="Kafka intent not found")

    db.delete(intent)
    db.commit()
    append_audit(
        db,
        actor=user,
        action="kafka.intent.delete",
        resource_kind="kafka",
        resource_id=str(intent_id),
        diff_json={},
        outcome="success",
        request=request,
    )
    return {"status": "deleted"}


@router.get("/clusters/{intent_id}/status", dependencies=[Depends(require_perm("kafka.deploy"))])
def kafka_status(intent_id: int, db: Session = Depends(get_db)) -> dict:
    intent = db.scalar(select(ResourceIntent).where(ResourceIntent.id == intent_id, ResourceIntent.resource_type == "kafka"))
    if not intent:
        raise HTTPException(status_code=404, detail="Kafka intent not found")

    observed = db.scalar(
        select(ObservedResource).where(
            ObservedResource.cluster_id == intent.cluster_id,
            ObservedResource.namespace == intent.namespace,
            ObservedResource.resource_type == "kafka",
            ObservedResource.resource_name == intent.spec_json.get("name", "kafka-cluster"),
        )
    )
    return {"intent_status": intent.status, "observed_status": observed.observed_json if observed else None}
