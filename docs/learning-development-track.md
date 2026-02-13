# Learning Along Development Track

## Goal
Build production capabilities while learning the platform internals phase by phase.

## Track
1. L1 Foundation
- Learn: cluster topology, namespaces, workloads, RBAC.
- Build: cluster registry + workload explorer + permission checks.

2. L2 Safe Mutations
- Learn: control loops, failure handling, auditability.
- Build: scale/restart/delete flows with audit logs and rollback strategy.

3. L3 Data Platform Services
- Learn: CRD-driven operations for Spark and Kafka.
- Build: Spark and Kafka service catalogs with validation boundaries.

4. L4 SRE Operations
- Learn: metrics, alerts, incident workflows, notification fanout.
- Build: Prometheus dashboard APIs + alert evaluator + incidents.

5. L5 AI for Operations
- Learn: LLM guardrails, usage telemetry, cost governance.
- Build: incident summarization + token/cost reporting.

## Execution Cadence
- Each phase has: design review, implementation PR, test gates, runbook updates.
- Complete one phase before expanding scope.
