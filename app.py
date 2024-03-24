from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Produto, Comentario
from logger import logger
from model.bop import BOP
from model.preventor import Preventor
from model.valvula import Valvula
from schemas import *
from flask_cors import CORS

from schemas.bop import BOPBuscaSchema, BOPViewSchema, apresenta_bop, apresenta_bops
from schemas.preventor import PreventorSchema
from schemas.valvula import ValvulaSchema

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
produto_tag = Tag(name="Produto", description="Adição, visualização e remoção de produtos à base")
comentario_tag = Tag(name="Comentario", description="Adição de um comentário à um produtos cadastrado na base")
bop_tag = Tag(name="BOP", description="Adição, visualização e remoção de BOPs à base")
valvula_tag = Tag(name="Valvula", description="Adição de uma válvula a um BOP cadastrado na base")
preventor_tag = Tag(name="Preventor", description="Adição de um preventor a um BOP cadastrado na base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/produto', tags=[produto_tag],
          responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_produto(form: ProdutoSchema):
    """Adiciona um novo Produto à base de dados

    Retorna uma representação dos produtos e comentários associados.
    """
    produto = Produto(
        nome=form.nome,
        quantidade=form.quantidade,
        valor=form.valor)
    logger.debug(f"Adicionando produto de nome: '{produto.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(produto)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado produto de nome: '{produto.nome}'")
        return apresenta_produto(produto), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Produto de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/produtos', tags=[produto_tag],
         responses={"200": ListagemProdutosSchema, "404": ErrorSchema})
def get_produtos():
    """Faz a busca por todos os Produto cadastrados

    Retorna uma representação da listagem de produtos.
    """
    logger.debug(f"Coletando produtos ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    produtos = session.query(Produto).all()

    if not produtos:
        # se não há produtos cadastrados
        return {"produtos": []}, 200
    else:
        logger.debug(f"%d rodutos econtrados" % len(produtos))
        # retorna a representação de produto
        print(produtos)
        return apresenta_produtos(produtos), 200


@app.get('/produto', tags=[produto_tag],
         responses={"200": ProdutoViewSchema, "404": ErrorSchema})
def get_produto(query: ProdutoBuscaSchema):
    """Faz a busca por um Produto a partir do id do produto

    Retorna uma representação dos produtos e comentários associados.
    """
    produto_id = query.id
    logger.debug(f"Coletando dados sobre produto #{produto_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    produto = session.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        # se o produto não foi encontrado
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao buscar produto '{produto_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Produto econtrado: '{produto.nome}'")
        # retorna a representação de produto
        return apresenta_produto(produto), 200


@app.delete('/produto', tags=[produto_tag],
            responses={"200": ProdutoDelSchema, "404": ErrorSchema})
def del_produto(query: ProdutoBuscaSchema):
    """Deleta um Produto a partir do nome de produto informado

    Retorna uma mensagem de confirmação da remoção.
    """
    produto_nome = unquote(unquote(query.nome))
    print(produto_nome)
    logger.debug(f"Deletando dados sobre produto #{produto_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Produto).filter(Produto.nome == produto_nome).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado produto #{produto_nome}")
        return {"mesage": "Produto removido", "id": produto_nome}
    else:
        # se o produto não foi encontrado
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao deletar produto #'{produto_nome}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.post('/cometario', tags=[comentario_tag],
          responses={"200": ProdutoViewSchema, "404": ErrorSchema})
def add_comentario(form: ComentarioSchema):
    """Adiciona de um novo comentário à um produtos cadastrado na base identificado pelo id

    Retorna uma representação dos produtos e comentários associados.
    """
    produto_id  = form.produto_id
    logger.debug(f"Adicionando comentários ao produto #{produto_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca pelo produto
    produto = session.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        # se produto não encontrado
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao adicionar comentário ao produto '{produto_id}', {error_msg}")
        return {"mesage": error_msg}, 404

    # criando o comentário
    texto = form.texto
    comentario = Comentario(texto)

    # adicionando o comentário ao produto
    produto.adiciona_comentario(comentario)
    session.commit()

    logger.debug(f"Adicionado comentário ao produto #{produto_id}")

    # retorna a representação de produto
    return apresenta_produto(produto), 200



###### IMPLEMEMENTAÇÃO NOVA##############

@app.post('/bop', tags=[bop_tag],
          responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_bop(form: BOPViewSchema):
    """Adiciona um novo BOP a base de dados

    Retorna uma representação dos BOPs com válvulas e preventores associados.
    """
    bop = BOP(
        sonda=form.sonda,
        tipo=form.tipo)
    logger.debug(f"Adicionando BOP da sonda: '{bop.sonda}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando bop
        session.add(bop)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado BOP da sonda: '{bop.sonda}'")
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
         responses={"200": ListagemProdutosSchema, "404": ErrorSchema})
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
    print(bop_sonda)
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


@app.post('/valvula', tags=[valvula_tag],
          responses={"200": BOPViewSchema, "404": ErrorSchema})
def add_valvula(form: ValvulaSchema):
    """Adiciona nova válvula a um BOP cadastrado na base identificado pelo id

    Retorna uma representação dos BOPs coma válvulas e preventores associados.
    """
    bop_id  = form.bop_id
    logger.debug(f"Adicionando válvulas ao BOP #{bop_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca pelo BOP
    bop = session.query(BOP).filter(BOP.id == bop_id).first()

    if not bop:
        # se BOP não encontrado
        error_msg = "BOP não encontrado na base :/"
        logger.warning(f"Erro ao adicionar válvula no BOP '{bop_id}', {error_msg}")
        return {"mesage": error_msg}, 404

    # criando a valvula
    acronimo = form.acronimo
    valvula = Valvula(acronimo)

    # adicionando o comentário ao produto
    bop.adiciona_valvula(valvula)
    session.commit()

    logger.debug(f"Adicionada válvula ao BOP #{bop_id}")

    # retorna a representação de produto
    return apresenta_bop(bop), 200

@app.post('/preventor', tags=[preventor_tag],
          responses={"200": BOPViewSchema, "404": ErrorSchema})
def add_preventor(form: PreventorSchema):
    """Adiciona novo preventor a um BOP cadastrado na base identificado pelo id

    Retorna uma representação dos BOPs com válvulas e preventores associados.
    """
    bop_id  = form.bop_id
    logger.debug(f"Adicionando válvulas ao BOP #{bop_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca pelo BOP
    bop = session.query(BOP).filter(BOP.id == bop_id).first()

    if not bop:
        # se BOP não encontrado
        error_msg = "BOP não encontrado na base :/"
        logger.warning(f"Erro ao adicionar válvula no BOP '{bop_id}', {error_msg}")
        return {"mesage": error_msg}, 404

    # criando a preventor
    acronimo = form.acronimo
    preventor = Preventor(acronimo)

    # adicionando o comentário ao produto
    bop.adiciona_preventor(preventor)
    session.commit()

    logger.debug(f"Adicionada válvula ao BOP #{bop_id}")

    # retorna a representação de produto
    return apresenta_bop(bop), 200
