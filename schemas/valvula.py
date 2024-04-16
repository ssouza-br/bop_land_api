from typing import List
from pydantic import BaseModel

from model.valvula import Valvula

class ValvulaSchema(BaseModel):
    """ Define como um novo comentário a ser inserido deve ser representado
    """
    valvula_id: int = "Inclua o id da válvulao BOP no qual a valvula deve ser inserida"
    acronimo: str = "Insira o nome do acronimo que defina corretamente a válvula"
    
class ValvulaBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome da sonda dona do BOP.
    """
    sonda: str  
    
class ListagemValvulasSchema(BaseModel):
    """ Define como uma listagem de BOPs será retornada.
    """
    content:List[ValvulaSchema]
  
def apresenta_valvulas(valvulas: List[Valvula]):
    return [v.acronimo for v in valvulas]

def apresenta_valvulas_objetos(valvulas: List[Valvula]):
    result = []
    for valvula in valvulas:
        result.append({
            "valvula_id": valvula.id,
            "acronimo": valvula.acronimo
        })

    return {"content": result}
