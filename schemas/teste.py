from enum import Enum
from pydantic import BaseModel
from typing import List
from models.teste import TesteModel
from schemas.preventor import PreventorSchema
from schemas.valvula import ValvulaSchema


class AprovaTesteSchema(BaseModel):
    """Define que o id é o parâmetro necessário para aprovação do teste
    válvulas testadas e preventores testados.
    """

    id: int


class TesteViewSchema(BaseModel):
    """Define como um Teste será retornado: nome do teste, bop_id,
    válvulas testadas e preventores testados.
    """

    id: int
    bop_id: int
    nome: str
    valvulas_testadas: List[ValvulaSchema]
    preventores_testados: List[PreventorSchema]


class TesteSchema(BaseModel):
    """Define como um Teste será retornado: nome do teste, bop_id,
    válvulas testadas e preventores testados.
    """

    bop_id: int
    nome: str
    valvulas_testadas: List[int]
    preventores_testados: List[int]


class ListagemTestesSchema(BaseModel):
    """Define como uma listagem de BOPs será retornada."""

    content: List[TesteViewSchema]


class StatusEnum(str, Enum):
    aprovado = "aprovado"
    em_andamento = "em_andamento"


class TesteBuscaSchema(BaseModel):
    """Define como deve ser a estrutura que representa a busca. Que será
    feita apenas com base no nome da sonda dona do BOP.
    """

    status: StatusEnum
    pagina: int = 1
    por_pagina: int = 4


class TesteDelSchema(BaseModel):
    """Define como deve ser a estrutura do dado retornado após uma requisição
    de remoção.
    """

    mensagem: str
    nome: str


def apresenta_testes(testes: List[TesteModel]):
    """Retorna uma representação do Teste"""
    result = []
    for teste in testes:
        result.append(
            {
                "id": teste.id,
                "bop_id": teste.bop_id,
                "nome": teste.nome,
                "valvulas_testadas": [v.acronimo for v in teste.valvulas_testadas],
                "preventores_testados": [
                    p.acronimo for p in teste.preventores_testados
                ],
            }
        )

    return {"content": result}
