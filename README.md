# Rede Social FEIceBOOK 

## Autores do Projeto
* Felipe Orlando Lanzara - 24.122.055-7
* Guilherme Marcato Mendes Justiça - 24.122.045-8
* João Vitor Governatore - 24.122.027-6
* Paulo Vincius Araujo Feitosa - 24.122.042-5


## Pré requisitos para rodar o programa

### [Docker](https://www.docker.com/)
### [NodeJS](https://nodejs.org/pt/download/current)
### [Java](https://www.oracle.com/java/technologies/downloads/)
### [Python](https://www.python.org/downloads/)

## Passo a passo de como rodar:

### 1.  Abrir o docker (linux)
### Com o linux, pode ignorar o resto
```
cd /caminho/para/projeto-dist/infra
sudo docker compose up --build -d
```

### 1.1 Abrir o docker (windows)
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

### 3. Criar e abrir o ambiente virtual
```
python3 -m venv venv
```
### Ative o ambiente virtual 
* Windows
```
venv\Scripts\activate
```
* Linux/Mac
```
source venv/bin/activate
```
### Instale as bibliotecas necessárias
```
pip install -r requirements.txt
```


### 3. Abrir os clients
```
cd /caminho/para/projeto-dist/client
python3 cliente.py
```

