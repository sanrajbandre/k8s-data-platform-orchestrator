# Architecture

## Planes
- Control plane: React UI, FastAPI API gateway, Celery worker/scheduler/watchers.
- Data plane: Spark Operator CRDs and Strimzi Kafka CRDs on managed clusters.
- Observability plane: Prometheus/Alertmanager/Grafana.

## Core Design
- Desired state is persisted in MySQL (`resource_intents`).
- Long-running actions execute through Celery and persist run history (`resource_runs`).
- Watchers project observed state into `observed_resources` for UI consistency.
- Audit logs are append-only and generated for all mutation operations.

## Compatibility Rules
- Kafka KRaft: Kafka 4.x + Strimzi 0.46+.
- Kafka legacy ZooKeeper: Kafka 3.8.1 + Strimzi 0.45.x only.

## Security
- JWT auth with refresh rotation.
- Service-scoped permissions and namespace policies.
- Per-cluster kubeconfig secret references with encryption helper.
