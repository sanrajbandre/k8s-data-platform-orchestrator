# Contributing

## Development Setup
- Python 3.12+
- Node 20+
- Docker + Docker Compose
- MySQL 8 and Redis (via `deploy/docker/docker-compose.dev.yml`)

## Workflow
1. Fork and create a feature branch (`codex/<feature-name>` recommended).
2. Run checks before pushing:
   - `make backend-lint backend-test`
   - `make worker-lint worker-test`
   - `make frontend-lint frontend-test`
3. Open a PR using the provided template.

## Commit and PR Expectations
- Keep changes scoped and include tests.
- Document API or schema changes in `docs/api-spec.md` and ADRs where needed.
- Include migration scripts for DB changes.

## Security and Secrets
- Never commit secrets.
- Use env files and secret references.
- Report vulnerabilities per `SECURITY.md`.
