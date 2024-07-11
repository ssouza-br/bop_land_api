from flask import jsonify, request, g
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field, ValidationError
import xml.etree.ElementTree as ET
import requests

from schemas.preventor import ListagemPreventoresSchema
from schemas.valvula import ListagemValvulasSchema
from schemas.bop import (
    BOPSchema,
    ListagemBOPsSchema,
    BOPBuscaSchema,
    BOPDelSchema,
    BOPViewSchema,
    ListagemSondasSchema,
)
from exceptions.repository_error import RepositoryError
from repositories.bop_repository import BOPRepository
from models import Session
from models import BOP
from schemas.error import ErrorSchema

bop_tag = Tag(name="BOP", description="Adição, visualização e remoção de BOPs à base")
security = [{"api_key": []}]

bp = APIBlueprint(
    "/bop",
    __name__,
    url_prefix="/api",
    abp_tags=[bop_tag],
    abp_security=security,
    abp_responses={"400": ErrorSchema, "409": ErrorSchema},
    doc_ui=True,
)
CORS(bp, supports_credentials=True, origins=["http://localhost:5173"])


class BOPPath(BaseModel):
    bop_id: int = Field(..., description="bop id")


class BOPPaginationPath(BaseModel):
    pagina: int = Field(..., description="pagina")
    por_pagina: int = Field(..., description="por pagina")


@bp.post("/bop", responses={"200": BOPViewSchema})
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
            {
                "sonda": bop_data.sonda,
                "latitude": bop_data.latitude,
                "longitude": bop_data.longitude,
                "valvulas": bop_data.valvulas,
                "preventores": bop_data.preventores,
            }
        )
        return new_bop.dict(), 201
    except RepositoryError as e:
        return e.to_dict(), 400


@bp.delete("/bop/<int:bop_id>", responses={"200": BOPDelSchema})
@jwt_required()
def del_bop(path: BOPPath):
    """Deleta um BOP a partir do seu id

    Retorna uma mensagem de confirmação da remoção.
    """
    bops_repo = BOPRepository(g.session)
    try:
        bops_repo.delete(path.bop_id)
        return {"mensagem": "BOP deletado com sucesso"}, 204
    except RepositoryError as e:
        return e.to_dict(), 400


@bp.get("/bop/<int:bop_id>/valves", responses={"200": ListagemValvulasSchema})
@jwt_required()
def get_valves_by_bop_id(path: BOPPath):
    """Retorna as válvulas do BOP a partir do seu id

    Retorna uma lista com todas válvulas do respectivo BOP.
    """
    bops_repo = BOPRepository(g.session)
    try:
        valvulas = bops_repo.get_valves_by_bop_id(path.bop_id)
        return valvulas, 200
    except RepositoryError as e:
        return e.to_dict(), 400


@bp.get("/bop/<int:bop_id>/preventors", responses={"200": ListagemPreventoresSchema})
@jwt_required()
def get_preventors_by_bop_id(path: BOPPath):
    """Retorna os preventores do BOP a partir do seu id

    Retorna uma lista com todos preventores do respectivo BOP.
    """
    bops_repo = BOPRepository(g.session)
    try:
        preventores = bops_repo.get_preventors_by_bop_id(path.bop_id)
        return preventores, 200
    except RepositoryError as e:
        return e.to_dict(), 400


@bp.get("/bop", responses={"200": ListagemBOPsSchema})
@jwt_required()
def get_bop(query: BOPBuscaSchema):
    """Faz a busca por um BOP do nome da sonda, caso esse campo fique vazio traz toda a lista paginada de BOPs do sistema

    Retorna uma representação dos BOPs, válvulas e preventores associados.
    """
    sonda, pagina, por_pagina = query.sonda, query.pagina, query.por_pagina

    bops_repo = BOPRepository(g.session)
    bops = bops_repo.list(sonda, pagina, por_pagina)
    return bops, 200


@bp.get("/previsao/bop/<int:bop_id>")
@jwt_required()
def get_weather(path: BOPPath):
    """Faz acesso a API externa CPTEC-INPE (http://servicos.cptec.inpe.br/XML/#req-previsao-7-dias) retornando a previsão do tempo para os últimos 7 dias na locação do BOP (latitude e longitude)

    Retorna uma representação de previsão do tempo com o nome da cidade e previsão de temperaturas min/max para os próximos 7 dias.
    """

    bops_repo = BOPRepository(g.session)
    try:
        bop = bops_repo.get_by_id(path.bop_id)
        # Get latitude and longitude from query parameters
        lat = bop.latitude
        lon = bop.longitude
    except ValidationError as err:
        return jsonify(err.errors()), 400

    if not lat or not lon:
        return jsonify({"error": "Please provide both latitude and longitude"}), 400

    try:
        # Construct the URL
        url = f"http://servicos.cptec.inpe.br/XML/cidade/7dias/{lat}/{lon}/previsaoLatLon.xml"

        # Fetch the weather forecast
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the XML response
        root = ET.fromstring(response.content)

        # Extract city and state information
        city_name = root.find("nome").text
        state = root.find("uf").text
        update_date = root.find("atualizacao").text

        # Extract weather forecasts
        forecasts = []
        for previsao in root.findall("previsao"):
            day_forecast = {
                "date": previsao.find("dia").text,
                "weather": previsao.find("tempo").text,
                "max_temp": previsao.find("maxima").text,
                "min_temp": previsao.find("minima").text,
                "uv_index": previsao.find("iuv").text,
            }
            forecasts.append(day_forecast)

        # Construct the JSON response
        result = {
            "city": city_name,
            "state": state,
            "updated_on": update_date,
            "forecasts": forecasts,
        }

        return jsonify(result)

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/sondas", responses={"200": ListagemSondasSchema})
@jwt_required()
def get_sondas():
    """
    Retorna lista de todas as sondas com BOPs salvos no sistema
    """
    # criando conexão com a base
    session = Session()

    # fazendo a busca
    bops = session.query(BOP).all()

    # retorna a representação de todas as sondas com BOP
    return {"items": [{"id": bop.id, "sonda": bop.sonda} for bop in bops]}, 200
