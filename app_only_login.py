from typing import List
from flask_openapi3 import OpenAPI, Info, Tag
from flask import Flask, redirect, request, session
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session
from logger import logger
from model.bop import BOP
from model.preventor import Preventor
from model.usuario import Usuario
from model.valvula import Valvula
from schemas import *
from flask_cors import CORS

from schemas.bop import BOPBuscaSchema, BOPViewSchema, ListagemBOPsSchema, apresenta_bop, apresenta_bops
from schemas.preventor import PreventorSchema, apresenta_preventores
from schemas.usuario import UsuarioLoginSchema, UsuarioSchema, UsuarioViewSchema, apresenta_usuario
from schemas.valvula import ValvulaSchema, apresenta_valvulas

app = Flask(__name__)
app.secret_key = 'secret_key'
CORS(app, supports_credentials=True)
app.config.update(
    PERMANENT_SESSION_LIFETIME=600
)

@app.route('/login', methods=['POST'])
def login():
        email = request.form["email"]
        senha = request.form["senha"]
        
        session_db = Session()
        usuario = session_db.query(Usuario).filter_by(email=email).first()
        
        if usuario and usuario.checa_senha(senha):
            session.clear()
            # cria e guarda os dados do usuário em variável de sessão para uso posterior
            session["nome"] = usuario.nome
            session["email"] = usuario.email
            session.permanent = True
            print(session)
            return apresenta_usuario(usuario), 200
        else:
            # caso um erro fora do previsto
            error_msg = "Senha ou email não encontrado no sistema :/"
            logger.warning(f"Erro ao buscar o usuário '{email}', {error_msg}")
            return {"message": error_msg}, 400

@app.route('/secao', methods=['GET'])
def get_dado_secao():
    print(session)
    if "email" in session:
        session_db = Session()
        usuario = session_db.query(Usuario).filter_by(email=session['email']).first()
        return apresenta_usuario(usuario), 200
    else:
        return apresenta_usuario(Usuario('Chico','c@c.com','123')), 400