
from urllib.parse import unquote
from venv import logger
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag

from model import Session
from model.bop import BOP
from model.preventor import Preventor
from schemas.error import ErrorSchema
from schemas.preventor import ListagemPreventoresSchema, PreventorBuscaSchema, apresenta_preventores, apresenta_preventores_objetos

preventor_tag = Tag(name="Preventor", description="Visualização de preventores persistidos na base")
security = [{"jwt": []}]

bp = APIBlueprint('preventor',
                  __name__, 
                  url_prefix='/preventor', 
                  abp_tags=[preventor_tag], 
                  abp_security=security,
                  abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
                  doc_ui=True)
CORS(bp, supports_credentials=True)

@bp.get('/', tags=[preventor_tag])
@jwt_required()
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

@bp.get('/sonda', responses={"200": ListagemPreventoresSchema})
@jwt_required()
def get_bop(query: PreventorBuscaSchema):
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
        logger.debug(f"Coletando os preventores do BOP #{bop_sonda}")
        
        # fazendo a busca dos preventores
        preventores = session.query(Preventor).filter(Preventor.bop_id == bop_id).all()
        
        if not preventores:
            # se as válvulas não forem encontradas
            error_msg = "Preventores não encontradas na base :/"
            logger.warning(f"Erro ao buscar preventores '{bop_sonda}', {error_msg}")
            return {"mensagem": error_msg}, 404
        else:
        
            logger.debug(f"Preventores encontradas do BOP: '{bop_sonda}'")
            # retorna a representação de bop
            return {
            "items": apresenta_preventores_objetos(preventores)}, 200
