# ===== Stage 1: Build the application =====
FROM openjdk:17-jdk-slim as builder

# Install Python and required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install torch diffusers psutil

WORKDIR /app

COPY mvnw pom.xml ./
COPY .mvn .mvn
COPY src src

RUN chmod +x ./mvnw
RUN ./mvnw clean package -DskipTests

# ===== Stage 2: Run the application =====
FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy only the final JAR from the builder stage
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar", "--server.port=${PORT}"]
