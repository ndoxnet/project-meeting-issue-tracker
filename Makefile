# Concept by MrHan (08974747477)
# Task commands. Build/up targets are guarded — they must NOT run on the
# production VPS in Phase 1 (see ADR-004).

.DEFAULT_GOAL := help
ENV_FILE ?= .env

.PHONY: help lint-backend test-backend dev-backend dev-frontend \
        compose-config compose-build compose-up compose-down \
        migration-new migration-up \
        openapi-export openapi-check contract-test frontend-types-generate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

lint-backend: ## Ruff lint (backend, dev machine)
	cd backend && ruff check app

test-backend: ## Run backend tests (dev machine)
	cd backend && pytest

dev-backend: ## Run backend dev server (dev machine)
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run frontend dev server (OFF-VPS)
	cd frontend && npm run dev

compose-config: ## Render & validate compose (safe: no build/pull/up)
	docker compose --env-file $(ENV_FILE) config

compose-build: ## Build images — DO NOT run on the production VPS (ADR-004)
	@echo ">>> REFUSING by default: frontend build must run OFF the VPS."
	@echo ">>> If you are OFF-VPS, run: docker compose --env-file $(ENV_FILE) build"
	@exit 1

compose-up: ## Start stack — NOT in Phase 1 on the VPS
	@echo ">>> Phase 1: do not start the stack on the production VPS."
	@echo ">>> Deployment sequence is in docs/DEPLOYMENT.md."
	@exit 1

compose-down: ## Stop the stack (no volume removal)
	docker compose --env-file $(ENV_FILE) down

migration-new: ## Create a new Alembic revision (NAME=...)
	cd backend && alembic revision --autogenerate -m "$(NAME)"

migration-up: ## Apply migrations to head
	cd backend && alembic upgrade head

openapi-export: ## Export OpenAPI to docs/api/openapi.{json,yaml} (no DB needed)
	cd backend && .venv/bin/python scripts/export_openapi.py

openapi-check: ## Fail if the committed OpenAPI is stale vs the app
	cd backend && .venv/bin/python scripts/export_openapi.py
	git diff --exit-code docs/api/openapi.json docs/api/openapi.yaml \
	  || (echo ">>> OpenAPI is stale — commit the regenerated docs/api/openapi.*" && exit 1)

contract-test: ## Run API contract tests
	cd backend && .venv/bin/pytest tests/contract -q

frontend-types-generate: ## Generate TS types from OpenAPI (OFF-VPS only)
	@echo ">>> Do NOT run npm-based type generation on the production VPS."
	@echo ">>> Off-VPS / CI, run:"
	@echo "    npx openapi-typescript docs/api/openapi.json \\"
	@echo "      --output frontend/src/api/generated/schema.ts"
