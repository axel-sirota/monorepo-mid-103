FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/notification-service ./cmd/server

FROM alpine:3.19
RUN apk add --no-cache ca-certificates wget
WORKDIR /app
COPY --from=build /out/notification-service /usr/local/bin/notification-service
COPY migrations /app/migrations
EXPOSE 8002
CMD ["notification-service"]
