from pydantic import BaseModel
from typing import Optional, List
from model.bop import BOP
from model.produto import Produto

from schemas import ComentarioSchema
from schemas.preventor import PreventorSchema
from schemas.valvula import ValvulaSchema


class BOPSchema(BaseModel):
    """ Define como um novo produto a ser inserido deve ser representado
    """
    sonda: str = "NSXX"
    tipo: int = 1

class BOPBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome da sonda dona do BOP.
    """
    sonda: str = "Teste"


class ListagemBOPsSchema(BaseModel):
    """ Define como uma listagem de BOPs será retornada.
    """
    bops:List[BOPSchema]


def apresenta_bops(bops: List[BOP]):
    """ Retorna uma representação do BOP seguindo o schema definido em
        BOPViewSchema.
    """
    result = []
    for bop in bops:
        result.append({
            "sonda": bop.sonda,
            "tipo": bop.tipo,
        })

    return {"bops": result}


class BOPViewSchema(BaseModel):
    """ Define como um BOP será retornado: BOP + válvulas + preventores.
    """
    sonda: str = "NSXX"
    tipo: Optional[int] = 1
    total_valvulas: int = 1
    valvulas:List[ValvulaSchema]    
    total_preventores: int = 1
    preventores:List[PreventorSchema]


class BOPDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    sonda: str

def apresenta_bop(BOP: BOP):
    """ Retorna uma representação do BOP seguindo o schema definido em
        BOPViewSchema.
    """
    return {
        "sonda": BOP.sonda,
        "tipo": BOP.tipo,
        "total_valvulas": len(BOP.valvulas),
        "valvulas": [{"acronimo": v.acronimo} for v in BOP.valvulas],
        "total_preventores": len(BOP.preventores),
        "preventores": [{"acronimo": p.acronimo} for p in BOP.preventores]
    }
