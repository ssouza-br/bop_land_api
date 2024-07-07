from typing import List
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import TesteModel, Preventor, Valvula, Base
from repositories.teste_repository import TesteRepository
from repositories.bop_repository import BOPRepository
from config import TestConfig
from exceptions.repository_error import RepositoryError


@pytest.fixture(scope="module")
def engine():
    return create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))

    yield session

    session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture
def teste_repo(session):
    return TesteRepository(session)


@pytest.fixture
def bop_repo(session):
    return BOPRepository(session)


@pytest.fixture
def setup_bop_and_teste(teste_repo, bop_repo):
    # Setup BOP
    bop_data = {
        "sonda": "sonda 1",
        "valvulas": ["val1", "val2", "val3"],
        "preventores": ["prev1", "prev2", "prev3"],
    }
    bop = bop_repo.add(bop_data)

    # Setup Teste
    teste_data = {
        "bopId": bop.id,
        "nome": "teste 1",
        "valvulasTestadas": [1, 2, 3],
        "preventoresTestados": [2, 3],
    }
    teste = teste_repo.add(teste_data)

    return bop, teste


def test_add_teste(teste_repo, setup_bop_and_teste):
    bop, _ = setup_bop_and_teste
    teste_data = {
        "bopId": bop.id,
        "nome": "teste 2",
        "valvulasTestadas": [1, 2, 3],
        "preventoresTestados": [2, 3],
    }

    teste = teste_repo.add(teste_data)
    assert teste.nome == teste_data["nome"]
    assert assertValves(teste.valvulas_testadas, teste_data["valvulasTestadas"])
    assert assertPreventors(
        teste.preventores_testados, teste_data["preventoresTestados"]
    )


def test_add_duplicate_teste(teste_repo):
    teste_data = {
        "bopId": 1,
        "nome": "teste 2",
        "valvulasTestadas": [1, 2, 3],
        "preventoresTestados": [2, 3],
    }

    with pytest.raises(RepositoryError):
        teste_repo.add(teste_data)


def test_list_testes_em_andamento(teste_repo, setup_bop_and_teste):
    bop, teste1 = setup_bop_and_teste

    teste_data_2 = {
        "bopId": bop.id,
        "nome": "teste 2",
        "valvulasTestadas": [1],
        "preventoresTestados": [2],
    }
    teste2 = teste_repo.add(teste_data_2)

    testes = teste_repo.lista_pelo_status(
        bopId=bop.id, status="em_andamento", pagina=1, por_pagina=2
    )
    assert len(testes["data"]) == 2
    assert testes["data"][0] == teste1.dict()
    assert testes["data"][1] == teste2.dict()


def test_delete_bop(teste_repo, setup_bop_and_teste):
    _, teste = setup_bop_and_teste
    teste_id = teste.id

    result = teste_repo.delete(teste_id)
    assert result is True

    deleted_teste = teste_repo.session.get(TesteModel, teste_id)
    assert deleted_teste is None


def assertValves(original: List[Valvula], resultado: List[int]):
    return [valv.id for valv in original] == resultado


def assertPreventors(original: List[Preventor], resultado: List[int]):
    return [prev.id for prev in original] == resultado
