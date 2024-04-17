from typing import List
from pydantic import BaseModel

from model.preventor import Preventor

class PreventorSchema(BaseModel):
    """ Define como um novo preventor a ser inserido deve ser representado
    """
    id: int = "Inclua o id da válvula"
    acronimo: str = "Insira o nome do acronimo que defina corretamente o preventor"
    
class PreventorBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no bop_id.
    """
    bop_id: int  
    
class ListagemPreventoresSchema(BaseModel):
    """ Define como uma listagem de preventores será retornada.
    """
    content:List[PreventorSchema]
  
def apresenta_preventores(preventores: List[Preventor]):
    return [p.acronimo for p in preventores]

def apresenta_preventores_objetos(preventores: List[Preventor]):
    result = []
    for preventor in preventores:
        result.append({
            "id": preventor.id,
            "acronimo": preventor.acronimo
        })

    return {"content": result}
