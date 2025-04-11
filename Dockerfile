FROM openjdk:17-jdk-slim

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip maven && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Build the Spring Boot application
RUN mvn clean package

# Copy the built JAR file
COPY target/backend-springboot-0.0.1-SNAPSHOT.jar app.jar

# Install Python dependencies
RUN pip3 install diffusers torch psutil

# Expose port
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]