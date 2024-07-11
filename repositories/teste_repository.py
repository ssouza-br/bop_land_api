from math import ceil
from typing import Dict, Optional
from models.teste import TestStatus
from specifications.testeSpec import (
    AprovadorIdSpecification,
    BopIdSpecification,
    StatusSpecification,
)
from schemas.teste import TesteSchema
from exceptions.repository_error import RepositoryError
from models import Preventor, Valvula, TesteModel, BOP as BOPModel
from sqlalchemy import and_, desc, exc


class TesteRepository:
    def __init__(self, session):
        self.session = session

    def add(self, teste: TesteSchema):
        bop_id, nome, valvulas_testadas, preventores_testados = (
            teste["bopId"],
            teste["nome"],
            teste["valvulasTestadas"],
            teste["preventoresTestados"],
        )

        bop = self.session.query(BOPModel).filter(BOPModel.id == bop_id).first()
        if not bop:
            raise RepositoryError("BOP id inválido")

        new_teste = TesteModel(nome=nome, bop_id=bop_id)

        # buscando as válvulas existentes por id na base
        valvulas_existentes = (
            self.session.query(Valvula)
            .filter(and_(Valvula.id.in_(valvulas_testadas), Valvula.bop_id == bop_id))
            .all()
        )

        valvulas_existentes_id = [vlv.id for vlv in valvulas_existentes]
        if set(valvulas_existentes_id) != set(valvulas_testadas):
            raise RepositoryError("Id de válvula testada não pertence a esse BOP :/")

        # buscando os preventores existentes por id na base
        preventores_existentes = (
            self.session.query(Preventor)
            .filter(
                and_(Preventor.id.in_(preventores_testados), Preventor.bop_id == bop_id)
            )
            .all()
        )
        preventores_existentes_id = [prv.id for prv in preventores_existentes]
        if set(preventores_existentes_id) != set(preventores_testados):
            raise RepositoryError("Id de preventor testada não pertence a esse BOP :/")

        # adicionando as válvulas ao Teste criado acima
        for valvula in valvulas_existentes:
            new_teste.valvulas_testadas.append(valvula)

        # adicionando os preventores ao Teste criado acima
        for preventor in preventores_existentes:
            new_teste.preventores_testados.append(preventor)

        self.session.add(new_teste)

        try:
            self.session.commit()
            return new_teste
        except exc.IntegrityError as e:
            self.session.rollback()
            raise RepositoryError("Teste dessa sonda já salvo na base :/")
        except Exception:
            # caso um erro fora do previsto
            raise RepositoryError("Não foi possível salvar novo Teste :/")

    def delete(self, teste_id):
        teste: TesteModel = self.session.get(TesteModel, teste_id)
        if teste:
            if teste.status == TestStatus.APROVADO:
                raise RepositoryError("Não é possível deletar um teste aprovado")
            else:
                # deletando as válvulas associadas ao teste em questão
                self.del_valvulas(teste_id)
                # deletando os preventores associados ao teste em questão
                self.del_preventores(teste_id)

                self.session.delete(teste)
                self.session.commit()
        else:
            raise RepositoryError("Teste id inválido")

    def listar(
        self,
        status: Optional[str] = None,
        bopId: Optional[int] = None,
        aprovadorId: Optional[int] = None,
        pagina=1,
        por_pagina=3,
    ) -> Dict:
        offset = (pagina - 1) * por_pagina

        query = self.session.query(TesteModel)

        # Apply status specification
        if status is not None:
            status_specification = StatusSpecification(status)
            query = status_specification.is_satisfied_by(query)

        # Apply bopId specification
        if bopId is not None:
            bopid_specification = BopIdSpecification(bopId)
            query = bopid_specification.is_satisfied_by(query)

        # Apply aprovadorId specification
        if aprovadorId is not None:
            aprovadorid_specification = AprovadorIdSpecification(aprovadorId)
            query = aprovadorid_specification.is_satisfied_by(query)

        if status == "APROVADO":
            query = query.order_by(desc(TesteModel.data_aprovacao))
        else:
            query = query.order_by(TesteModel.nome)

        total_registros = query.count()
        query = query.limit(por_pagina).offset(offset)

        testes = query.all()

        dados_paginados = []
        for teste in testes:
            dados_paginados.append(teste.dict())

        # Paginate results
        total_paginas = ceil(total_registros / por_pagina)
        tem_proximo = pagina < total_paginas
        tem_anterior = pagina > 1

        return {
            "data": dados_paginados,
            "pagination": {
                "total_paginas": total_paginas,
                "total_registros": total_registros,
                "pagina_atual": pagina,
                "tem_proximo": tem_proximo,
                "tem_anterior": tem_anterior,
            },
        }

    def del_valvulas(self, teste_id):
        # encontrando as válvulas associadas ao Teste em questão
        valvulas = (
            self.session.query(Valvula).filter(Valvula.teste_id == teste_id).all()
        )

        # deletando válvula por válvula associada a esse Teste
        [
            self.session.query(Valvula).filter(Valvula.id == v.id).delete()
            for v in valvulas
        ]
        self.session.commit()

    def del_preventores(self, teste_id):
        # encontrando os preventores associadas ao Teste em questão
        preventores = (
            self.session.query(Preventor).filter(Preventor.teste_id == teste_id).all()
        )

        # deletando preventor por preventor associada a esse Teste
        [
            self.session.query(Preventor).filter(Preventor.id == p.id).delete()
            for p in preventores
        ]
        self.session.commit()
