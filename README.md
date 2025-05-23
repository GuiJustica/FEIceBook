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
### Antes de iniciar o projeto será necessário incluir o arquivo ```.env``` na pasta ```client``` do projeto. Caminho até o diretório: ```cd /client```.

Formato do arquivo ```.env``` que deverá ser criado:

![Formato .env](https://cdn.discordapp.com/attachments/1372327706980651028/1375306552935845942/image.png?ex=6831358a&is=682fe40a&hm=737ac7936cb6a8ae20efc81406da8bc537a9f79ccffaca688b5c9d200507225c&)
> ### Observação:  
> Banco de dados ```CockroachDB```

## Passo a passo de como rodar o projeto:

Para executar o nosso projeto, qpor ele utilizar uma interface gráfica desenvolvida com ```Tkinter``` (biblioteca nativa do Python), é necessário rodá-lo em um ambiente ```Linux``` ou, alternativamente, em um terminal ```WSL``` (Windows Subsystem for Linux) que simule um ambiente Linux.


### 1.  Acesse o diretório do projeto onde se encontra o arquivo ```docker-compose.yml```:
```cd infra```

### 2. Habilite o acesso gráfico para os containers ```Docker``` com o comando:
```xhost +local:docker```

### 3. Execute o Docker Compose para iniciar os serviços e instalar as dependências automaticamente:
```sudo docker compose up --build```

### Para executar o programa no ```WSL``` apenas entre na pasta ```ìnfra``` e execute o comando: ```sudo docker compose up --build```. 

> ### Observação:  
> Após a primeira execução (com `--build`), caso deseje rodar o projeto novamente, basta utilizar o comando:
> ```sudo docker-compose up```
---

# Explicação do funcionamento do projeto
Ao iniciar o projeto, o Docker carregará todos os containers, criando automaticamente cinco clientes e três servidores:
![clientes](https://cdn.discordapp.com/attachments/1372327706980651028/1375517572056743986/image.png?ex=6831fa11&is=6830a891&hm=d588b80992cb42e55c8507f381b59a4e8b93e2c8250cae5c9aed519dc3c4eacd&)
![servidores](https://cdn.discordapp.com/attachments/1372327706980651028/1375518225449615420/image.png?ex=6831faac&is=6830a92c&hm=02f8e6310ee20bd140dc6c55ef25a46e868d27e596391fbc5fe948c0fb4f1877&)
