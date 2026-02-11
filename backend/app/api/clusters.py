from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.config import get_settings
from app.core.crypto import SecretCrypto
from app.core.deps import get_current_user, get_db
from app.core.rbac import require_perm
from app.db.models import Cluster, User
from app.db.schemas import ClusterCreate, ClusterOut
from app.k8s.client import api_client_from_kubeconfig, core_v1
from app.k8s.utils import parse_kubeconfig

router = APIRouter(prefix="/clusters", tags=["clusters"])


def _cluster_out(cluster: Cluster) -> ClusterOut:
    return ClusterOut(
        id=cluster.id,
        name=cluster.name,
        kubeconfig_ref=f"enc://clusters/{cluster.id}",
        default_namespace_policy=cluster.default_namespace_policy,
        labels=cluster.labels,
        status=cluster.status,
    )


@router.get("", response_model=list[ClusterOut], dependencies=[Depends(require_perm("k8s.read"))])
def list_clusters(db: Session = Depends(get_db)) -> list[ClusterOut]:
    return [_cluster_out(c) for c in db.scalars(select(Cluster).order_by(Cluster.name)).all()]


@router.post("", response_model=ClusterOut, dependencies=[Depends(require_perm("k8s.write"))])
def create_cluster(
    payload: ClusterCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ClusterOut:
    if db.scalar(select(Cluster).where(Cluster.name == payload.name)):
        raise HTTPException(status_code=409, detail="Cluster exists")

    crypto = SecretCrypto(get_settings().fernet_key)
    cluster = Cluster(
        name=payload.name,
        kubeconfig_ref=crypto.encrypt(payload.kubeconfig),
        default_namespace_policy=payload.default_namespace_policy,
        labels=payload.labels,
        status="registered",
    )
    db.add(cluster)
    db.commit()
    db.refresh(cluster)

    append_audit(
        db,
        actor=actor,
        action="cluster.create",
        resource_kind="cluster",
        resource_id=str(cluster.id),
        diff_json={"name": cluster.name, "labels": cluster.labels},
        outcome="success",
        request=request,
    )
    return _cluster_out(cluster)


@router.get("/{cluster_id}/namespaces", dependencies=[Depends(require_perm("k8s.read"))])
def list_namespaces(cluster_id: int, db: Session = Depends(get_db)) -> dict:
    cluster = db.scalar(select(Cluster).where(Cluster.id == cluster_id))
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    crypto = SecretCrypto(get_settings().fernet_key)
    kubeconfig = parse_kubeconfig(crypto.decrypt(cluster.kubeconfig_ref))

    try:
        c = core_v1(api_client_from_kubeconfig(kubeconfig))
        rows = c.list_namespace().items
        return {"items": [r.metadata.name for r in rows]}
    except Exception:
        return {"items": [], "warning": "Failed to connect cluster with provided kubeconfig"}
