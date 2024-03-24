from pydantic import BaseModel


class PreventorSchema(BaseModel):
    """ Define como um novo comentário a ser inserido deve ser representado
    """
    bop_id: int = "Inclua o id do BOP no qual o preventor deve ser inserido"
    acronimo: str = "Insira o nome do acronimo que defina corretamente o preventor"
