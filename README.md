# Rede Social FEIBOOK 

## Pré requisitos para rodar o programa

###  [Docker](https://www.docker.com/)
### [NodeJS](https://nodejs.org/pt/download/current)


## Passo a passo de como rodar:

### 1.  Abrir o docker
```
cd /caminho/para/projeto-dist/infra
docker-compose up -d --build rabbitmq broker-js
docker-compose logs -f broker-js
```
Se for a segunda vez tentando abrir o docker, será necessário fechar o antigo
```
docker-compose down
```

### 2. Abrir o servidor 
```
cd /caminho/para/projeto-dist/server-java/server/server/src/main/java/com/redesocial/server
java ServerApplication
```
### 3. Abrir os clients
```
cd /caminho/para/projeto-dist/client
python3 cliente.py
```

