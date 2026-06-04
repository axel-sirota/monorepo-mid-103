FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/inference-gateway ./cmd/server

FROM alpine:3.19
RUN apk add --no-cache ca-certificates wget
COPY --from=build /out/inference-gateway /usr/local/bin/inference-gateway
EXPOSE 9000
CMD ["inference-gateway"]
