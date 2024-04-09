
# from sqlite3 import IntegrityError
from math import ceil
from operator import itemgetter
from urllib.parse import unquote
from venv import logger
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy import exc

from model import Session
from model.bop import BOP
from model.preventor import Preventor
from model.valvula import Valvula
from schemas.bop import BOPBuscaSchema, BOPDelSchema, BOPViewSchema, ListagemBOPsSchema, apresenta_bops
from schemas.error import ErrorSchema

bop_tag = Tag(name="BOP", description="Adição, visualização e remoção de BOPs à base")
security = [{"jwt": []}]

bp = APIBlueprint('bop',
                  __name__, 
                  url_prefix='/bop', 
                  abp_tags=[bop_tag], 
                  abp_security=security,
                  abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
                  doc_ui=True)
CORS(bp, supports_credentials=True)

@bp.post('/', responses={"200": BOPViewSchema})
@jwt_required()
def add_bop(form: BOPViewSchema):
    """Adiciona um novo BOP a base de dados

    Retorna uma representação dos BOPs com válvulas e preventores associados.
    """
    sonda = form.sonda
    valvulas = form.valvulas
    preventores = form.preventores
    session = Session()
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
        # adicionando bop
        session.add(bop)
        session.commit()
        # efetivando o camando de adição de novo item na tabela
        logger.debug(f"Adicionado BOP da sonda: '{bop.sonda}' com válvulas e preventores")
        return apresenta_bops([bop]), 200

    except exc.IntegrityError:
        session.rollback()
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "BOP dessa sonda já salvo na base :/"
        logger.warning(f"Erro ao adicionar produto '{bop.sonda}', {error_msg}")
        return {"mensagem": error_msg}, 409

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo BOP :/"
        logger.warning(f"Erro ao adicionar BOP '{bop.sonda}', {error_msg}")
        return {"mensagem": error_msg}, 400

@bp.get('/', responses={"200": ListagemBOPsSchema})
@jwt_required()
def get_bop(query: BOPBuscaSchema):
    """Faz a busca por um BOP do nome da sonda, caso esse campo fique vazio traz toda a lista de BOP do sistema

    Retorna uma representação dos BOPs, válvulas e preventores associados.
    """
    # criando conexão com a base
    session = Session()

    sonda, page, per_page = query.sonda, query.page, query.per_page
    if sonda:
        bop_sonda = sonda
        logger.debug(f"Coletando dados sobre BOP #{bop_sonda}")
        # fazendo a busca
        bop = session.query(BOP).filter(BOP.sonda.like(f'%{bop_sonda}%')).all()
        if not bop:
            # se o bop não foi encontrado
            error_msg = "BOP não encontrado na base :/"
            logger.warning(f"Erro ao buscar BOP '{bop_sonda}', {error_msg}")
            return {"mensagem": error_msg}, 404
        else:
            total_records = session.query(BOP).filter(BOP.sonda.like(f'%{bop_sonda}%')).count()

            # Calculate total pages
            total_pages = ceil(total_records / per_page)

            # Calculate whether there are more pages
            has_next = page < total_pages

            # Calculate whether there are previous pages
            has_prev = page > 1
            
            # Calculate current page
            current_page = page
        
            logger.debug(f"BOP encontrado: '{bop_sonda}'")
            # retorna a representação de bop
            return {
            "total_pages": total_pages,
            "total_records": total_records,
            "current_page": current_page,
            "has_next": has_next,
            "has_prev": has_prev,
            "items": apresenta_bops(bop)
        }, 200
    else:
        # trazendo os resultados paginados e em ordem alfabética por nome da sonda
        offset = (page - 1) * per_page
        bops = session.query(BOP).order_by(BOP.sonda).offset(offset).limit(per_page).all()
        # Count total number of records
        total_records = session.query(BOP).count()

        # Calculate total pages
        total_pages = ceil(total_records / per_page)

        # Calculate whether there are more pages
        has_next = page < total_pages

        # Calculate whether there are previous pages
        has_prev = page > 1

        # Perform pagination manually
        offset = (page - 1) * per_page
        bops = session.query(BOP).order_by(BOP.sonda).offset(offset).limit(per_page).all()

        # Calculate current page
        current_page = page
        
        return {
            "total_pages": total_pages,
            "total_records": total_records,
            "current_page": current_page,
            "has_next": has_next,
            "has_prev": has_prev,
            "items": apresenta_bops(bops)
        }, 200

@bp.delete('/', responses={"200": BOPDelSchema})
@jwt_required()
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
        logger.debug(f"Deletado BOP #{bop_sonda}")
        return {"mensagem": "BOP removido", "sonda": bop_sonda}
    else:
        # se o produto não foi encontrado
        error_msg = "BOP não encontrado na base :/"
        logger.warning(f"Erro ao deletar BOP #'{bop_sonda}', {error_msg}")
        return {"mensagem": error_msg}, 404

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