.PHONY: build test run migrate-up migrate-down tidy

MIGRATE ?= migrate
DATABASE_URL ?= postgres://monorepo:monorepo@localhost:5432/notifications_db?sslmode=disable

tidy:
	go mod tidy

build:
	go build -o ./tmp/notification-service ./cmd/server

test:
	go test ./... -count=1

run:
	go run ./cmd/server

migrate-up:
	$(MIGRATE) -database "$(DATABASE_URL)" -path migrations up

migrate-down:
	$(MIGRATE) -database "$(DATABASE_URL)" -path migrations down 1
