# ===== Stage 1: Build the application ======
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

# Install Python and required system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Ensure Python dependencies are installed
COPY src/main/resources/python/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# ✅ Download the spaCy model 'en_core_web_sm'
RUN python -m spacy download en_core_web_sm

# Copy Python scripts and make them executable
COPY src/main/resources/python/ src/main/resources/python/
RUN chmod +x src/main/resources/python/*.py

# Create model directory with proper permissions
RUN mkdir -p /app/src/main/resources/python/model && \
    chmod -R 777 /app/src/main/resources/python/model

# Ensure the application listens on port 80
ENV PORT=80

EXPOSE 80

# Update the ENTRYPOINT to pass the port explicitly
ENTRYPOINT ["java", "-jar", "app.jar", "--server.port=80"]