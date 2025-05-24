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
### Antes de iniciar o projeto será necessário incluir o arquivo ```.env``` na pasta ```client``` do projeto e criar um database no ```CockroachDB``` . Caminho até o diretório: ```cd /client```.

Formato do arquivo ```.env``` que deverá ser criado:

![Formato .env](https://cdn.discordapp.com/attachments/1372327706980651028/1375306552935845942/image.png?ex=6831358a&is=682fe40a&hm=737ac7936cb6a8ae20efc81406da8bc537a9f79ccffaca688b5c9d200507225c&)

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
Sempre que um ```post``` for realizado, um usuário for ```seguido``` ou uma ```mensagem privada``` for enviada, a ação será exibida tanto na ```interface gráfica``` quanto nos ```servidores``` e no ```broker```. Os servidores receberão a notificação, seguindo a ordem de inicialização — neste caso, o servidor 1 receberá primeiro, seguido pelo servidor 3 e, por último, pelo servidor 2.

Ao iniciar o projeto, o Docker carregará todos os containers, criando automaticamente cinco clientes e três servidores:
![clientes](https://cdn.discordapp.com/attachments/1372327706980651028/1375517572056743986/image.png?ex=6831fa11&is=6830a891&hm=d588b80992cb42e55c8507f381b59a4e8b93e2c8250cae5c9aed519dc3c4eacd&)
![servidores](https://cdn.discordapp.com/attachments/1372327706980651028/1375518225449615420/image.png?ex=6831faac&is=6830a92c&hm=02f8e6310ee20bd140dc6c55ef25a46e868d27e596391fbc5fe948c0fb4f1877&)

### Cadastro dos usuários:
Apenas será realizado o cadastro do usuário ao preencher o ```Usuário```, ```Senha``` e ```Confirmar Senha```. O ```usuário``` deve ser único.

Tentando realizar o cadastro sem o preenchimento de nenhuma informação:

![Cadastro sem nada](https://cdn.discordapp.com/attachments/1372327706980651028/1375519001681072189/image.png?ex=6831fb65&is=6830a9e5&hm=1f1daf930cd00259886334279fa8d5c32e62cc395571b5db0701666d2ec2015b&)

Cadastro com as senhas não coincidindo:

![Cadastro usuário senhas não coincidindo](https://cdn.discordapp.com/attachments/1372327706980651028/1375535350642114572/image.png?ex=68320a9f&is=6830b91f&hm=b695281701343ab7cbf530387b9526e16cd1e2bc01f5ea2f95a3d63ed1ceea62&)

Cadastro com todas as informações preenchidas:

![Cadastro correto](https://cdn.discordapp.com/attachments/1372327706980651028/1375519277372805291/image.png?ex=6831fba7&is=6830aa27&hm=b03e2ac14d52732807fbff8cb1b849c1794eac51d6c5638ca11a51b2aad71436&)

Cadastro com o usuário já criado:

![Cadastro usuário já cadastrado](https://cdn.discordapp.com/attachments/1372327706980651028/1375520417380306955/image.png?ex=6831fcb7&is=6830ab37&hm=f607de3b7b957c6ebeefeaafc3f796756fbdd61227ca05265202fe54c3cbebb2&)

Após o cadastro do usuário será salvo suas informações no banco de dados ```CockroachDB```, com a seguinte tabela ```usuario```:

![Banco de dados cadastro](https://cdn.discordapp.com/attachments/1372327706980651028/1375519600443396167/image.png?ex=6831fbf4&is=6830aa74&hm=17e404e5e9741febc06849c6f813aa8e384192dcda10b2f6351fe1ef1047b462&)

Você será redirecionado para a tela de ```login```, onde será necessário preencher os dados cadastrados anteriormente.


Tentativa de Login com o usuário não cadastrado:

![Loguin não cadastrado](https://cdn.discordapp.com/attachments/1372327706980651028/1375521274154979430/image.png?ex=6831fd83&is=6830ac03&hm=955115d25ec4f6d027379c65a4e078aa8b2c2e6bd67605e8432139450d4be94f&)

Login com usuário cadastrado:

![Loguin correto](https://cdn.discordapp.com/attachments/1372327706980651028/1375521650472255758/image.png?ex=6831fddd&is=6830ac5d&hm=c89cf7527ba396fa22fc24cbe3e6207754d6955718e15992aaa57ef46776a9a2&)

Após o login, o usuário será redirecionado para a tela de ```Postar```:

![Redirecionamento](https://cdn.discordapp.com/attachments/1372327706980651028/1375522008825335848/image.png?ex=6831fe32&is=6830acb2&hm=5fa20d367097ef2d0da4229d3f44c9036c3fa57f0a8121c1604b1cd336d33b55&)

Ao postar alguma mensagem, aparecerá essa mensagem no canto ao lado, e todas as pessoas que estão seguindo esse usuário poderão visualizar esse post: 

![Post](https://cdn.discordapp.com/attachments/1372327706980651028/1375523082516566107/image.png?ex=6831ff32&is=6830adb2&hm=23df535cd931cdb66b47c53c872aeabddc07f46e57124c877c1d12e7d1cae642&)

> ### Atenção!!
> Para verificar que os posts estão sendo atualizadas, é necessário clicar novamente no botão de ```postar```!

> ### Observação:  
> Criei outra conta com o usuário ```felipe``` para mostrar o funcionamento do seguir

### Seguir

![Post](https://cdn.discordapp.com/attachments/1372327706980651028/1375524073517351033/image.png?ex=6832001f&is=6830ae9f&hm=7f3b67356ba2c76a1a137abd76ab279e8bf8bb2ff19f1532471d322dde50962d&)

O usuário ```felipe``` ao seguir o ```joao```, ao clicar na aba de Postar recebeu todos os posts do ```joao```:

![Post recebido do joao](https://cdn.discordapp.com/attachments/1372327706980651028/1375524357689970839/image.png?ex=68320062&is=6830aee2&hm=f9c06e7b8b5af00b90ef5276bcca52929674f164b2ebb274c854f20bd0cd2f53&)

Fiz outro post com o ```felipe```, porém como o ```joao``` não está seguindo o ```felipe```, ele não receberá:

![Post felipe](https://cdn.discordapp.com/attachments/1372327706980651028/1375525015260233758/image.png?ex=683200ff&is=6830af7f&hm=6afbcdf94675417566aae6905c76624fd81958fb576892a3a935ebf5f5b3a32a&)

No banco de dados os posts e seguidores ficarão assim:

![banco de dados seguidores e posts](https://cdn.discordapp.com/attachments/1372327706980651028/1375525845736755394/image.png?ex=683201c5&is=6830b045&hm=2149ce9e40402d55c656ce10def28430af035932febdea17f27dacef9ccdc05e&)


### Para conseguir enviar ```mensagens privadas```, é necessário que ambos os usuários estejam se seguindo, portando fiz o ```joao``` seguir o ```felipe```:

![banco de dados seguidores e posts](https://cdn.discordapp.com/attachments/1372327706980651028/1375527086147768410/image.png?ex=683202ed&is=6830b16d&hm=5c4216cb99a745758da952785bbd85d37a65993ee451f935dda37d71a2cfbd45&)

Banco de Dados atualizado:

![banco de dados atualizado](https://cdn.discordapp.com/attachments/1372327706980651028/1375527800785731635/image.png?ex=68320397&is=6830b217&hm=211f28e1273ee66863d3c861369a5bd32cab8e6ad7c3528554a709596209efe0&)

### ```joao``` enviando mensagem privada para o ```felipe```:

![mensagem privada joao](https://cdn.discordapp.com/attachments/1372327706980651028/1375528511837573272/image.png?ex=68320441&is=6830b2c1&hm=0fc0405db7c6646c37735a3cedb2a8efb15786f83e42d8a1bbe1c9fafc65ec81&)

### ```felipe``` enviando mensagem para o ```joao```

![mensagem privada felipe](https://cdn.discordapp.com/attachments/1372327706980651028/1375529689946259577/image.png?ex=6832055a&is=6830b3da&hm=0492f71725c7810add2f9d22e0a8308eeb35553056f6b619512c11b3f2920fd5&)

> ### Atenção!!
> Para verificar que as mensagens privadas estão sendo atualizadas, é necessário clicar novamente no botão de ```mensagens privadas``` e clicar na caixa de seleção do usuário que deseja conversar!

Banco de dados atualizado com as ```mensagens privadas```:

![Banco de dados mensagens privadas](https://cdn.discordapp.com/attachments/1372327706980651028/1375530151047331930/image.png?ex=683205c8&is=6830b448&hm=aeb7edba95548d464b561c24826bf546827bf8a8a6815df95b1bfa409df826f3&)

### Atualização de Relógio Lógico (Lamport)

Na imagem você vê que, a cada post recebido pelo RabbitMQ, o servidor pega o timestamp que veio na mensagem (1, depois 3, depois 5) e faz ```clock_local = max(clock_local, ts_remoto) + 1```. Então, se antes o relógio local era 0, ao receber 1 vira 2; ao receber 3 vira 4; ao receber 5 vira 6. Isso garante que, mesmo em vários servidores, os eventos fiquem sempre ordenados de forma causal.

![Atualização de Relógio Lógico (Lamport)](https://cdn.discordapp.com/attachments/973374566879625216/1375632974485393518/image.png?ex=6832658b&is=6831140b&hm=135f5ec84a0d2f9d3c802e217572039ebcc05da44109e0117ea9c9a6624d07be&)

### Sincronização do Relógio Berkeley

Neste caso, quando o usuário joao enviou um post, aparece que foi aplicado um adiantamento no tempo (30% de chance de ocorrer). O servidor 1, que foi o responsável por esse post recebe esse adiantamento como é possível ver, já que seu horário adiantou 1 minuto. No entanto, logo abaixo ele informa que recebeu esse tempo a mais e já sincronizou para corrigir o horário. É possível verificar que o horário for concertado, pois depois de 10 segundos esse mesmo servidor alerta que não houve mais problemas com o horário e já mostra o horário corrigido.

![Sincronização do Relógio Berkeley](https://cdn.discordapp.com/attachments/973374566879625216/1375629269392425042/image.png?ex=68326217&is=68311097&hm=40d381f8ebb2c28cf424a8a66c4e7fb9fbc033c5cea4743c2d020a3a6482303a&)

### Criação do arquivo .log

Esse arquivo .log vai conter tudo que acontece em nossa aplicação como: Criação de uma nova conta, login, enviar uma mensagem privada, postar algo, seguir alguém ou qualquer erro que ocorra como falha ao logar por conta de nome ou senha incorretos. O arquivo esta no caminho a seguir: ```./client/logs```. E o nome do arquivo é ```client-python.log```.

![Sincronização do Relógio Berkeley](https://cdn.discordapp.com/attachments/973374566879625216/1375635289225039942/image.png?ex=683267b3&is=68311633&hm=3bcb6d4d71ded62f2feb7295006ce67c1113550d5f277e77f12da59fdc8174c1&)

---

