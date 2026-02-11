SHELL := /bin/bash

.PHONY: backend-install backend-run backend-lint backend-test backend-migrate
.PHONY: worker-install worker-run worker-beat worker-lint worker-test
.PHONY: frontend-install frontend-run frontend-lint frontend-test
.PHONY: dev-up dev-down format

backend-install:
	cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -e .[dev]

backend-run:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-lint:
	cd backend && source .venv/bin/activate && ruff check app tests && mypy app

backend-test:
	cd backend && source .venv/bin/activate && pytest -q

backend-migrate:
	cd backend && source .venv/bin/activate && alembic upgrade head

worker-install:
	cd worker && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -e .[dev]

worker-run:
	cd worker && source .venv/bin/activate && celery -A app.celery_app worker -l INFO

worker-beat:
	cd worker && source .venv/bin/activate && celery -A app.celery_app beat -l INFO

worker-lint:
	cd worker && source .venv/bin/activate && ruff check app tests && mypy app

worker-test:
	cd worker && source .venv/bin/activate && pytest -q

frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

frontend-lint:
	cd frontend && npm run lint

frontend-test:
	cd frontend && npm run test -- --run

dev-up:
	docker compose -f deploy/docker/docker-compose.dev.yml up -d

dev-down:
	docker compose -f deploy/docker/docker-compose.dev.yml down

format:
	cd backend && source .venv/bin/activate && ruff check --fix app tests
	cd worker && source .venv/bin/activate && ruff check --fix app tests
	cd frontend && npm run format
