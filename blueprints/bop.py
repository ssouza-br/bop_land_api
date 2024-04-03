
from sqlite3 import IntegrityError
from urllib.parse import unquote
from venv import logger
from flask_openapi3 import APIBlueprint, Tag

from model import Session
from model.bop import BOP
from model.preventor import Preventor
from model.valvula import Valvula
from schemas.bop import BOPBuscaSchema, BOPDelSchema, BOPViewSchema, ListagemBOPsSchema, apresenta_bops
from schemas.error import ErrorSchema

bop_tag = Tag(name="BOP", description="Adição, visualização e remoção de BOPs à base")

bp = APIBlueprint('bop',
                  __name__, url_prefix='/bop', 
                  abp_tags=[bop_tag], 
                  abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
                  doc_ui=True)

@bp.post('/', responses={"200": BOPViewSchema})
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
        return apresenta_bops(bops), 200

@bp.get('/', responses={"200": ListagemBOPsSchema})
def get_bop(query: BOPBuscaSchema):
    """Faz a busca por um BOP do nome da sonda dona desse equipamento

    Retorna uma representação dos BOPs, válvulas e preventores associados.
    """
    # criando conexão com a base
    session = Session()
    
    if query.sonda:
        bop_sonda = query.sonda
        logger.debug(f"Coletando dados sobre BOP #{bop_sonda}")
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
            return apresenta_bops([bop]), 200 
    else:
        bops = session.query(BOP).all()
        return apresenta_bops(bops), 200 

@bp.delete('/', responses={"200": BOPDelSchema})
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