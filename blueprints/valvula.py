from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag

from models import Session
from models.valvula import Valvula
from schemas.error import ErrorSchema
from schemas.valvula import (
    apresenta_valvulas,
)

valvula_tag = Tag(
    name="Válvula", description="Visualização de válvulas persistidas na base"
)
security = [{"jwt": []}]

bp = APIBlueprint(
    "/valvula",
    __name__,
    url_prefix="/api",
    abp_tags=[valvula_tag],
    abp_security=security,
    abp_responses={"400": ErrorSchema, "409": ErrorSchema},
    doc_ui=True,
)
CORS(bp, supports_credentials=True)


@bp.get("/valvula", tags=[valvula_tag])
@jwt_required()
def get_valvulas():
    """Retorna uma lista com todas as válvulas distintas presentes no sistema."""
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    valvulas = session.query(Valvula.acronimo).distinct().all()

    if not valvulas:
        # se não há valvulas cadastrados
        return {"valvulas": []}, 200
    else:
        # retorna a representação de Válvulas
        return apresenta_valvulas(valvulas), 200
