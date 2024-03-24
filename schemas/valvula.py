from pydantic import BaseModel


class ValvulaSchema(BaseModel):
    """ Define como um novo comentário a ser inserido deve ser representado
    """
    bop_id: int = "Inclua o id do BOP no qual a valvula deve ser inserida"
    acronimo: str = "Insira o nome do acronimo que defina corretamente a válvula"
