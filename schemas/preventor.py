from typing import List
from pydantic import BaseModel

from model.preventor import Preventor

class PreventorSchema(BaseModel):
    """ Define como um novo comentário a ser inserido deve ser representado
    """
    preventor_id: int = "Inclua o id da válvulao BOP no qual a Preventor deve ser inserida"
    acronimo: str = "Insira o nome do acronimo que defina corretamente a válvula"
    
class PreventorBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome da sonda dona do BOP.
    """
    sonda: str  
    
class ListagemPreventoresSchema(BaseModel):
    """ Define como uma listagem de BOPs será retornada.
    """
    content:List[PreventorSchema]
  
def apresenta_preventores(preventores: List[Preventor]):
    return [p.acronimo for p in preventores]

def apresenta_preventores_objetos(preventores: List[Preventor]):
    result = []
    for preventor in preventores:
        result.append({
            "preventor_id": preventor.id,
            "acronimo": preventor.acronimo
        })

    return {"content": result}
