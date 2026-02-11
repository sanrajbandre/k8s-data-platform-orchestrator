# K8s Data Platform Orchestrator

Open-source multi-cluster Kubernetes orchestration dashboard for Spark 4.x and Kafka 3.8.1/4.x.

## Stack
- Frontend: React 18 + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy + Alembic + MySQL 8
- Worker: Celery + Redis
- Metrics: Prometheus query proxy (no timeseries persisted in MySQL)
- AI: OpenAI incident analysis with token/cost accounting

## Repository Layout
- `backend/`: API gateway, RBAC, orchestration APIs
- `worker/`: Celery workers, schedulers, watchers
- `frontend/`: React dashboard and admin UX
- `docs/`: architecture, threat model, API spec, runbooks
- `deploy/`: docker/k8s manifests and Helm stubs

Implementation snapshot: `docs/implementation-status.md`

## Quick Start
1. Copy env files:
   - `cp backend/.env.example backend/.env`
   - `cp worker/.env.example worker/.env`
   - `cp frontend/.env.example frontend/.env`
   - Generate and set `FERNET_KEY` in `backend/.env` (for encrypted kubeconfig refs)
2. Start local dependencies (MySQL + Redis):
   - `docker compose -f deploy/docker/docker-compose.dev.yml up -d`
3. Install and run:
   - `make backend-install && make worker-install && make frontend-install`
   - `make backend-run`
   - `make worker-run`
   - `make frontend-run`

## Rocky 9 Automation (Ansible)
- Playbooks live in `/Users/sanraj/Documents/CODEX-HOME/k8s-data-platform-orchestrator/deploy/ansible`.
- Full deployment:
  - `cd deploy/ansible`
  - `cp inventory/hosts.ini.example inventory/hosts.ini`
  - `cp group_vars/all.yml.example group_vars/all.yml`
  - `ansible-galaxy collection install -r requirements.yml`
  - `ansible-playbook playbooks/site.yml`
- Maintenance restart options:
  - Entire app: `ansible-playbook playbooks/maintenance.yml -e restart_target=all`
  - Backend only: `ansible-playbook playbooks/maintenance.yml -e restart_target=backend`
  - Frontend only: `ansible-playbook playbooks/maintenance.yml -e restart_target=frontend`

## Milestones
- `v0.1-alpha`: auth/rbac/audit, multi-cluster registry, K8s explorer, Spark orchestration
- `v0.2-beta`: Kafka dual-mode support, metrics dashboards, alerts engine
- `v1.0-ga`: AI analytics/cost tracking, hardening, threat model closure

## Compatibility Contracts
- Kafka 4.x is KRaft-only.
- ZooKeeper mode is legacy (`Kafka 3.8.1` + `Strimzi 0.45.x`) and explicitly validated.
- KRaft mode requires Strimzi `0.46+`.

## License
Apache-2.0
