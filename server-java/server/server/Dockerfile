

# ../server-java/Dockerfile
# Etapa 1: Construir o JAR
FROM maven:3.8.8-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package

# Etapa 2: Executar o JAR
FROM openjdk:17
WORKDIR /app
COPY --from=build /app/target/server-0.0.1-SNAPSHOT.jar server.jar
#CMD ["java", "-jar", "server.jar"]


