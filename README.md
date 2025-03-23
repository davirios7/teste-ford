
# Teste-Ford-Davi

Esse é o teste técnico para a vaga de Desenvolvedor Back-end Python (Nível Entry Level) na Ford


## Instalação do projeto

OBS: Será necessário ter o Docker instalado em sua máquina para rodar o projeto, caso não tenha, segue o link:

```http
  https://www.docker.com/products/docker-desktop/
```

Primeiro, baixe o repositório do projeto em sua máquina:
```http
  https://github.com/davirios7/teste-ford.git
```

Abra o repositório e instale o projeto:
```http
  cd teste-ford
  docker-compose up --build
```

Após isso, o banco automaticamente criado e povoado com o script de dados ficticios e a API será iniciada.
## Documentação da API

#### A Documentação foi gerada automaticamente pelo FastApi com Swagger, pode ser encontrada em

```http
  GET /docs
```


## Estratégia de segurança utilizada:

Nesse projeto, foi utilizado a criptografia das senhas dos usuários "bcrypt", também foi utilizado a segurança por validação de autenticação nas rotas utilizando JWT.

(Eu sei que a .env tá no github mas é porquê não sabia como mandar ela para o avaliador kk)