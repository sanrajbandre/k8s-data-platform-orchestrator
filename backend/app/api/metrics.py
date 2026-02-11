from fastapi import APIRouter, Depends, HTTPException

from app.core.rbac import require_perm
from app.db.schemas import PromQueryRequest, PromRangeRequest
from app.services.metrics import query_prometheus

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/query", dependencies=[Depends(require_perm("k8s.read"))])
def query(payload: PromQueryRequest) -> dict:
    try:
        params = {"query": payload.query}
        if payload.time is not None:
            params["time"] = payload.time
        return query_prometheus("/api/v1/query", params)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Prometheus query failed: {exc}") from exc


@router.post("/range", dependencies=[Depends(require_perm("k8s.read"))])
def range_query(payload: PromRangeRequest) -> dict:
    try:
        params = {
            "query": payload.query,
            "start": payload.start,
            "end": payload.end,
            "step": payload.step,
        }
        return query_prometheus("/api/v1/query_range", params)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Prometheus query_range failed: {exc}") from exc


@router.get("/dashboards/cluster-overview", dependencies=[Depends(require_perm("k8s.read"))])
def cluster_overview_dashboard() -> dict:
    try:
        cpu = query_prometheus(
            "/api/v1/query",
            {"query": "sum(rate(container_cpu_usage_seconds_total{container!=''}[5m]))"},
        )
        memory = query_prometheus(
            "/api/v1/query",
            {"query": "sum(container_memory_working_set_bytes{container!=''})"},
        )
        restarts = query_prometheus(
            "/api/v1/query",
            {"query": "sum(kube_pod_container_status_restarts_total)"},
        )
        return {"cpu": cpu, "memory": memory, "restarts": restarts}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Dashboard query failed: {exc}") from exc


@router.get("/dashboards/kafka-overview", dependencies=[Depends(require_perm("k8s.read"))])
def kafka_overview_dashboard() -> dict:
    try:
        urp = query_prometheus(
            "/api/v1/query",
            {"query": "sum(kafka_server_replicamanager_underreplicatedpartitions)"},
        )
        request_latency = query_prometheus(
            "/api/v1/query",
            {"query": "histogram_quantile(0.95, sum(rate(kafka_network_requestmetrics_totaltimems_bucket[5m])) by (le))"},
        )
        return {"under_replicated_partitions": urp, "request_latency_p95": request_latency}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Kafka dashboard query failed: {exc}") from exc
