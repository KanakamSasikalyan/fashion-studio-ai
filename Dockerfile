# ===== Stage 1: Build the application =====
FROM openjdk:17-jdk-slim as builder

# Install Python and required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY mvnw pom.xml ./ 
COPY .mvn .mvn 
COPY src src

RUN chmod +x ./mvnw
RUN ./mvnw clean package -DskipTests

# ===== Stage 2: Run the application =====
FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy the application JAR file into the container
COPY --from=builder /app/target/*.jar app.jar

# Install Python and required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Ensure Python dependencies are installed
COPY src/main/resources/python/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Python scripts and make them executable
COPY src/main/resources/python/ src/main/resources/python/
RUN chmod +x src/main/resources/python/*.py

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar", "--server.port=${PORT}"]
