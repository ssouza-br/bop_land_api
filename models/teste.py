import enum
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.orm import relationship

from models import Base


class TestStatus(enum.Enum):
    CRIADO = "criado"
    AGENDAD0 = "agendado"
    APROVADO = "aprovado"
    FALHO = "falho"


class TesteModel(Base):
    __tablename__ = "teste"

    id = Column("pk_teste", Integer, primary_key=True)
    nome = Column(String(4000))
    data_aprovacao = Column(DateTime)
    aprovador_id = Column(Integer, ForeignKey("usuario.pk_usuario"))
    # aprovador = relationship("Usuario", back_populates="teste")

    # Definição do relacionamento entre o teste e o BOP.
    # Aqui está sendo definido a coluna 'bop_id' que vai guardar
    # a referencia ao BOP, a chave estrangeira que relaciona
    # um BOP ao teste.
    bop_id = Column(Integer, ForeignKey("bop.pk_bop"), nullable=False)
    bop = relationship("BOP", back_populates="testes")
    valvulas_testadas = relationship("Valvula", back_populates="teste")
    preventores_testados = relationship("Preventor", back_populates="teste")
    status = Column(Enum(TestStatus), nullable=False, default=TestStatus.CRIADO)

    # Define a unique constraint on the combination of 'nome' and 'bop_id'
    __table_args__ = (UniqueConstraint("nome", "bop_id", name="_nome_bop_id_uc"),)

    def __init__(self, nome: str, bop_id: int):
        """
        Cria uma Válvula

        Arguments:
            nome: nome para identificação do teste.
        """
        self.nome = nome
        self.bop_id = bop_id

    def dict(self):
        if self.aprovador_id:
            return {
                "testeId": self.id,
                "bopId": self.bop_id,
                "nome": self.nome,
                "aprovadorId": self.aprovador_id,
                "dataAprovacao": self.data_aprovacao,
                "valvulasTestadas": [
                    valvula.to_string() for valvula in self.valvulas_testadas
                ],
                "preventoresTestados": [
                    preventor.to_string() for preventor in self.preventores_testados
                ],
            }
        return {
            "testeId": self.id,
            "bopId": self.bop_id,
            "nome": self.nome,
            "valvulasTestadas": [
                valvula.to_string() for valvula in self.valvulas_testadas
            ],
            "preventoresTestados": [
                preventor.to_string() for preventor in self.preventores_testados
            ],
        }
