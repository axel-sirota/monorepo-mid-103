.PHONY: build test test-cover run migrate-up migrate-down tidy

MIGRATE ?= migrate
DATABASE_URL ?= postgres://monorepo:monorepo@localhost:5432/notifications_db?sslmode=disable

tidy:
	go mod tidy

build:
	go build -o ./tmp/notification-service ./cmd/server

test:
	go test ./... -count=1

test-cover: ## Run tests with coverage report
	go test ./... -coverprofile=coverage.out && go tool cover -html=coverage.out -o coverage.html

run:
	go run ./cmd/server

migrate-up:
	$(MIGRATE) -database "$(DATABASE_URL)" -path migrations up

migrate-down:
	$(MIGRATE) -database "$(DATABASE_URL)" -path migrations down 1
