# Nexa Control Plane Architecture

## Product Identity
Nexa Control Plane is a fresh implementation for operating Spark and Kafka platforms across Kubernetes clusters.
It is inspired by real operational workflows but not copied from existing dashboards.

## Design Principles
- Fresh-first codebase: all product code authored in this repository.
- Integration-only OSS policy: operators and SDKs are consumed through APIs, not code cloning.
- Desired-state + observed-state split for reliable reconciliation.
- Least privilege and explicit audit for every mutation.
- Multi-cluster-by-default with namespace-level authorization boundaries.

## Planes
- Experience Plane:
  - React UI with permission-aware navigation.
  - Learning workspace embedded in product UI.
- Control Plane:
  - FastAPI gateway for auth/RBAC/audit and orchestration APIs.
  - Celery workers for long-running operations.
  - Scheduled evaluators for alerts and incident workflows.
- Data Plane:
  - Spark applications through Spark Operator CRDs.
  - Kafka clusters through Strimzi with strict compatibility contracts.
- Insight Plane:
  - Prometheus query federation (no timeseries in MySQL).
  - Incident evidence and AI summary/cost telemetry.

## Runtime Flow
1. UI sends a desired state request.
2. API validates identity, permission, namespace scope, and compatibility rules.
3. Intent is persisted in MySQL (`resource_intents`).
4. Worker executes action and records run state (`resource_runs`).
5. Watchers/evaluators update observed snapshots and incidents.
6. UI reads merged intent+observed state and audit logs.

## Compatibility Contracts
- Kafka KRaft: Kafka `>=4.0.0` with Strimzi `>=0.46.0`.
- Kafka legacy ZooKeeper mode: Kafka `3.8.1` with Strimzi `0.45.x` only.
- Spark: SparkApplication-first execution model via Spark Operator.

## Security Controls
- JWT access and refresh with role and permission enforcement.
- Namespace policy checks for all mutating actions.
- Audit log append on each mutation (`who`, `what`, `when`, `diff`, `outcome`).
- Encrypted kubeconfig references; decryption key sourced from environment.

## Reliability Controls
- Queue-backed asynchronous operations.
- Retry/backoff for scheduled and long-running tasks.
- Explicit readiness endpoints and health checks.
- Immutable execution history for rollback/forensics.
