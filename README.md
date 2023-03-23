Projeto: Consumo de APIs CEP e Previsão de Tempo

Tecnologias Utilizadas:

- Docker;
- MongoDB;
- Python;
- Flask;
- Postman;
- Swagger;
- Bibliotecas.

Utilização:

1 - Clone o repositório:

```
git clone https://github.com/lucianonevesln/docker-python-mongodb-elasticsearch-swagger.git
```

2 - Execute o comando a seguir, na raiz do projeto (onde encontra-se o arquivo docker-compose.yml):

```
docker-compose up --build
```

3 - Caso deseje refazer o processo anterior, execute o comando a seguir e volte ao passo 2:

```
docker-compose down --volumes
```

4 - Com os containeres em execução, siga para o link abaixo:

http://0.0.0.0:5000/docs/#/

5 - Abra a opção "createUser", pressione o botão "Try it out" e execute o json disponibilizado como exemplo.

6 - A opção de "login" não está funcionando corretamente no Swagger, mas você pode testá-la no Postman, com o método GET e o json abaixo:

```
{
  "email": "john@email.com",
  "password": "12345"
}
```

7 - Agora, você já pode se dirigir para a opção "busca-cep-previsao-tempo-quatro-dias", pressionar o botão "Try it out", digitar um número de CEP válido e executar. A aplicação deve retornar um json com dados do endereço do CEP e a previsão do tempo para 4 dias.
OBS: pode haver problemas na consulta de alguns CEP, cujo diagnóstico (bug) não foi identificado. Segue alguns exemplos de CEP que funcionarão corretamente:

- 01001000;
- 05001000;
- 29032145;
- 69900001;
- 70722500;

Fim.
