# syntax=docker/dockerfile:1.7
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /workspace

# Wrapper + pom first for better layer caching.
COPY mvnw mvnw
COPY .mvn .mvn
COPY pom.xml pom.xml
RUN chmod +x mvnw && ./mvnw -B -q -DskipTests dependency:go-offline || true

COPY src src
RUN ./mvnw -B -DskipTests package && \
    cp target/api-gateway-*.jar app.jar

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
# wget for the docker-compose healthcheck (alpine JRE doesn't ship it)
RUN apk add --no-cache wget
COPY --from=build /workspace/app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
