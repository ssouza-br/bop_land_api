from sqlalchemy import Column, String, Integer
import bcrypt

from  model import Base


class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column("pk_usuario", Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    senha = Column(String(100))

    def __init__(self, nome:str, email:str, senha: str):
        """
        Cria um usuário
        """
        self.nome = nome
        self.email = email
        self.senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    def checa_senha(self,senha):
        return bcrypt.checkpw(senha.encode('utf-8'),self.senha.encode('utf-8'))

