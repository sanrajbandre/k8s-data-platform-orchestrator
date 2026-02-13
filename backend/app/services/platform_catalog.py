from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

PRODUCT_PROFILE: dict[str, Any] = {
    "name": "Nexa Control Plane",
    "tagline": "Multi-cluster data platform orchestration for Spark and Kafka",
    "implementation_policy": {
        "code_origin": "fresh-first",
        "rule": "No direct code copy from external dashboards; only API-level integrations and standard SDK usage",
        "updated_at": datetime.now(UTC).isoformat(),
    },
}

OSS_REPOSITORIES: list[dict[str, str]] = [
    {
        "name": "Kubernetes Python Client",
        "repository": "https://github.com/kubernetes-client/python",
        "license": "Apache-2.0",
        "usage": "Kubernetes API access for cluster/workload operations",
    },
    {
        "name": "Kubeflow Spark Operator",
        "repository": "https://github.com/kubeflow/spark-operator",
        "license": "Apache-2.0",
        "usage": "SparkApplication CRD lifecycle management",
    },
    {
        "name": "Strimzi",
        "repository": "https://github.com/strimzi/strimzi-kafka-operator",
        "license": "Apache-2.0",
        "usage": "Kafka CR lifecycle (KRaft + legacy guarded mode)",
    },
    {
        "name": "Prometheus",
        "repository": "https://github.com/prometheus/prometheus",
        "license": "Apache-2.0",
        "usage": "Metrics query backend via HTTP API",
    },
    {
        "name": "Grafana",
        "repository": "https://github.com/grafana/grafana",
        "license": "AGPL-3.0",
        "usage": "External observability dashboard embedding/integration",
    },
    {
        "name": "OpenTelemetry",
        "repository": "https://github.com/open-telemetry/opentelemetry-python",
        "license": "Apache-2.0",
        "usage": "Tracing and metrics instrumentation",
    },
    {
        "name": "FastAPI",
        "repository": "https://github.com/fastapi/fastapi",
        "license": "MIT",
        "usage": "API gateway framework",
    },
    {
        "name": "React",
        "repository": "https://github.com/facebook/react",
        "license": "MIT",
        "usage": "Frontend rendering framework",
    },
]

LEARNING_PATH: list[dict[str, Any]] = [
    {
        "phase": "L1",
        "title": "Core Kubernetes Operations",
        "goal": "Understand multi-cluster discovery, namespace scoping, and read APIs",
        "deliverables": [
            "Cluster registry CRUD",
            "Namespace/workload/pod explorer",
            "Permission and namespace policy checks",
        ],
    },
    {
        "phase": "L2",
        "title": "Controlled Mutations and Audit",
        "goal": "Implement safe write operations with immutable tracking",
        "deliverables": [
            "Scale/restart/delete flows",
            "Node cordon and queued drain",
            "Mutation audit with actor/diff/outcome",
        ],
    },
    {
        "phase": "L3",
        "title": "Data Service Orchestration",
        "goal": "Deliver Spark and Kafka service catalogs with strong validation",
        "deliverables": [
            "SparkApplication template CRUD",
            "Kafka KRaft and legacy compatibility guards",
            "Migration assistant prechecks",
        ],
    },
    {
        "phase": "L4",
        "title": "SRE Automation",
        "goal": "Connect metrics, alerts, incidents, and response workflows",
        "deliverables": [
            "Prometheus proxy + dashboard API",
            "Alert evaluator scheduler + notifications",
            "Incident lifecycle APIs",
        ],
    },
    {
        "phase": "L5",
        "title": "AI-Assisted Operations",
        "goal": "Add controlled AI insights with transparent usage accounting",
        "deliverables": [
            "Incident summarization API",
            "Per-model pricing and cost reports",
            "Guardrailed AI trigger policy",
        ],
    },
]

ROADMAP: list[dict[str, str]] = [
    {"milestone": "v0.1-alpha", "focus": "Identity, RBAC, multi-cluster read + safe write foundation"},
    {"milestone": "v0.2-beta", "focus": "Spark/Kafka catalogs, metrics dashboards, alerts engine"},
    {"milestone": "v1.0-ga", "focus": "AI insights, hardening, scale tests, production runbooks"},
]


def platform_overview() -> dict[str, Any]:
    return {
        "product": PRODUCT_PROFILE,
        "roadmap": ROADMAP,
        "capabilities": {
            "control_plane": ["auth", "rbac", "orchestration", "audit"],
            "data_plane": ["spark", "kafka"],
            "observability": ["metrics", "alerts", "incidents"],
            "analytics": ["ai_summary", "token_cost_tracking"],
        },
    }
