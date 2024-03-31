from flask_openapi3 import OpenAPI, Info, Tag
from flask import jsonify, redirect
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

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from schemas.bop import BOPBuscaSchema, BOPViewSchema, ListagemBOPsSchema, apresenta_bop, apresenta_bops
from schemas.preventor import PreventorSchema, apresenta_preventores
from schemas.usuario import UsuarioLoginSchema, UsuarioSchema, UsuarioViewSchema, apresenta_usuario
from schemas.valvula import ValvulaSchema, apresenta_valvulas

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.secret_key = 'secret_key'
CORS(app)
jwt = JWTManager(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
usuario_tag = Tag(name="Usuario", description="Adição, visualização e remoção de usuários à base")
bop_tag = Tag(name="BOP", description="Adição, visualização e remoção de BOPs à base")
valvula_tag = Tag(name="Valvula", description="Adição de uma válvula a um BOP cadastrado na base")
preventor_tag = Tag(name="Preventor", description="Adição de um preventor a um BOP cadastrado na base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

###### API de usuario ####################

@app.post('/cadastro', tags=[usuario_tag],
          responses={"200": UsuarioViewSchema, "409": ErrorSchema, "400": ErrorSchema})
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

        except IntegrityError as e:
            # como a duplicidade do nome é a provável razão do IntegrityError
            error_msg = "Usuário já cadastrado com esse email :/"
            logger.warning(f"Erro ao adicionar usuário '{novo_usuario.email}', {error_msg}")
            return {"message": error_msg}, 409

        except Exception as e:
            # caso um erro fora do previsto
            error_msg = "Não foi possível salvar novo usuário :/"
            logger.warning(f"Erro ao adicionar usuário '{novo_usuario.email}', {error_msg}")
            return {"message": error_msg}, 400

@app.post('/login', tags=[usuario_tag],
          responses={"200": UsuarioViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def login(form: UsuarioLoginSchema):
        email = form.email
        senha = form.senha
        
        session = Session()
        usuario = session.query(Usuario).filter_by(email=email).first()
        
        if usuario and usuario.checa_senha(senha):
            # cria e guarda os dados do usuário em variável de sessão para uso posterior
            access_token = create_access_token(identity=email)
            # return apresenta_usuario(usuario), 200
            return jsonify(access_token=access_token)
        else:
            # caso um erro fora do previsto
            error_msg = "Senha ou email não encontrado no sistema :/"
            logger.warning(f"Erro ao buscar o usuário '{email}', {error_msg}")
            return {"message": error_msg}, 400

@app.get('/usuario', tags=[usuario_tag],
          responses={"200": UsuarioLoginSchema, "409": ErrorSchema, "400": ErrorSchema})
@jwt_required()
def get_dado_secao():
    current_user = get_jwt_identity()
    if current_user:
        session = Session()
        usuario = session.query(Usuario).filter_by(email=current_user).first()
        return apresenta_usuario(usuario), 200
              
###### IMPLEMEMENTAÇÃO NOVA##############

@app.post('/bop', tags=[bop_tag],
          responses={"200": BOPViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_bop(form: BOPViewSchema):
    """Adiciona um novo BOP a base de dados

    Retorna uma representação dos BOPs com válvulas e preventores associados.
    """
    sonda = form.sonda
    valvulas = form.valvulas
    preventores = form.preventores
    print(form)
    # criando um BOP
    bop = BOP(sonda=sonda)
    logger.debug(f"Adicionando BOP da sonda: '{bop.sonda}'")
    
    # adicionando as válvulas ao BOP criado acima
    [bop.adiciona_valvula(Valvula(v)) for v in valvulas]
    
    # adicionando os preventores ao BOP criado acima
    [bop.adiciona_preventor(Preventor(p)) for p in preventores]
    try:
        # criando conexão com a base
        session = Session()
        # adicionando bop
        session.add(bop)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado BOP da sonda: '{bop.sonda}' com válvulas e preventores")
        return apresenta_bop(bop), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "BOP dessa sonda já salvo na base :/"
        logger.warning(f"Erro ao adicionar produto '{bop.sonda}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo BOP :/"
        logger.warning(f"Erro ao adicionar BOP '{bop.sonda}', {error_msg}")
        return {"mesage": error_msg}, 400

@app.get('/bops', tags=[bop_tag],
         responses={"200": ListagemBOPsSchema, "404": ErrorSchema})
def get_bops():
    """Faz a busca por todos os BOPs cadastrados

    Retorna uma representação da listagem de BOPs.
    """
    logger.debug(f"Coletando BOPs ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    bops = session.query(BOP).all()

    if not bops:
        # se não há bops cadastrados
        return {"bops": []}, 200
    else:
        logger.debug(f"%d BOPs encontrados" % len(bops))
        # retorna a representação de BOP
        print(bops)
        return apresenta_bops(bops), 200

@app.get('/bop', tags=[bop_tag],
         responses={"200": BOPViewSchema, "404": ErrorSchema})
def get_bop(query: BOPBuscaSchema):
    """Faz a busca por um BOP do nome da sonda dona desse equipamento

    Retorna uma representação dos BOPs, válvulas e preventores associados.
    """
    bop_sonda = query.sonda
    logger.debug(f"Coletando dados sobre BOP #{bop_sonda}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    bop = session.query(BOP).filter(BOP.sonda == bop_sonda).first() 

    if not bop:
        # se o bop não foi encontrado
        error_msg = "BOP não encontrado na base :/"
        logger.warning(f"Erro ao buscar BOP '{bop_sonda}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"BOP encontrado: '{bop_sonda}'")
        # retorna a representação de bop
        return apresenta_bop(bop), 200

@app.delete('/bop', tags=[bop_tag],
         responses={"200": BOPViewSchema, "404": ErrorSchema})
def del_bop(query: BOPBuscaSchema):
    """Deleta um BOP a partir do nome da sonda dona desse equipamento

    Retorna uma mensagem de confirmação da remoção.
    """
    bop_sonda = unquote(unquote(query.sonda))
    logger.debug(f"Coletando dados sobre BOP #{bop_sonda}")
    # criando conexão com a base
    session = Session()
    
    # encontrando o bop a ser deletado
    bop_id = session.query(BOP).filter(BOP.sonda == bop_sonda).first().id
    
    # deletando as válvulas associadas ao BOP em questão
    del_valvulas(bop_id)
    # deletando os preventores associados ao BOP em questão
    del_preventores(bop_id)
    
    # deletando o bop
    bop = session.query(BOP).filter(BOP.sonda == bop_sonda).delete()
    session.commit()

    if bop:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado produto #{bop_sonda}")
        return {"mesage": "Produto removido", "id": bop_sonda}
    else:
        # se o produto não foi encontrado
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao deletar produto #'{bop_sonda}', {error_msg}")
        return {"mesage": error_msg}, 404

@app.get('/valvulas', tags=[valvula_tag],
         responses={"200": ValvulaSchema, "404": ErrorSchema})
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
    
@app.get('/preventores', tags=[preventor_tag],
         responses={"200": PreventorSchema, "404": ErrorSchema})
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

def del_valvulas(bop_id):
    session = Session()
    
    # encontrando as válvulas associadas ao BOP em questão
    valvulas = session.query(Valvula).filter(Valvula.bop_id == bop_id).all()
    
    #deletando válvula por válvula associada a esse BOP
    [session.query(Valvula).filter(Valvula.id == v.id).delete() for v in valvulas]
    session.commit()

def del_preventores(bop_id):
    session = Session()
    
    # encontrando as válvulas associadas ao BOP em questão
    preventores = session.query(Preventor).filter(Preventor.bop_id == bop_id).all()
    
    #deletando válvula por válvula associada a esse BOP
    [session.query(Preventor).filter(Preventor.id == p.id).delete() for p in preventores]
    session.commit()