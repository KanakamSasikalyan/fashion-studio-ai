# Use an official OpenJDK runtime as a parent image
FROM openjdk:17-jdk-slim

# Install Python and required dependencies (just in case your app uses it for some reason)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the Maven wrapper and pom.xml to the container
COPY mvnw pom.xml . 
COPY .mvn .mvn

# Grant executable permissions to the mvnw script
RUN chmod +x ./mvnw

# Fetch Maven dependencies
RUN ./mvnw dependency:resolve

# Copy the project source code to the container
COPY src src

# Build the application and skip tests (but ensure a proper exit status for the build)
RUN ./mvnw package -DskipTests

# Ensure target directory is created (it should be created by the build, but it's good practice to explicitly handle it)
RUN mkdir -p target

# Copy any JAR file from the target directory to the container as app.jar
# This will ensure the target directory exists and contains a JAR file
COPY target/*.jar app.jar

# Expose the port the app runs on
EXPOSE 8080

# Set the entry point to run the Spring Boot application
ENTRYPOINT ["java", "-jar", "app.jar"]
