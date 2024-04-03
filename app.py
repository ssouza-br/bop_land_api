from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect

from model import Session
from logger import logger

from model.preventor import Preventor
from model.valvula import Valvula
from schemas import *
from flask_cors import CORS

from flask_jwt_extended import JWTManager

from schemas.preventor import apresenta_preventores
from schemas.valvula import apresenta_valvulas

from blueprints import auth
from blueprints import bop

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.secret_key = 'secret_key'
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!

CORS(app)
jwt = JWTManager(app)

# registrando a blueprint de autenticação
app.register_api(auth.bp)

# registrando a blueprint do bop
app.register_api(bop.bp)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
valvula_tag = Tag(name="Valvula", description="Adição de uma válvula a um BOP cadastrado na base")
preventor_tag = Tag(name="Preventor", description="Adição de um preventor a um BOP cadastrado na base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.get('/valvulas', tags=[valvula_tag])
def get_valvulas():
    """Faz a busca por todas  as válvulas já cadastradas

    Retorna uma representação da listagem de Válvulas.
    """
    logger.debug(f"Coletando Válvulas ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    valvulas = session.query(Valvula.acronimo).distinct().all()

    if not valvulas:
        # se não há valvulas cadastrados
        return {"valvulas": []}, 200
    else:
        logger.debug(f"%d Válvulas encontradas" % len(valvulas))
        # retorna a representação de BOP
        return apresenta_valvulas(valvulas), 200
    
@app.get('/preventores', tags=[preventor_tag])
def get_preventores():
    """Faz a busca por todas os preventores já cadastrados

    Retorna uma representação da listagem de Preventores.
    """
    logger.debug(f"Coletando Preventores ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    preventores = session.query(Preventor.acronimo).distinct().all()

    if not preventores:
        # se não há preventores cadastrados
        return {"preventores": []}, 200
    else:
        logger.debug(f"%d Válvulas encontradas" % len(preventores))
        # retorna a representação de BOP
        return apresenta_preventores(preventores), 200