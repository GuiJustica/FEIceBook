# # broker-js/Dockerfile
# FROM node:16

# WORKDIR /app

# COPY . .

# RUN npm install

# CMD ["node", "index.js"] # Ajuste conforme o nome do arquivo principal

# # ../server-java/Dockerfile
# FROM openjdk:17
# WORKDIR /app
# COPY . .
# CMD ["java", "-jar", "server.jar"] # Ajuste conforme o nome do JAR

# # ../client-python/Dockerfile
# FROM python:3.9
# WORKDIR /app
# COPY . .
# RUN pip install -r requirements.txt
# CMD ["python", "cliente.py"] # Ajuste conforme o nome do script

# Use uma imagem base leve
FROM ubuntu:22.04

# Instale dependências necessárias
RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Instale dependências ou copie arquivos necessários
RUN apt-get update && apt-get install -y x11-xserver-utils

# Defina o diretório de trabalho
WORKDIR /app

# Comando para manter o contêiner ativo
CMD ["tail", "-f", "/dev/null"]

