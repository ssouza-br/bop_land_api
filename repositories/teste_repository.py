from math import ceil
from typing import List
from schemas.teste import StatusEnum, TesteSchema
from exceptions.repository_error import RepositoryError
from models import (
    Preventor,
    Valvula,
    TesteModel,
    BOP as BOPModel,
    Usuario as UsuarioModel,
)
from sqlalchemy import desc, exc


class TesteRepository:
    def __init__(self, session):
        self.session = session

    def add(self, teste: TesteSchema):
        bop_id, nome, valvulas_testadas, preventores_testados = (
            teste["bop_id"],
            teste["nome"],
            teste["valvulas_testadas"],
            teste["preventores_testados"],
        )

        bop = self.session.query(BOPModel).filter(BOPModel.id == bop_id).first()
        if not bop:
            raise RepositoryError("BOP id inválido")

        # print(bop_id, nome, valvulas_testadas, preventores_testados)

        new_teste = TesteModel(nome=nome, bop_id=bop_id)

        # buscando as válvulas existentes por id na base
        valvulas_existentes = (
            self.session.query(Valvula).filter(Valvula.id.in_(valvulas_testadas)).all()
        )

        valvulas_existentes_id = [vlv.id for vlv in valvulas_existentes]

        if valvulas_existentes_id != valvulas_testadas:
            raise RepositoryError("Id de válvula testada não pertence a esse BOP :/")

        # buscando os preventores existentes por id na base
        preventores_existentes = (
            self.session.query(Preventor)
            .filter(Preventor.id.in_(preventores_testados))
            .all()
        )
        preventores_existentes_id = [prv.id for prv in preventores_existentes]
        if preventores_existentes_id != preventores_testados:
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
        teste = self.session.get(TesteModel, teste_id)
        if teste:
            # deletando as válvulas associadas ao teste em questão
            self.del_valvulas(teste_id)
            # deletando os preventores associados ao teste em questão
            self.del_preventores(teste_id)

            self.session.delete(teste)
            self.session.commit()
            return True
        return False

    def lista_pelo_status(self, status: str, pagina=1, por_pagina=3):
        # status, pagina, por_pagina = (
        #     teste["status"],
        #     teste["pagina"],
        #     teste["por_pagina"],
        # )
        offset = (pagina - 1) * por_pagina

        query = self.session.query(TesteModel)

        # lista os testes a partir do status
        # aprovado, caso haja data no campo data_aprovacao
        if status == StatusEnum.aprovado:
            # coletando todos os registros de testes aprovados
            testes = (
                query.order_by(desc(TesteModel.data_aprovacao))
                .filter(TesteModel.data_aprovacao != None)
                .offset(offset)
                .limit(por_pagina)
                .all()
            )
            # calcula o total de registros
            total_registros = query.filter(TesteModel.data_aprovacao != None).count()

            # pegando o nome do aprovador pelo usuario_id
            dados_paginados = []
            for teste in testes:
                aprovador = (
                    self.session.query(UsuarioModel)
                    .filter(UsuarioModel.id == teste.aprovador_id)
                    .first()
                    if teste.aprovador_id
                    else None
                )
                dados_paginados.append(teste.dict())
        # em_andamento caso contrário
        elif status == StatusEnum.em_andamento:
            testes = (
                query.order_by(desc(TesteModel.data_aprovacao))
                .filter(TesteModel.data_aprovacao == None)
                .offset(offset)
                .limit(por_pagina)
                .all()
            )
            # calcula o total de registros
            total_registros = query.filter(TesteModel.data_aprovacao == None).count()

            dados_paginados = []
            for teste in testes:
                dados_paginados.append(teste.dict())

        else:
            raise NameError
        # Calcula o total de páginas
        total_paginas = ceil(total_registros / por_pagina)

        # Calcula se tem próxima página
        tem_proximo = pagina < total_paginas

        # Calcula se tem página anterior
        tem_anterior = pagina > 1

        # Calcula a página atual
        pagina_atual = pagina

        # retorna a representação de bop paginada
        return {
            "dado": dados_paginados,
            "paginacao": {
                "total_paginas": total_paginas,
                "total_registros": total_registros,
                "pagina_atual": pagina_atual,
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
