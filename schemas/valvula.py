from typing import List
from pydantic import BaseModel

from models.valvula import Valvula

class ValvulaSchema(BaseModel):
    """ Define como uma nova válvula a ser inserido deve ser representada
    """
    id: int = "Inclua o id da válvula"
    acronimo: str = "Insira o nome do acronimo que defina corretamente a válvula"
    
class ValvulaBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no bop_id.
    """
    bop_id: int
    
class ListagemValvulasSchema(BaseModel):
    """ Define como uma listagem de válvulas será retornada.
    """
    content:List[ValvulaSchema]
  
def apresenta_valvulas(valvulas: List[Valvula]):
    return [v.acronimo for v in valvulas]

def apresenta_valvulas_objetos(valvulas: List[Valvula]):
    result = []
    for valvula in valvulas:
        result.append({
            "id": valvula.id,
            "acronimo": valvula.acronimo
        })

    return {"content": result}
