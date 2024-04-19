# Minha API

Este pequeno projeto faz parte da entrega do MVP da disciplina: Desenvolvimento Full Stack Básico cursada na Pós-Graduação em Engenharia de Software da PUC-RJ

O projeto é uma aplicação web chamada BOP Land onde um usuário pode logar, criar, salvar e visualizar BOP's de forma simples e interativa. Como contexto de negócio o BOP (Blowout Preventer) é um equipamento de segurança de poço fundamental em intervenções em poços de petróleo. Este é composto por várias válvulas e preventores que podem ser fechadas para vedar, controlar e monitorar poços de petróleo e gás para evitar explosões, a liberação descontrolada de petróleo bruto ou gás natural de um poço.

---
## Como executar 


Será necessário ter todas as libs python listadas no `requirements.txt` instaladas. A versão do python utilizada foi 3.10.12.

Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.


> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

```
(env)$ pip install -r requirements.txt
```

Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

É necessário criar um arquivo `.env` com a chave `JWT_SECRET_KEY` e uma senha a sua escolha que será utilizada no jwt token
```
JWT_SECRET_KEY = 'your_secret_key'
```

Para executar a API  basta executar:

```
(env)$ flask run --host 0.0.0.0 --port 5000
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor
automaticamente após uma mudança no código fonte. 

```
(env)$ flask run --host 0.0.0.0 --port 5000 --reload
```

Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API em execução.

Para realizar qualquer chamada a API pelo swagger é necessário incluir o token no campo Authorize. Dessa forma, deve-se acessar o endpoint : `/auth/login/`, conforme imagem abaixo e utilizando as seguintes credenciais:
```
email: admin@admin.com
senha: 12345
```
![alt text](image-1.png)

O token se encontra na resposta do login como valor da chave access_token, neste caso do print: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxMzU0NTI2NywianRpIjoiYmI2MmVkYTctMWFiOS00NzIzLTg2YjMtNjBkYWU5ZTc4YmQwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluQGFkbWluLmNvbSIsIm5iZiI6MTcxMzU0NTI2NywiY3NyZiI6ImZmY2MwMTk5LTU0ZWItNDM1NS1iNTA5LTI2NTlhZmQ1YWE3YyIsImV4cCI6MTcxMzU4MTI2N30.M4JgHKOfcjkOGwjLg-jOXaUomkXOr2mhNv1lxoSfxhA`

Basta colá-lo no authorizations e voilá.
![alt text](image-2.png)