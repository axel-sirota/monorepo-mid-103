.PHONY: help up down logs ps reset \
        train predict codegen \
        test test-apps test-ml test-frontend \
        lint lint-apps lint-ml lint-frontend \
        install install-apps install-ml install-frontend \
        seed-data

# Default goal
.DEFAULT_GOAL := help

# Pretty colors (use printf, not echo, for portability)
BLUE := \033[34m
GREEN := \033[32m
RESET := \033[0m

help: ## Show this help
	@printf "$(BLUE)Monorepo dev commands$(RESET)\n\n"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ---------------------------- Stack lifecycle ----------------------------

up: ## Start full stack (prod mode)
	docker compose up -d

up-dev: ## Start full stack with hot-reload (dev mode)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

down: ## Stop and remove all containers
	docker compose down

reset: ## Stop, remove, and wipe volumes
	docker compose down -v

logs: ## Tail logs from all services
	docker compose logs -f --tail=100

ps: ## Show container status
	docker compose ps

# ---------------------------- ML lifecycle ----------------------------

train: ## Run one-shot training (writes /models/churn.joblib + MLflow run)
	docker compose --profile training run --rm training

predict: ## Send a sample prediction request via inference-gateway
	@curl -s -X POST http://localhost:9000/predict \
		-H "Content-Type: application/json" \
		-H "X-API-Key: $${INFERENCE_API_KEY:-dev-key-change-me}" \
		-d '{"user_id": 1, "engagement_score": 0.32, "days_since_login": 28, "sessions_last_30d": 2, "support_tickets_last_90d": 4}' | jq .

codegen: ## Generate client/server stubs from OpenAPI spec (Lab 6)
	@echo "🔧 Generating code from OpenAPI spec..."
	@command -v openapi-generator >/dev/null 2>&1 || { echo "⚠️  openapi-generator not found. Install: npm install -g @openapitools/openapi-generator-cli"; exit 1; }
	@openapi-generator generate -i contracts/openapi/user.yaml -g python-pydantic -o apps/user-service/app/generated --skip-validate-spec || true
	@openapi-generator generate -i contracts/openapi/user.yaml -g spring -o apps/api-gateway/target/generated-sources --skip-validate-spec || true
	@openapi-generator generate -i contracts/openapi/user.yaml -g go-server -o apps/notification-service/generated --skip-validate-spec || true
	@echo "✅ Code generation complete. Check generated/ directories in each service."

# ---------------------------- Testing ----------------------------

test: test-apps test-ml test-frontend ## Run tests for every cluster

test-apps: ## Run tests for apps/ cluster (Java + Python + Go)
	@printf "$(BLUE)Testing apps/api-gateway$(RESET)\n"
	cd apps/api-gateway && ./mvnw -B test
	@printf "$(BLUE)Testing apps/user-service$(RESET)\n"
	cd apps/user-service && uv run pytest
	@printf "$(BLUE)Testing apps/notification-service$(RESET)\n"
	cd apps/notification-service && go test ./...

test-ml: ## Run tests for ml/ cluster
	cd ml/model-serving && uv run pytest
	cd ml/inference-gateway && go test ./...

test-frontend: ## Run tests for frontend/ cluster
	cd frontend && npm test --workspaces --if-present

# ---------------------------- Linting ----------------------------

lint: lint-apps lint-ml lint-frontend ## Lint every cluster

lint-apps:
	cd apps/user-service && uv run ruff check .
	cd apps/notification-service && go vet ./...

lint-ml:
	cd ml/model-serving && uv run ruff check .
	cd ml/training && uv run ruff check .
	cd ml/inference-gateway && go vet ./...

lint-frontend:
	cd frontend && npm run lint --workspaces --if-present

# ---------------------------- Install / sync deps ----------------------------

install: install-apps install-ml install-frontend ## Install/sync deps in every cluster

install-apps:
	cd apps/api-gateway && ./mvnw -B -DskipTests package
	cd apps/user-service && uv sync
	cd apps/notification-service && go mod download

install-ml:
	cd ml/model-serving && uv sync
	cd ml/training && uv sync
	cd ml/inference-gateway && go mod download

install-frontend:
	cd frontend && npm install
