# Bibliotecas
import xmltodict
from flask import Flask, jsonify, request, Response
import requests
from pymongo import MongoClient
from flask_cors import CORS 
from bson import ObjectId
import json
import jwt
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from functools import wraps
from flask_swagger_ui import get_swaggerui_blueprint


# Configurações Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
secret = "***************"


# Credenciais de banco de dados
mongo = MongoClient(host='10.5.0.5', port=27017)
# Nome do banco de dados criado
db = mongo['database']


# Configurações do SWAGGER
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Test application"
    },
)
app.register_blueprint(swaggerui_blueprint)


# Criação de token
def tokenReq(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
            try:
                jwt.decode(token, secret)
            except:
                return jsonify({"status": "fail", "message": "unauthorized"}), 401
            return f(*args, **kwargs)
        else:
            return jsonify({"status": "fail", "message": "unauthorized"}), 401
    return decorated


# Rota inicial (sem mapeamento no Swagger)
@app.route('/')
def func():
    return "Serviço de consumo das API's: CEP e Previsão de Tempo", 200


# Criação de usuário
@app.route('/createUser', methods=['POST'])
def save_user():
    message = ""
    code = 500
    status = "fail"
    try:
        data = request.get_json()
        check = db['users'].find({"email": data['email']})
        if check.count() >= 1:
            message = "user with that email exists"
            code = 401
            status = "fail"
        else:
            # hashing the password so it's not stored in the db as it was 
            data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            data['created'] = datetime.now()

            #this is bad practice since the data is not being checked before insert
            res = db["users"].insert_one(data) 
            if res.acknowledged:
                status = "successful"
                message = "user created successfully"
                code = 201
    except Exception as ex:
        message = f"{ex}"
        status = "fail"
        code = 500
    return jsonify({'status': status, "message": message}), 200


# Login de usuário
@app.route('/login', methods=['GET'])
def login():
    message = ""
    res_data = {}
    code = 500
    status = "fail"
    try:
        data = request.get_json()
        user = db['users'].find_one({"email": f'{data["email"]}'})

        if user:
            user['_id'] = str(user['_id'])
            if user and bcrypt.check_password_hash(user['password'], data['password']):
                time = datetime.utcnow() + timedelta(hours=24)
                token = jwt.encode({
                        "user": {
                            "email": f"{user['email']}",
                            "id": f"{user['_id']}",
                        },
                        "exp": time
                    },secret)

                del user['password']

                message = f"user authenticated"
                code = 200
                status = "successful"
                res_data['token'] = token.decode('utf-8')
                res_data['user'] = user

            else:
                message = "wrong password"
                code = 401
                status = "fail"
        else:
            message = "invalid login details"
            code = 401
            status = "fail"

    except Exception as ex:
        message = f"{ex}"
        code = 500
        status = "fail"
    return jsonify({'status': status, "data": res_data, "message":message}), code


# Rota para consultar CEP e retornar dados de endereço com previsão do tempo
@app.route('/busca-cep-previsao-tempo-quatro-dias/<cep>', methods=['GET'])
def busca_cep(cep):
    print(cep)
    # Busca a partir de cep digitado na URL.
    url = f"https://viacep.com.br/ws/{cep}/json/"
    cep_resultado = requests.get(url)
    cep_resultado = cep_resultado.json()
    cidade = cep_resultado['localidade']
    # Script a ser melhora em função da repetição (testar com regex futuramente).
    cidade = cidade.replace('ã', 'a')
    cidade = cidade.replace('á', 'a')
    cidade = cidade.replace('à', 'a')
    cidade = cidade.replace('é', 'e')
    cidade = cidade.replace('í', 'i')
    cidade = cidade.replace('ó', 'o')
    cidade = cidade.replace('õ', 'o')
    cidade = cidade.replace('ú', 'u')
    cidade = cidade.replace('ç', 'c')
    cidade = cidade.lower()
    uf = cep_resultado['uf']
    # Consulta para descobrir o id da cidade perante o CPTEC/INPE.
    url = f'http://servicos.cptec.inpe.br/XML/listaCidades?city={cidade}'
    id_cidade = ''
    lista_cidades = requests.get(url)
    lista_cidades = xmltodict.parse(lista_cidades.content)
    lista_cidades = lista_cidades['cidades']['cidade']
    for cidade_alvo in lista_cidades:
        if [cidade_alvo['nome'] == cidade] and [cidade_alvo['uf'] == uf]:
            id_cidade = cidade_alvo['id']
            # Consulta para retornar a previsão da temperadutura dos próximos 4 dias.
            url = f'http://servicos.cptec.inpe.br/XML/cidade/{id_cidade}/previsao.xml'
            previsoes = requests.get(url)
            previsoes = xmltodict.parse(previsoes.content)
            #previsoes = json.dumps(previsoes)
            previsoes = dict(previsoes)
            return jsonify({'Dados CEP': cep_resultado, 'Dados Previsão': previsoes})


# Configurações para inicializar app
if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)
