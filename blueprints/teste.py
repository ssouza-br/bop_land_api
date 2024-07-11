from zoneinfo import ZoneInfo
from flask import g, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field, ValidationError

from utils.utils import format_error
from exceptions.repository_error import RepositoryError
from repositories.teste_repository import TesteRepository
from models import Session
from models.teste import TestStatus, TesteModel
from models.usuario import Usuario
from schemas.error import ErrorSchema
from schemas.teste import (
    ListagemTestesSchema,
    TesteBuscaSchema,
    TesteDelSchema,
    TesteSchema,
    TesteViewSchema,
)
from datetime import datetime


class TestePath(BaseModel):
    teste_id: int = Field(..., description="teste id")


teste_tag = Tag(name="Teste", description="Adição e visualização de testes à base")
security = [{"api_key": []}]

bp = APIBlueprint(
    "/teste",
    __name__,
    url_prefix="/api",
    abp_tags=[teste_tag],
    abp_security=security,
    abp_responses={"400": ErrorSchema, "409": ErrorSchema},
    doc_ui=True,
)
CORS(bp, supports_credentials=True, origins=["http://localhost:5173"])


@bp.post("/teste", responses={"200": TesteViewSchema})
@jwt_required()
def add_teste(body: TesteSchema):
    """Adiciona um novo Teste a base de dados

    Retorna uma representação do teste recém adicionado com válvulas e preventores testados.
    """
    json_data = request.get_json()
    try:
        teste_data = TesteSchema(**json_data)
    except ValidationError as err:
        return jsonify(err.errors()), 400

    testes_repo = TesteRepository(g.session)

    try:
        new_teste = testes_repo.add(
            {
                "bopId": teste_data.bopId,
                "nome": teste_data.nome,
                "valvulasTestadas": teste_data.valvulasTestadas,
                "preventoresTestados": teste_data.preventoresTestados,
            }
        )
        return new_teste.dict(), 201
    except RepositoryError as e:
        return e.to_dict(), 400


@bp.delete("/teste/<int:teste_id>", responses={"200": TesteDelSchema})
@jwt_required()
def del_teste(path: TestePath):
    """Deleta um teste a partir do seu id

    Retorna uma mensagem de confirmação da remoção.
    """
    testes_repo = TesteRepository(g.session)
    try:
        testes_repo.delete(path.teste_id)
        return {"mensagem": "Teste deletado com sucesso"}, 204
    except RepositoryError as e:
        return e.to_dict(), 400


@bp.get("/teste", responses={"200": ListagemTestesSchema})
@jwt_required()
def get_teste(query: TesteBuscaSchema):
    """Faz a busca por todos os Testes presentes no sistema, a partir do seu status no sistema: aprovado ou em_andamento

    Retorna uma representação dos Testes.
    """
    status, bopId, aprovadorId, pagina, por_pagina = (
        query.status,
        query.bopId,
        query.aprovadorId,
        query.pagina,
        query.por_pagina,
    )

    testes_repo = TesteRepository(g.session)
    testes = testes_repo.listar(status, bopId, aprovadorId, pagina, por_pagina)
    return testes, 200


@bp.put("/teste/<int:teste_id>/aprovar", responses={"200": ListagemTestesSchema})
@jwt_required()
def aprovar_teste(path: TestePath):
    """Aprova um teste a partir do seu id"""
    # criando conexão com a base
    session = Session()

    teste_id = path.teste_id
    # pegando o usuário que aprovou o teste
    current_user = get_jwt_identity()
    aprovador = session.query(Usuario).filter_by(email=current_user).first()

    teste = session.query(TesteModel).filter(TesteModel.id == teste_id).first()
    if teste:
        # atribuindo o id do aprovador ao teste
        teste.aprovador_id = aprovador.id

        # atribuindo a data da aprovação
        teste.data_aprovacao = datetime.now(ZoneInfo("America/Sao_Paulo"))

        # mudando o status do teste
        teste.status = TestStatus.APROVADO

        session.commit()
    else:
        # caso um erro fora do previsto
        error_msg = "Teste não encontrado no sistema :/"
        return jsonify(format_error(error_msg)), 400

    # retorna a representação de bop paginada
    return {
        "teste_id": teste_id,
        "aprovador": aprovador.nome,
        "data_aprovacao": teste.data_aprovacao,
    }, 200
