from pydantic import BaseModel
from typing import List, Optional
from models.preventor import Preventor
from models.valvula import Valvula
from models.bop import BOP

class BOPSchema(BaseModel):
    """ Define como um novo produto a ser inserido deve ser representado
    """
    sonda: str
    valvulas: List[str]    
    preventores: List[str]
    

class ListagemBOPsSchema(BaseModel):
    """ Define como uma listagem de BOPs será retornada.
    """
    content:List[BOPSchema]
    
class BOPBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome da sonda dona do BOP.
    """
    sonda: Optional[str] = None
    pagina: int = 1
    por_pagina: int = 4

class BOPDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mensagem: str
    sonda: str
    
class BOPViewSchema(BaseModel):
    """ Define como um BOP será retornado: BOP + válvulas + preventores.
    """
    bop_id: int
    sonda: str
    valvulas: List[str]    
    preventores: List[str]
    
class ListagemSondasSchema(BaseModel):
    """ Define como uma listagem de sondas será retornada.
    """
    content:List[str]