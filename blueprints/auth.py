
import datetime
from sqlalchemy import exc
from venv import logger
from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_openapi3 import APIBlueprint, Tag

from model import Session
from model.usuario import Usuario
from schemas.error import ErrorSchema
from schemas.usuario import UsuarioLoginSchema, UsuarioSchema, UsuarioViewSchema, apresenta_usuario

usuario_tag = Tag(name="Usuario", description="Adição, visualização e remoção de usuários à base")
security = [{"jwt": []}]

bp = APIBlueprint(
    'auth',
    __name__, 
    url_prefix='/auth', 
    abp_tags=[usuario_tag],
    abp_security=security, 
    abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
    doc_ui=True )

@bp.post('/register', responses={"200": UsuarioViewSchema})
def cadastro_usuario(form: UsuarioSchema):
        nome = form.nome
        email = form.email
        senha = form.senha

        novo_usuario = Usuario(nome=nome,email=email,senha=senha)
        
        try:
            # criando conexão com a base
            session = Session()
            # adicionando bop
            session.add(novo_usuario)
            # efetivando o camando de adição de novo item na tabela
            session.commit()
            logger.debug(f"Adicionado usuário: '{novo_usuario.email}'")
            return apresenta_usuario(novo_usuario), 200

        except exc.IntegrityError:
            session.rollback()
            # como a duplicidade do nome é a provável razão do IntegrityError
            error_msg = "Usuário já cadastrado com esse email :/"
            logger.warning(f"Erro ao adicionar usuário '{novo_usuario.email}', {error_msg}")
            return {"mensagem": error_msg}, 409

        except Exception:
            # caso um erro fora do previsto
            error_msg = "Não foi possível salvar novo usuário :/"
            logger.warning(f"Erro ao adicionar usuário '{novo_usuario.email}', {error_msg}")
            return {"mensagem": error_msg}, 400

@bp.post('/login', responses={"200": UsuarioViewSchema})
def login(form: UsuarioLoginSchema):
        email = form.email
        senha = form.senha
        
        session = Session()
        usuario = session.query(Usuario).filter_by(email=email).first()
        
        if usuario and usuario.checa_senha(senha):
            # cria e guarda os dados do usuário em variável de sessão para uso posterior
            access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(minutes=5))
            # return apresenta_usuario(usuario), 200
            return jsonify(access_token=access_token)
        else:
            # caso um erro fora do previsto
            error_msg = "Senha ou email não encontrado no sistema :/"
            logger.warning(f"Erro ao buscar o usuário '{email}', {error_msg}")
            return {"mensagem": error_msg}, 400

@bp.get('/quemeusou',responses={"200": UsuarioViewSchema})
@jwt_required()
def get_dado_secao():
    current_user = get_jwt_identity()
    if current_user:
        session = Session()
        usuario = session.query(Usuario).filter_by(email=current_user).first()
        return apresenta_usuario(usuario), 200