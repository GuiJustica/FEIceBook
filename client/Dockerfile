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

# ../client-python/Dockerfile
FROM python:3.9

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos do cliente para o contêiner
COPY . .

# Instale as dependências
RUN pip install -r requirements.txt

# Comando para executar o cliente
CMD ["python3", "cliente.py"]
