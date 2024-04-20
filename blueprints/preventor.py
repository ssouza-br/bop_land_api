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

@bp.get('/all', tags=[preventor_tag])
@jwt_required()
def get_preventores():
    """Faz a busca por todas os preventores já cadastrados

    Retorna uma representação da listagem de Preventores.
    """
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    preventores = session.query(Preventor.acronimo).distinct().all()

    if not preventores:
        # se não há preventores cadastrados
        return {"preventores": []}, 200
    else:
        # retorna a representação de BOP
        return apresenta_preventores(preventores), 200

@bp.get('/', responses={"200": ListagemPreventoresSchema})
@jwt_required()
def get_bop(query: PreventorBuscaSchema):
    """Faz a busca de todas as válvulas de um BOP através do bop_id

    Retorna uma representação das válvulas.
    """
    bop_id = query.bop_id

    # criando conexão com a base
    session = Session()

    # encontrando o bop pelo nome da sonda
    bop = session.query(BOP).filter(BOP.id == bop_id).first()
    
    if not bop:
        # se o bop não foi encontrado
        error_msg = "BOP não encontrado na base :/"
        return {"mensagem": error_msg}, 404
    else:
        bop_id = bop.id
        
        # fazendo a busca dos preventores
        preventores = session.query(Preventor).filter(Preventor.bop_id == bop_id).all()
        
        if not preventores:
            # se os preventores não forem encontrados
            error_msg = "Preventores não encontradas na base :/"
            return {"mensagem": error_msg}, 404
        else:
            # retorna a representação dos preventores
            return apresenta_preventores_objetos(preventores), 200
