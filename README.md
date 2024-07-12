# BOP Land - Backend

Este pequeno projeto faz parte da entrega do MVP da disciplina: Arquitetura de Software cursada na Pós-Graduação em Engenharia de Software da PUC-RJ

O projeto é uma aplicação web chamada BOP Land onde um usuário pode logar, criar e aprovar testes de BOP de forma simples e interativa. Como contexto de negócio o BOP (Blowout Preventer) é um equipamento de segurança de poço fundamental em intervenções em poços de petróleo. Este é composto por várias válvulas e preventores que podem ser fechadas para vedar, controlar e monitorar poços de petróleo. O teste completo desse equipamento é fundamental para garantia de seu funcionamento e vedação.

Visando auxiliar na tomada de decisão para aprovação do teste, foi feito um acesso a uma API externa do CPTEC-INPE com a previsão do tempo nos próximos 7 dias baseado na locação onde o BOP está instalado. Esta API está disponível de forma gratuita e sem chave de acesso através de [http://servicos.cptec.inpe.br/XML/#req-previsao-7-dias](http://servicos.cptec.inpe.br/XML/#req-previsao-7-dias)

O objetivo aqui é apresentar uma API emplementada seguindo o estilo REST.

As principais tecnologias que serão utilizadas aqui são:

- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [OpenAPI3](https://swagger.io/specification/)
- [SQLite](https://www.sqlite.org/index.html)
- [Pytest](https://docs.pytest.org/en/8.2.x/)

---

## Como executar o back

Será necessário ter o [Docker](https://www.docker.com/) instalado.

Após clonar o repositório, é necessário ir ao diretório raiz desse projeto pelo terminal criar um arquivo `.env` com a chave `JWT_SECRET_KEY` e uma senha a sua escolha que será utilizada no jwt token

```
JWT_SECRET_KEY = 'your_secret_key'
```

Execute os comandos descritos abaixo.

```
docker build -t back .
```

```
docker run -p 5666:5666 back
```

Abra o [http://localhost:5666/#/](http://localhost:5666/#/) no navegador para verificar o status da API em execução.

Para realizar qualquer chamada a API pelo swagger é necessário utilizar o endpoint : `/auth/login/`, conforme imagem abaixo e utilizando as seguintes credenciais:

```
email: admin@admin.com
senha: 12345
```

![alt text](image-1.png)
