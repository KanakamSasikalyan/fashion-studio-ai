FROM openjdk:17-jdk-slim

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Spring Boot JAR and Python script
COPY target/backend-springboot-0.0.1-SNAPSHOT.jar app.jar
COPY src/main/resources/python/scripts/ scripts/

# Install Python dependencies
RUN pip3 install diffusers torch psutil

# Expose port
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]