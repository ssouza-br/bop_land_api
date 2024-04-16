
from urllib.parse import unquote
from venv import logger
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag

from model import Session
from model.bop import BOP
from model.valvula import Valvula
from schemas.error import ErrorSchema
from schemas.valvula import ListagemValvulasSchema, ValvulaBuscaSchema, apresenta_valvulas, apresenta_valvulas_objetos

valvula_tag = Tag(name="Válvula", description="Visualização de válvulas persistidas na base")
security = [{"jwt": []}]

bp = APIBlueprint('valvula',
                  __name__, 
                  url_prefix='/valvula', 
                  abp_tags=[valvula_tag], 
                  abp_security=security,
                  abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
                  doc_ui=True)
CORS(bp, supports_credentials=True)

@bp.get('/', tags=[valvula_tag])
@jwt_required()
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
        # retorna a representação de Válvulas
        return apresenta_valvulas(valvulas), 200

@bp.get('/sonda', responses={"200": ListagemValvulasSchema})
@jwt_required()
def get_bop(query: ValvulaBuscaSchema):
    """Faz a busca de todas as válvulas de um BOP através do nome sonda

    Retorna uma representação das válvulas.
    """
    # criando conexão com a base
    session = Session()

    sonda = query.sonda

    bop_sonda = unquote(unquote(sonda))
    logger.debug(f"Coletando dados sobre BOP #{bop_sonda}")
    # criando conexão com a base
    session = Session()

    # encontrando o bop pelo nome da sonda
    bop = session.query(BOP).filter(BOP.sonda == bop_sonda).first()
    
    if not bop:
        # se o bop não foi encontrado
        error_msg = "BOP não encontrado na base :/"
        logger.warning(f"Erro ao buscar BOP '{bop_sonda}', {error_msg}")
        return {"mensagem": error_msg}, 404
    else:
        bop_id = bop.id
        logger.debug(f"Coletando as válvulas do BOP #{bop_sonda}")
        
        # fazendo a busca das válvulas
        valvulas = session.query(Valvula).filter(Valvula.bop_id == bop_id).all()
        
        if not valvulas:
            # se as válvulas não forem encontradas
            error_msg = "Válvulas não encontradas na base :/"
            logger.warning(f"Erro ao buscar Válvulas '{bop_sonda}', {error_msg}")
            return {"mensagem": error_msg}, 404
        else:
        
            logger.debug(f"Válvulas encontradas do BOP: '{bop_sonda}'")
            # retorna a representação de bop
            return {
            "items": apresenta_valvulas_objetos(valvulas)}, 200
