from flask import request, jsonify
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field, ValidationError

from schemas.error import ErrorSchema

previsao_tag = Tag(
    name="Previsao", description="Previsão do tempo para os próximos 7 dias"
)
security = [{"api_key": []}]

bp = APIBlueprint(
    "/previsao",
    __name__,
    url_prefix="/api",
    abp_tags=[previsao_tag],
    abp_security=security,
    abp_responses={"400": ErrorSchema, "409": ErrorSchema},
    doc_ui=True,
)
CORS(bp, supports_credentials=True)


class PrevisaoPath(BaseModel):
    latitude: float = Field(..., description="latitude")
    longitude: float = Field(..., description="longitude")


@bp.get("/previsao")
def get_weather(body: PrevisaoPath):
    json_data = request.get_json()
    try:
        previsao_data = PrevisaoPath(**json_data)
    except ValidationError as err:
        return jsonify(err.errors()), 400

    # Get latitude and longitude from query parameters
    lat = previsao_data.latitude
    lon = previsao_data.longitude

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
