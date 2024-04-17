from pydantic import BaseModel
from typing import List, Optional
from model.teste import Teste
from schemas.preventor import PreventorSchema
from schemas.valvula import ValvulaSchema

class TesteViewSchema(BaseModel):
    """ Define como um Teste será retornado: nome do teste, bop_id,
    válvulas testadas e preventores testados.
    """
    nome: str
    bop_id: int
    valvulas_testadas: List[ValvulaSchema]    
    preventores_testados: List[PreventorSchema]

def apresenta_testes(testes: List[Teste]):
    """ Retorna uma representação do Teste
    """
    result = []
    for teste in testes:
        result.append({
            "nome": teste.nome,
            "bop_id": teste.bop_id,
            "valvulas_testadas": [v.acronimo for v in teste.valvulas_testadas],
            "preventores_testados": [p.acronimo for p in teste.preventores_testados],
        })

    return {"content": result}

