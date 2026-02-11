# Threat Model

## Assets
- Cluster credentials and tokenized kubeconfig references.
- User identities, RBAC bindings, audit logs.
- Incident evidence and AI analysis outputs.

## Threats
- Unauthorized namespace mutation via broken RBAC checks.
- Token replay or refresh token theft.
- Secrets exposure in logs or API payloads.
- SSRF via unsafe metrics proxy URLs.
- Prompt injection in AI incident summaries.

## Controls
- Centralized permission dependencies and namespace allowlist checks.
- Short access token TTL with refresh token rotation.
- Sensitive fields redaction in logs and audit diff snapshots.
- Static allowlist for Prometheus base URL.
- AI prompt guardrails and restricted output rendering.
