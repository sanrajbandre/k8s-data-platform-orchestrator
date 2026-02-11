# Codex Prompt Pack

## Global Preamble
```text
/plan Work only in this monorepo. Preserve existing conventions. Implement production-grade code with tests, docs updates, and migration scripts where needed. Enforce RBAC + namespace scoping on all mutating endpoints. Add audit log writes for every mutation. Do not store timeseries in MySQL. For Kafka, enforce: Kafka 4.x => KRaft only; ZooKeeper legacy only for Kafka 3.8.1 with Strimzi 0.45.x.
```

## Phase Prompts
1. `/plan Bootstrap monorepo structure, Makefile targets, env templates, Dockerfiles, and CI workflows for backend/worker/frontend.`
2. `/plan Implement auth+RBAC+audit with SQLAlchemy/Alembic, JWT access+refresh, Argon2 hashing, and permission dependency helpers.`
3. `/plan Add cluster registry and secure kubeconfig reference handling with namespace policy model and enforcement middleware.`
4. `/plan Implement K8s read APIs (namespaces, workloads, pods, logs, events) with per-cluster routing and RBAC checks.`
5. `/plan Implement safe mutating K8s actions (scale, restart, delete, cordon/drain) via Celery jobs with rollback/error tracking.`
6. `/plan Add SparkApplication service: templates, CRUD endpoints, status mapper, and worker wait-for-completion jobs.`
7. `/plan Add Kafka service: KRaft + legacy modes, CR templates, version/operator validation, and migration-assistant precheck endpoint.`
8. `/plan Implement metrics proxy endpoints and backend normalization for cluster, namespace, Kafka, and Spark dashboards.`
9. `/plan Implement alerts engine with PromQL evaluation scheduler, incident lifecycle, and notification adapters (webhook/slack/email).`
10. `/plan Implement AI analytics pipeline for incidents with OpenAI integration, usage token capture, DB pricing table lookup, and cost reporting APIs.`
11. `/plan Build React pages and permission-aware routing for login, cluster explorer, Spark, Kafka, metrics, alerts, AI insights, and admin.`
12. `/plan Complete GA hardening: threat model closure, rate limits, API pagination, load tests, docs/runbooks, and release checklist.`

## Follow-up Prompt
```text
Implement exactly the approved plan for this phase. Include code, migrations, tests, and docs. Run the relevant checks and report results plus any residual risks.
```
