# Multi-stage build for ProjectFlow Intelligence Backend
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /app

# Copy gradle wrapper and build files
COPY gradlew gradlew.bat settings.gradle build.gradle gradle.properties ./
COPY gradle/ gradle/
COPY shared-core/ shared-core/
COPY backend/ backend/

# Ensure gradlew has execution rights
RUN chmod +x gradlew

# Build backend jar
RUN ./gradlew :backend:bootJar --no-daemon

# Runtime stage
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Create non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Copy executable jar from builder stage
COPY --from=builder /app/backend/build/libs/*.jar app.jar

# Render exposes PORT dynamically (defaults to 8080)
ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java -Xmx400m -Dserver.port=${PORT:-8080} -jar app.jar"]
