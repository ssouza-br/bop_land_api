from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models import Base


class Preventor(Base):
    __tablename__ = "preventor"

    id = Column(Integer, primary_key=True)
    acronimo = Column(String(4000))

    # Definição do relacionamento entre o BOP e o preventor
    # Aqui está sendo definido a coluna 'bop_id' que vai guardar
    # a referencia ao BOP, a chave estrangeira que relaciona
    # um BOP ao preventor.
    bop_id = Column(Integer, ForeignKey("bop.pk_bop"), nullable=False)
    teste_id = Column(Integer, ForeignKey("teste.pk_teste"))
    bop = relationship(
        "BOP",
        back_populates="preventores",
        passive_deletes=True,
    )
    teste = relationship("TesteModel", back_populates="preventores_testados")

    def __init__(self, acronimo: str):
        """
        Cria um Preventor

        Arguments:
            acrônimo: acronimo para identificação do preventor.
        """
        self.acronimo = acronimo

    def to_string(self):
        return self.acronimo

    def dict(self):
        return {
            "id": self.id,
            "acronimo": self.acronimo,
        }
