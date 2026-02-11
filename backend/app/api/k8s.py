from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import append_audit
from app.core.config import get_settings
from app.core.crypto import SecretCrypto
from app.core.deps import get_current_user, get_db
from app.core.rbac import enforce_namespace_access, require_perm
from app.db.models import Cluster, User
from app.db.schemas import ScaleRequest
from app.k8s.client import api_client_from_kubeconfig, apps_v1, core_v1
from app.k8s.utils import parse_kubeconfig

router = APIRouter(prefix="/k8s", tags=["k8s"])


def _cluster_client(db: Session, cluster_id: int):
    cluster = db.scalar(select(Cluster).where(Cluster.id == cluster_id))
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    crypto = SecretCrypto(get_settings().fernet_key)
    kubeconfig = parse_kubeconfig(crypto.decrypt(cluster.kubeconfig_ref))
    return api_client_from_kubeconfig(kubeconfig)


@router.get("/{cluster_id}/workloads", dependencies=[Depends(require_perm("k8s.read"))])
def list_workloads(
    cluster_id: int,
    namespace: str = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    try:
        c = apps_v1(_cluster_client(db, cluster_id))
        deps = c.list_namespaced_deployment(namespace).items
        sts = c.list_namespaced_stateful_set(namespace).items
        dss = c.list_namespaced_daemon_set(namespace).items
        return {
            "deployments": [x.metadata.name for x in deps],
            "statefulsets": [x.metadata.name for x in sts],
            "daemonsets": [x.metadata.name for x in dss],
        }
    except Exception:
        return {"deployments": [], "statefulsets": [], "daemonsets": []}


@router.get("/{cluster_id}/pods", dependencies=[Depends(require_perm("k8s.read"))])
def list_pods(cluster_id: int, namespace: str = Query(...), db: Session = Depends(get_db)) -> dict:
    try:
        c = core_v1(_cluster_client(db, cluster_id))
        pods = c.list_namespaced_pod(namespace).items
        return {"items": [p.metadata.name for p in pods]}
    except Exception:
        return {"items": []}


@router.get("/{cluster_id}/pods/{namespace}/{name}/logs", dependencies=[Depends(require_perm("k8s.read"))])
def get_pod_logs(cluster_id: int, namespace: str, name: str, db: Session = Depends(get_db)) -> dict:
    try:
        c = core_v1(_cluster_client(db, cluster_id))
        return {"logs": c.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=200)}
    except Exception:
        return {"logs": ""}


@router.get("/{cluster_id}/events", dependencies=[Depends(require_perm("k8s.read"))])
def list_events(cluster_id: int, namespace: str = Query(...), db: Session = Depends(get_db)) -> dict:
    try:
        c = core_v1(_cluster_client(db, cluster_id))
        events = c.list_namespaced_event(namespace).items
        return {
            "items": [
                {
                    "type": e.type,
                    "reason": e.reason,
                    "message": e.message,
                    "object": e.involved_object.name if e.involved_object else None,
                }
                for e in events
            ]
        }
    except Exception:
        return {"items": []}


@router.post(
    "/{cluster_id}/deployments/{namespace}/{name}/scale",
    dependencies=[Depends(require_perm("k8s.write"))],
)
def scale_deployment(
    cluster_id: int,
    namespace: str,
    name: str,
    payload: ScaleRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    enforce_namespace_access(db, user, cluster_id, namespace, "k8s.scale")

    try:
        c = apps_v1(_cluster_client(db, cluster_id))
        body = {"spec": {"replicas": payload.replicas}}
        c.patch_namespaced_deployment_scale(name=name, namespace=namespace, body=body)
        outcome = "success"
    except Exception:
        outcome = "failed"

    append_audit(
        db,
        actor=user,
        action="k8s.scale",
        resource_kind="deployment",
        resource_id=f"{namespace}/{name}",
        diff_json={"replicas": payload.replicas, "cluster_id": cluster_id},
        outcome=outcome,
        request=request,
    )
    return {"status": outcome}


@router.post(
    "/{cluster_id}/deployments/{namespace}/{name}/rollout-restart",
    dependencies=[Depends(require_perm("k8s.write"))],
)
def rollout_restart(
    cluster_id: int,
    namespace: str,
    name: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    enforce_namespace_access(db, user, cluster_id, namespace, "k8s.rollout_restart")
    outcome = "success"
    try:
        c = apps_v1(_cluster_client(db, cluster_id))
        body = {
            "spec": {
                "template": {
                    "metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": "now"}}
                }
            }
        }
        c.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
    except Exception:
        outcome = "failed"

    append_audit(
        db,
        actor=user,
        action="k8s.rollout_restart",
        resource_kind="deployment",
        resource_id=f"{namespace}/{name}",
        diff_json={"cluster_id": cluster_id},
        outcome=outcome,
        request=request,
    )
    return {"status": outcome}


@router.delete(
    "/{cluster_id}/pods/{namespace}/{name}",
    dependencies=[Depends(require_perm("k8s.write"))],
)
def delete_pod(
    cluster_id: int,
    namespace: str,
    name: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    enforce_namespace_access(db, user, cluster_id, namespace, "k8s.delete_pod")
    outcome = "success"
    try:
        c = core_v1(_cluster_client(db, cluster_id))
        c.delete_namespaced_pod(name=name, namespace=namespace, grace_period_seconds=20)
    except Exception:
        outcome = "failed"

    append_audit(
        db,
        actor=user,
        action="k8s.delete_pod",
        resource_kind="pod",
        resource_id=f"{namespace}/{name}",
        diff_json={"cluster_id": cluster_id},
        outcome=outcome,
        request=request,
    )
    return {"status": outcome}


@router.post("/{cluster_id}/nodes/{name}/cordon", dependencies=[Depends(require_perm("admin.all"))])
def cordon_node(
    cluster_id: int,
    name: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    outcome = "success"
    try:
        c = core_v1(_cluster_client(db, cluster_id))
        c.patch_node(name=name, body={"spec": {"unschedulable": True}})
    except Exception:
        outcome = "failed"
    append_audit(
        db,
        actor=user,
        action="k8s.cordon_node",
        resource_kind="node",
        resource_id=name,
        diff_json={"cluster_id": cluster_id},
        outcome=outcome,
        request=request,
    )
    return {"status": outcome}


@router.post("/{cluster_id}/nodes/{name}/drain", dependencies=[Depends(require_perm("admin.all"))])
def drain_node(
    cluster_id: int,
    name: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    # A full drain implementation should evict pods respecting PDBs. This is a guarded stub.
    append_audit(
        db,
        actor=user,
        action="k8s.drain_node.requested",
        resource_kind="node",
        resource_id=name,
        diff_json={"cluster_id": cluster_id},
        outcome="queued",
        request=request,
    )
    return {"status": "queued", "note": "drain orchestration should run in worker for full safety"}
