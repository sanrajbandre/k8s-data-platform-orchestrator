from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.config import get_settings
from app.core.crypto import SecretCrypto
from app.core.deps import get_current_user, get_db
from app.core.rbac import require_perm
from app.db.models import Cluster, User, UserNamespaceScope
from app.db.schemas import ClusterCreate, ClusterOut, NamespacePolicyCreate, NamespacePolicyOut
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


@router.get(
    "/{cluster_id}/namespace-policies",
    response_model=list[NamespacePolicyOut],
    dependencies=[Depends(require_perm("admin.rbac.read"))],
)
def list_namespace_policies(cluster_id: int, db: Session = Depends(get_db)) -> list[NamespacePolicyOut]:
    cluster = db.scalar(select(Cluster).where(Cluster.id == cluster_id))
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    rows = db.scalars(
        select(UserNamespaceScope)
        .where(UserNamespaceScope.cluster_id == cluster_id)
        .order_by(UserNamespaceScope.namespace.asc(), UserNamespaceScope.user_id.asc())
    ).all()
    return [NamespacePolicyOut.model_validate(row) for row in rows]


@router.post(
    "/{cluster_id}/namespace-policies",
    response_model=NamespacePolicyOut,
    dependencies=[Depends(require_perm("admin.rbac.write"))],
)
def upsert_namespace_policy(
    cluster_id: int,
    payload: NamespacePolicyCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> NamespacePolicyOut:
    cluster = db.scalar(select(Cluster).where(Cluster.id == cluster_id))
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    if db.scalar(select(User).where(User.id == payload.user_id)) is None:
        raise HTTPException(status_code=404, detail="Target user not found")

    scope = db.scalar(
        select(UserNamespaceScope).where(
            UserNamespaceScope.cluster_id == cluster_id,
            UserNamespaceScope.user_id == payload.user_id,
            UserNamespaceScope.namespace == payload.namespace,
        )
    )
    if scope is None:
        scope = UserNamespaceScope(
            user_id=payload.user_id,
            cluster_id=cluster_id,
            namespace=payload.namespace,
            allowed_actions={"actions": payload.allowed_actions},
            denied_actions={"actions": payload.denied_actions},
        )
        db.add(scope)
    else:
        scope.allowed_actions = {"actions": payload.allowed_actions}
        scope.denied_actions = {"actions": payload.denied_actions}

    db.commit()
    db.refresh(scope)
    append_audit(
        db,
        actor=actor,
        action="cluster.namespace_policy.upsert",
        resource_kind="namespace_policy",
        resource_id=str(scope.id),
        diff_json={
            "cluster_id": cluster_id,
            "user_id": payload.user_id,
            "namespace": payload.namespace,
            "allowed_actions": payload.allowed_actions,
            "denied_actions": payload.denied_actions,
        },
        outcome="success",
        request=request,
    )
    return NamespacePolicyOut.model_validate(scope)


@router.delete(
    "/{cluster_id}/namespace-policies/{scope_id}",
    dependencies=[Depends(require_perm("admin.rbac.write"))],
)
def delete_namespace_policy(
    cluster_id: int,
    scope_id: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    scope = db.scalar(
        select(UserNamespaceScope).where(
            UserNamespaceScope.id == scope_id,
            UserNamespaceScope.cluster_id == cluster_id,
        )
    )
    if scope is None:
        raise HTTPException(status_code=404, detail="Namespace policy not found")

    db.delete(scope)
    db.commit()
    append_audit(
        db,
        actor=actor,
        action="cluster.namespace_policy.delete",
        resource_kind="namespace_policy",
        resource_id=str(scope_id),
        diff_json={"cluster_id": cluster_id},
        outcome="success",
        request=request,
    )
    return {"status": "deleted"}
