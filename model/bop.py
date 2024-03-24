from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base, Comentario
from model.preventor import Preventor
from model.valvula import Valvula


class BOP(Base):
    __tablename__ = 'bop'

    id = Column("pk_bop", Integer, primary_key=True)
    sonda = Column(String(140), unique=True)
    tipo = Column(Integer)

    # Definição do relacionamento entre o produto e o comentário.
    # Essa relação é implicita, não está salva na tabela 'produto',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    valvulas = relationship("Valvula")
    preventores = relationship("Preventor")

    def __init__(self, sonda:str, tipo:int):
        """
        Cria um BOP

        Arguments:
            sonda: sonda na qual esse BOP pertence
            tipo: tipo de BOP para efeito do algoritimo de teste
        """
        self.sonda = sonda
        self.tipo = tipo

    def adiciona_valvula(self, valvula:Valvula):
        """ Adiciona uma nova válvula ao BOP
        """
        self.valvulas.append(valvula)
        
    def adiciona_preventor(self, preventor:Preventor):
        """ Adiciona uma nova válvula ao BOP
        """
        self.preventores.append(preventor)

