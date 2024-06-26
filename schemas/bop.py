from pydantic import BaseModel
from typing import List, Optional
from model.bop import BOP

class BOPSchema(BaseModel):
    """ Define como um novo produto a ser inserido deve ser representado
    """
    sonda: str = "NSXX"

class BOPBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome da sonda dona do BOP.
    """
    sonda: Optional[str] = None
    pagina: int = 1
    por_pagina: int = 4

class ListagemBOPsSchema(BaseModel):
    """ Define como uma listagem de BOPs será retornada.
    """
    content:List[BOPSchema]
    
class ListagemSondasSchema(BaseModel):
    """ Define como uma listagem de sondas será retornada.
    """
    content:List[str]


def apresenta_bops(bops: List[BOP]):
    """ Retorna uma representação do BOP seguindo o schema definido em
        BOPViewSchema.
    """
    result = []
    for bop in bops:
        result.append({
            "id": bop.id,
            "sonda": bop.sonda,
            "valvulas": [v.acronimo for v in bop.valvulas],
            "preventores": [p.acronimo for p in bop.preventores],
        })

    return {"content": result}


class BOPViewSchema(BaseModel):
    """ Define como um BOP será retornado: BOP + válvulas + preventores.
    """
    sonda: str
    valvulas: List[str]    
    preventores: List[str]

class BOPDelSchemaById(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    id: int

class BOPDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mensagem: str
    sonda: str
