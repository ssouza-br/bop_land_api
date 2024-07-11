from typing import Optional

from models.teste import TesteModel
from sqlalchemy.orm import Query


class Specification:
    def is_satisfied_by(self, query: Query) -> Query:
        raise NotImplementedError()


class StatusSpecification(Specification):
    def __init__(self, status: Optional[str]):
        self.status = status

    def is_satisfied_by(self, query: Query) -> Query:
        if self.status in ("APROVADO", "CRIADO"):
            if self.status == "APROVADO":
                return query.filter(TesteModel.data_aprovacao != None)
            elif self.status == "CRIADO":
                return query.filter(TesteModel.data_aprovacao == None)
        else:
            print("eu n tenho status", query)
            return query


class BopIdSpecification(Specification):
    def __init__(self, bopId: Optional[int]):
        self.bopId = bopId

    def is_satisfied_by(self, query: Query) -> Query:
        if self.bopId is not None:
            return query.filter(TesteModel.bop_id == self.bopId)
        else:
            return query


class AprovadorIdSpecification(Specification):
    def __init__(self, aprovador_id: Optional[int]):
        self.aprovador_id = aprovador_id

    def is_satisfied_by(self, query: Query) -> Query:
        if self.aprovador_id is not None:
            return query.filter(TesteModel.aprovador_id == self.aprovador_id)
        else:
            return query
