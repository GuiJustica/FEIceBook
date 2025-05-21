# broker-js/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copia o package.json e o package-lock.json (se existir)
COPY package*.json ./

# Instala só as dependências necessárias
RUN npm install --production

# Copia o código da aplicação
COPY index.js .

# Comando que inicia o broker
CMD ["node", "index.js"]
