from datetime import datetime
from typing import List, Optional

from models.preventor import Preventor
from models.teste import Teste
from models.valvula import Valvula


class BOP:
    def __init__(self, sonda: str, valvulas: List[Valvula], preventores: List[Preventor], testes: List[Teste]):
        self.sonda = sonda
        self.valvulas = valvulas
        self.preventores = preventores
        self.testes = testes


    def dict(self):
        return {
            "sonda": self.sonda,
            "valvulas": self.valvulas,
            "preventores": self.preventores,
            "testes": self.testes,
        }