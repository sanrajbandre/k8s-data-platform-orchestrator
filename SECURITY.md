# Security Policy

## Supported Versions
Security updates are provided for the latest `main` and current release branch.

## Reporting a Vulnerability
Please report vulnerabilities privately by opening a private security advisory or
contacting maintainers through secure channels.

Include:
- Affected version/commit
- Reproduction steps
- Expected vs actual behavior
- Suggested remediation (if available)

## Security Baseline
- Least-privileged cluster access
- Namespace-scoped RBAC enforcement
- JWT auth with short-lived access tokens
- Immutable mutation audit logs
- Dependency scanning in CI
