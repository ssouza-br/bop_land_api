import os
from dotenv import load_dotenv
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect

from schemas import *
from flask_cors import CORS

from flask_jwt_extended import JWTManager

from blueprints import auth
from blueprints import bop
from blueprints import valvula
from blueprints import preventor

# JWT Bearer Sample
jwt = {
  "type": "http",
  "scheme": "bearer",
  "bearerFormat": "JWT"
}

security_schemes = {"jwt": jwt}

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

# carregando os dados do .env
load_dotenv()
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# usado somente com cookies
# app.config['JWT_TOKEN_LOCATION'] = os.getenv('JWT_TOKEN_LOCATION')
# app.config['JWT_COOKIE_SECURE'] = os.getenv('JWT_COOKIE_SECURE')
# app.config['JWT_COOKIE_CSRF_PROTECT'] = os.getenv('JWT_COOKIE_CSRF_PROTECT')

CORS(app, supports_credentials=True)
jwt = JWTManager(app)

# registrando a blueprint de autenticação
app.register_api(auth.bp)

# registrando a blueprint do bop
app.register_api(bop.bp)

# registrando a blueprint da válvula
app.register_api(valvula.bp)

# registrando a blueprint de preventor
app.register_api(preventor.bp)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')