from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from  model import Base
from model.preventor import Preventor
from model.valvula import Valvula


class BOP(Base):
    __tablename__ = 'bop'

    id = Column("pk_bop", Integer, primary_key=True)
    sonda = Column(String(140), unique=True)

    # Definição do relacionamento entre o BOP, as válvulas e os preventores.
    # Essa relação é implicita, não está salva na tabela 'bop',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    valvulas = relationship("Valvula", back_populates="bop")
    preventores = relationship("Preventor", back_populates="bop")
    testes = relationship("Teste", back_populates="bop")

    def __init__(self, sonda:str):
        """
        Cria um BOP

        Arguments:
            sonda: sonda na qual esse BOP pertence
        """
        self.sonda = sonda

    def adiciona_valvula(self, valvula:Valvula):
        """ Adiciona uma nova válvula ao BOP
        """
        self.valvulas.append(valvula)
        
    def adiciona_preventor(self, preventor:Preventor):
        """ Adiciona um novo preventor ao BOP
        """
        self.preventores.append(preventor)

