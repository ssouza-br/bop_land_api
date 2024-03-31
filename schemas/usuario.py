from pydantic import BaseModel
from model.usuario import Usuario

class UsuarioSchema(BaseModel):
    """ Define como um novo usuário a ser inserido deve ser representado
    """
    nome: str
    email: str
    senha: str
    
class UsuarioViewSchema(BaseModel):
    """ Define como um novo usuário a ser inserido deve ser representado
    """
    nome: str
    email: str
    
class UsuarioLoginSchema(BaseModel):
    """ Define como um novo usuário a ser inserido deve ser representado
    """
    email: str
    senha: str
    
def apresenta_usuario(usuario: Usuario):
    """ Retorna uma representação do usuário seguindo o schema definido em
        usuarioViewSchema.
    """

    return {"nome": usuario.nome, "email": usuario.email}

