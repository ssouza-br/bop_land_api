from sqlalchemy import Column, Date, DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from model import Base


class Teste(Base):
    __tablename__ = 'teste'

    id = Column("pk_teste", Integer, primary_key=True)
    nome = Column(String(4000))
    data_aprovacao = Column(DateTime)
    aprovador_id = Column(Integer, ForeignKey("usuario.pk_usuario")) 

    # Definição do relacionamento entre o teste e o BOP.
    # Aqui está sendo definido a coluna 'bop_id' que vai guardar
    # a referencia ao BOP, a chave estrangeira que relaciona
    # um BOP ao teste.
    bop_id = Column(Integer, ForeignKey("bop.pk_bop"), nullable=False)
    bop = relationship("BOP", back_populates="testes")
    valvulas_testadas = relationship("Valvula", back_populates="teste")
    preventores_testados = relationship("Preventor", back_populates="teste")

    def __init__(self, nome:str, bop_id: int):
        """
        Cria uma Válvula

        Arguments:
            nome: nome para identificação do teste.
        """
        self.nome = nome
        self.bop_id = bop_id