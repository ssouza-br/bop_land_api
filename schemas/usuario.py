from pydantic import BaseModel
from models.usuario import Usuario


class UsuarioViewSchema(BaseModel):
    """Define como um novo usuário a ser inserido deve ser representado"""

    name: str
    email: str


class UsuarioLoginSchema(BaseModel):
    """Define como um novo usuário a ser inserido deve ser representado"""

    email: str
    password: str


class UsuarioRegisterSchema(BaseModel):
    """Define como um novo usuário a ser inserido deve ser representado"""

    name: str
    email: str
    password: str


def apresenta_usuario(usuario: Usuario):
    """Retorna uma representação do usuário seguindo o schema definido em
    usuarioViewSchema.
    """
    return {"nome": usuario.nome, "email": usuario.email}
