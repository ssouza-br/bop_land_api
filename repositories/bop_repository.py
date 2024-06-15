from math import ceil
from typing import List
from schemas.bop import BOPSchema
from exceptions.repository_error import RepositoryError
from models import Preventor, Valvula, BOP as BOPModel
from sqlalchemy import exc

class BOPRepository:
    def __init__(self, session):
        self.session = session

    def add(self, bop:BOPSchema):
        sonda, valvulas, preventores = bop["sonda"], bop["valvulas"], bop["preventores"]
        
        new_bop = BOPModel(
            sonda=sonda,
        )
        
        # adicionando as válvulas ao BOP criado acima
        [new_bop.adiciona_valvula(Valvula(v)) for v in valvulas]
        
        # adicionando os preventores ao BOP criado acima
        [new_bop.adiciona_preventor(Preventor(p)) for p in preventores]
        
        self.session.add(new_bop)
        
        try:
            self.session.commit()
            return new_bop
        except exc.IntegrityError as e:
            self.session.rollback()
            raise RepositoryError("BOP dessa sonda já salvo na base :/")
        except Exception:
            # caso um erro fora do previsto
            raise RepositoryError("Não foi possível salvar novo BOP :/")
    
    def delete(self, bop_id):
        bop = self.session.query(BOPModel).get(bop_id)
        if bop:
            # deletando as válvulas associadas ao BOP em questão
            self.del_valvulas(bop_id)
            # deletando os preventores associados ao BOP em questão
            self.del_preventores(bop_id)
    
            self.session.delete(bop)
            self.session.commit()
            return True
        return False
    
    def list(self, sonda: str, pagina=1, por_pagina=3):
        offset = (pagina - 1) * por_pagina
        
        query = self.session.query(BOPModel)
        
        if sonda:
            query_filtrada = query.filter(BOPModel.sonda.ilike(f"%{sonda}%"))
            dados_paginados = query_filtrada.limit(por_pagina).offset(offset).all()
            total_registros = query_filtrada.count()
        
        else:
            dados_paginados = query.limit(por_pagina).offset(offset).all()
            total_registros = query.count()

        # Calcula o total de páginas
        total_paginas = ceil(total_registros / por_pagina)

        # Calcula se tem próxima página
        tem_proximo = pagina < total_paginas

        # Calcula se tem página anterior
        tem_anterior = pagina > 1
        
        # Calcula a página atual
        pagina_atual = pagina
        
        return {
            "dado": [bop.dict() for bop in dados_paginados],
            "paginacao": {
                        "total_paginas": total_paginas,
                        "total_registros": total_registros,
                        "pagina_atual": pagina_atual,
                        "tem_proximo": tem_proximo,
                        "tem_anterior": tem_anterior,
            }
        }
    
    def del_valvulas(self, bop_id):      
        # encontrando as válvulas associadas ao BOP em questão
        valvulas = self.session.query(Valvula).filter(Valvula.bop_id == bop_id).all()
        
        #deletando válvula por válvula associada a esse BOP
        [self.session.query(Valvula).filter(Valvula.id == v.id).delete() for v in valvulas]
        self.session.commit()

    def del_preventores(self, bop_id):      
        # encontrando os preventores associadas ao BOP em questão
        preventores = self.session.query(Preventor).filter(Preventor.bop_id == bop_id).all()
        
        #deletando preventor por preventor associada a esse BOP
        [self.session.query(Preventor).filter(Preventor.id == p.id).delete() for p in preventores]
        self.session.commit()
        