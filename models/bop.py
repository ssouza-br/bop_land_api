from sqlalchemy import Column, Float, String, Integer
from sqlalchemy.orm import relationship

from models import Base
from models.preventor import Preventor
from models.valvula import Valvula


class BOP(Base):
    __tablename__ = "bop"

    id = Column("pk_bop", Integer, primary_key=True)
    sonda = Column(String(140), unique=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Definição do relacionamento entre o BOP, as válvulas e os preventores.
    # Essa relação é implicita, não está salva na tabela 'bop',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    valvulas = relationship("Valvula", back_populates="bop", cascade="all, delete")
    preventores = relationship("Preventor", back_populates="bop", cascade="all, delete")
    testes = relationship("TesteModel", back_populates="bop")

    def __init__(self, sonda: str):
        """
        Cria um BOP

        Arguments:
            sonda: sonda na qual esse BOP pertence
        """
        self.sonda = sonda

    def adiciona_valvula(self, valvula: Valvula):
        """Adiciona uma nova válvula ao BOP"""
        self.valvulas.append(valvula)

    def adiciona_preventor(self, preventor: Preventor):
        """Adiciona um novo preventor ao BOP"""
        self.preventores.append(preventor)

    def equipment_to_string(lista):
        return [item.to_string() for item in lista]

    def dict(self):
        return {
            "bop_id": self.id,
            "sonda": self.sonda,
            "valvulas": [valvula.to_string() for valvula in self.valvulas],
            "preventores": [preventor.to_string() for preventor in self.preventores],
            # "testes": self.testes,
        }
