from math import ceil
from flask import jsonify, request, g
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field, ValidationError

from schemas.bop import BOPSchema, ListagemBOPsSchema, BOPBuscaSchema, BOPDelSchema, BOPViewSchema, ListagemSondasSchema
from exceptions.repository_error import RepositoryError
from repositories.bop_repository import BOPRepository
from models import Session
from models import BOP
from schemas.error import ErrorSchema

bop_tag = Tag(name="BOP", description="Adição, visualização e remoção de BOPs à base")
security = [{"api_key": []}]

bp = APIBlueprint('/bop',
                  __name__, 
                  url_prefix='/api', 
                  abp_tags=[bop_tag], 
                  abp_security=security,
                  abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
                  doc_ui=True)
CORS(bp, supports_credentials=True)

@bp.post('/bop', responses={"200": BOPViewSchema})
@jwt_required()
def add_bop(body: BOPSchema):
    """Adiciona um novo BOP a base de dados

    Retorna uma representação dos BOPs com válvulas e preventores associados.
    """
    json_data = request.get_json()
    try:
        bop_data = BOPSchema(**json_data)
    except ValidationError as err:
        return jsonify(err.errors()), 400

    bops_repo = BOPRepository(g.session)
    
    try:
        new_bop = bops_repo.add(
            sonda=bop_data.sonda,
            valvulas=bop_data.valvulas,
            preventores=bop_data.preventores
        )
        return new_bop.dict(), 201
    except RepositoryError as e:
        return e.to_dict(), 400

class BOPPath(BaseModel):
    bop_id: int = Field(..., description='bop id')
      
class BOPPaginationPath(BaseModel):
    pagina: int = Field(..., description='pagina')
    por_pagina: int = Field(..., description='por pagina')
    
@bp.delete('/bop/<int:bop_id>', responses={"200": BOPDelSchema})
@jwt_required()
def del_bop(path: BOPPath):
    print(path.bop_id)
    """Deleta um BOP a partir do nome da sonda dona desse equipamento

    Retorna uma mensagem de confirmação da remoção.
    """
    """Delete a booking by ID"""
    bops_repo = BOPRepository(g.session)
    if bops_repo.delete(path.bop_id):
        return {"mensagem": "BOP deletado com sucesso"}, 204
    return {'mensagem': 'BOP not found'}, 404

@bp.get('/bop', responses={"200": ListagemBOPsSchema})
@jwt_required()
def get_bop(query: BOPBuscaSchema):
    """Faz a busca por um BOP do nome da sonda, caso esse campo fique vazio traz toda a lista de BOP do sistema

    Retorna uma representação dos BOPs, válvulas e preventores associados.
    """
    sonda, pagina, por_pagina = query.sonda, query.pagina, query.por_pagina
    
    bops_repo = BOPRepository(g.session)
    bops = bops_repo.list(sonda, pagina, por_pagina)
    return bops

@bp.get('/sondas', responses={"200": ListagemSondasSchema})
@jwt_required()
def get_sondas():
    """
    Retorna todas as sondas com BOPs salvos no sistema
    """
    # criando conexão com a base
    session = Session()

    # fazendo a busca
    bops = session.query(BOP).all()
            
    # retorna a representação de todas as sondas com BOP
    return {
    "items": [{"id": bop.id ,"sonda": bop.sonda} for bop in bops]
}, 200