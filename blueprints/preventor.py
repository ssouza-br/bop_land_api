from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag

from models import Session
from models.preventor import Preventor
from schemas.error import ErrorSchema
from schemas.preventor import (
    apresenta_preventores,
)

preventor_tag = Tag(
    name="Preventor", description="Visualização de preventores persistidos na base"
)
security = [{"jwt": []}]

bp = APIBlueprint(
    "/preventor",
    __name__,
    url_prefix="/api",
    abp_tags=[preventor_tag],
    abp_security=security,
    abp_responses={"400": ErrorSchema, "409": ErrorSchema},
    doc_ui=True,
)
CORS(bp, supports_credentials=True)


@bp.get("/preventor", tags=[preventor_tag])
@jwt_required()
def get_preventores():
    """Retorna uma lista com todos os preventores distintos presentes no sistema."""

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
