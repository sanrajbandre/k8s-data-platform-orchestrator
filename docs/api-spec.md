# API Specification (v0.1-alpha)

## Auth
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`
- `POST /auth/users`

## RBAC
- `GET /rbac/roles`
- `GET /rbac/permissions`
- `POST /rbac/users/{user_id}/roles/{role_id}`
- `GET /users`
- `GET /roles`
- `GET /permissions`

## Clusters
- `GET /clusters`
- `POST /clusters`
- `GET /clusters/{cluster_id}/namespaces`
- `GET /clusters/{cluster_id}/namespace-policies`
- `POST /clusters/{cluster_id}/namespace-policies`
- `DELETE /clusters/{cluster_id}/namespace-policies/{scope_id}`

## Kubernetes
- `GET /k8s/{cluster_id}/workloads`
- `GET /k8s/{cluster_id}/pods`
- `GET /k8s/{cluster_id}/pods/{namespace}/{name}/logs`
- `GET /k8s/{cluster_id}/events`
- `POST /k8s/{cluster_id}/deployments/{namespace}/{name}/scale`
- `POST /k8s/{cluster_id}/deployments/{namespace}/{name}/rollout-restart`
- `DELETE /k8s/{cluster_id}/pods/{namespace}/{name}`
- `POST /k8s/{cluster_id}/nodes/{name}/cordon`
- `POST /k8s/{cluster_id}/nodes/{name}/drain`

## Services
- Spark: templates + CRUD + status `/services/spark/*`
- Kafka: templates + CRUD + status + migration assistant `/services/kafka/*`

## Orchestration
- `POST /orchestration/intents/{intent_id}/apply`
- `GET /orchestration/intents/{intent_id}/runs`
- `GET /orchestration/runs/{run_id}`

## Metrics
- `GET /metrics/query`
- `GET /metrics/range`
- `GET /metrics/dashboards/cluster-overview`
- `GET /metrics/dashboards/kafka-overview`

## Alerts
- `GET /alerts/rules`
- `POST /alerts/rules`
- `GET /alerts/incidents`
- `POST /alerts/incidents/{incident_id}/ack`

## AI
- `POST /ai/incidents/{incident_id}/analyze`
- `GET /ai/usage`
- `GET /ai/cost-reports`

## Audit
- `GET /audit/logs`

## Platform
- `GET /platform/about`
- `GET /platform/oss-repositories`
- `GET /platform/learning-path`
