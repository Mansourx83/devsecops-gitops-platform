# Use a lightweight Eclipse Temurin Java 17 JRE image based on Alpine Linux
FROM eclipse-temurin:17-jre-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the built JAR file from the target directory and rename it to app.jar
COPY target/*.jar app.jar

# Expose the port that the application listens on
EXPOSE 8080

# Define the default command to run the application when the container starts
ENTRYPOINT ["java", "-jar", "app.jar"]