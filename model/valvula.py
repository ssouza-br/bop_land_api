from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from  model import Base


class Valvula(Base):
    __tablename__ = 'valvula'

    id = Column(Integer, primary_key=True)
    acronimo = Column(String(4000))

    # Definição do relacionamento entre o BOP e a válvula.
    # Aqui está sendo definido a coluna 'bop_id' que vai guardar
    # a referencia ao BOP, a chave estrangeira que relaciona
    # um BOP a válvula.
    bop_id = Column(Integer, ForeignKey("bop.pk_bop"), nullable=False)
    teste_id = Column(Integer, ForeignKey("teste.pk_teste"))
    bop = relationship("BOP", back_populates="valvulas")
    teste = relationship("Teste", back_populates="valvulas_testadas")

    def __init__(self, acronimo:str):
        """
        Cria uma Válvula

        Arguments:
            acrônimo: acronimo para identificação da válvula.
        """
        self.acronimo = acronimo