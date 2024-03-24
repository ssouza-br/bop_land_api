from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from typing import Union

from  model import Base


class Preventor(Base):
    __tablename__ = 'preventor'

    id = Column(Integer, primary_key=True)
    acronimo = Column(String(4000))

    # Definição do relacionamento entre o comentário e um produto.
    # Aqui está sendo definido a coluna 'produto' que vai guardar
    # a referencia ao produto, a chave estrangeira que relaciona
    # um produto ao comentário.
    bop = Column(Integer, ForeignKey("bop.pk_bop"), nullable=False)

    def __init__(self, acronimo:str):
        """
        Cria um Preventor

        Arguments:
            acrônimo: acronimo para identificação do preventor.
        """
        self.acronimo = acronimo