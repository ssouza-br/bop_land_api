from typing import List
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from models.preventor import Preventor
from models.valvula import Valvula
from models import BOP, Base
from repositories.bop_repository import BOPRepository
from config import TestConfig
from exceptions.repository_error import RepositoryError
from datetime import datetime

@pytest.fixture(scope='module')
def engine():
    return create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)

@pytest.fixture(scope='module')
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
def bop_repo(session):
    return BOPRepository(session)

def test_add_bop(bop_repo):
    bop_data = {
            "sonda": "sonda 1",
            "valvulas": ["val1", "val2", "val3"],
            "preventores": ["prev1", "prev2", "prev3"],
    }
    bop = bop_repo.add(bop_data)
    assert bop.sonda == bop_data['sonda']
    assert assertValves(bop.valvulas, bop_data['valvulas']) 
    assert assertPreventors(bop.preventores, bop_data['preventores'])

def test_add_duplicate_bop(bop_repo):
    bop_data = {
            "sonda": "sonda 1",
            "valvulas": ["val1", "val2", "val3"],
            "preventores": ["prev1", "prev2", "prev3"],
    }
    bop_repo.add(bop_data)

    with pytest.raises(RepositoryError):
        bop_repo.add(bop_data)

def test_list_bops(bop_repo):
    bop_data_1 = {
            "sonda": "sonda 1",
            "valvulas": ["val1", "val2", "val3"],
            "preventores": ["prev1", "prev2", "prev3"],
    }
    bop_data_2 = {
            "sonda": "sonda 2",
            "valvulas": ["val3", "val4"],
            "preventores": ["prev3"],
    }
    bop_repo.add(bop_data_1)
    bop_repo.add(bop_data_2)

    bops = bop_repo.list(sonda='', pagina=1, por_pagina=2)
    assert len(bops['dado']) == 2

def test_search_by_sonda_name(bop_repo):
    bop_data_1 = {
            "sonda": "sonda 1",
            "valvulas": ["val1", "val2", "val3"],
            "preventores": ["prev1", "prev2", "prev3"],
    }
    bop_data_2 = {
            "sonda": "sonda 2",
            "valvulas": ["val3", "val4"],
            "preventores": ["prev3"],
    }
    bop1 = bop_repo.add(bop_data_1)
    bop2 = bop_repo.add(bop_data_2)

    bops = bop_repo.list(sonda='sonda')
    assert bops['dado'][0] == bop1.dict()
    assert bops['dado'][1] == bop2.dict()

def test_delete_bop(bop_repo):
    bop_data = {
            "sonda": "sonda 1",
            "valvulas": ["val1", "val2", "val3"],
            "preventores": ["prev1", "prev2", "prev3"],
    }
    bop = bop_repo.add(bop_data)
    bop_id = bop.id

    result = bop_repo.delete(bop_id)
    assert result is True

    deleted_bop = bop_repo.session.query(BOP).get(bop_id)
    assert deleted_bop is None
    
def assertValves(original: List[Valvula], resultado: List[str]):
    return [valv.acronimo for valv in original] == resultado

def assertPreventors(original: List[Preventor], resultado: List[str]):
    return [prev.acronimo for prev in original] == resultado
