.PHONY: build test run tidy

build:
	go build -o ./tmp/inference-gateway ./cmd/server

test:
	go test ./... -count=1

run:
	go run ./cmd/server

tidy:
	go mod tidy
