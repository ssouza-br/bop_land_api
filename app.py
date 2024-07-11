import os
from dotenv import load_dotenv
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, g

from schemas import *
from flask_cors import CORS

from flask_jwt_extended import JWTManager

from blueprints import auth
from blueprints import bop
from blueprints import valvula
from blueprints import preventor
from blueprints import teste
from models import Session

# JWT Bearer Sample
jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}

api_key = {"type": "apiKey", "name": "acess_token", "in": "cookie"}

# security_schemes = {"jwt": jwt, "api_key": api_key}
security_schemes = {"api_key": api_key}

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

# carregando os dados do .env
load_dotenv()
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# usado somente com cookies
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"

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

# registrando a blueprint de teste
app.register_api(teste.bp)


@app.before_request
def before_request():
    g.session = Session()


@app.teardown_request
def teardown_request(exception=None):
    if hasattr(g, "session"):
        # g.session.remove()
        pass


# definindo tags
home_tag = Tag(
    name="Documentação",
    description="Seleção de documentação: Swagger, Redoc ou RapiDoc",
)


@app.get("/", tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")
