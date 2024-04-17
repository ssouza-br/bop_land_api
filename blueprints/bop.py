from math import ceil
from urllib.parse import unquote
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy import exc

from model import Session
from model.bop import BOP
from model.preventor import Preventor
from model.valvula import Valvula
from schemas.bop import BOPBuscaSchema, BOPDelSchema, BOPViewSchema, ListagemBOPsSchema, ListagemSondasSchema, apresenta_bops
from schemas.error import ErrorSchema

bop_tag = Tag(name="BOP", description="Adição, visualização e remoção de BOPs à base")
security = [{"jwt": []}]

bp = APIBlueprint('bop',
                  __name__, 
                  url_prefix='/bop', 
                  abp_tags=[bop_tag], 
                  abp_security=security,
                  abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
                  doc_ui=True)
CORS(bp, supports_credentials=True)

@bp.post('/', responses={"200": BOPViewSchema})
@jwt_required()
def add_bop(form: BOPViewSchema):
    """Adiciona um novo BOP a base de dados

    Retorna uma representação dos BOPs com válvulas e preventores associados.
    """
    sonda = form.sonda
    valvulas = form.valvulas
    preventores = form.preventores

    # criando um BOP
    bop = BOP(sonda=sonda)
    
    # adicionando as válvulas ao BOP criado acima
    [bop.adiciona_valvula(Valvula(v)) for v in valvulas]
    
    # adicionando os preventores ao BOP criado acima
    [bop.adiciona_preventor(Preventor(p)) for p in preventores]
    try:
        # criando conexão com a base
        session = Session()
        # adicionando bop
        session.add(bop)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        return apresenta_bops([bop]), 200

    except exc.IntegrityError:
        session.rollback()
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "BOP dessa sonda já salvo na base :/"
        return {"mensagem": error_msg}, 409

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo BOP :/"
        return {"mensagem": error_msg}, 400

@bp.get('/', responses={"200": ListagemBOPsSchema})
@jwt_required()
def get_bop(query: BOPBuscaSchema):
    """Faz a busca por um BOP do nome da sonda, caso esse campo fique vazio traz toda a lista de BOP do sistema

    Retorna uma representação dos BOPs, válvulas e preventores associados.
    """
    # criando conexão com a base
    session = Session()

    sonda, pagina, por_pagina = query.sonda, query.pagina, query.por_pagina
    if sonda:
        bop_sonda = sonda
        # fazendo a busca
        bop = session.query(BOP).filter(BOP.sonda.like(f'%{bop_sonda}%')).all()
        if not bop:
            # se o bop não foi encontrado
            error_msg = "BOP não encontrado na base :/"
            return {"mensagem": error_msg}, 404
        else:
            # calcula o total de registros
            total_registros = session.query(BOP).filter(BOP.sonda.like(f'%{bop_sonda}%')).count()

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
            "total_paginas": total_paginas,
            "total_registros": total_registros,
            "pagina_atual": pagina_atual,
            "tem_proximo": tem_proximo,
            "tem_anterior": tem_anterior,
            "items": apresenta_bops(bop)
        }, 200
    else:
        # trazendo os resultados paginados e em ordem alfabética por nome da sonda
        offset = (pagina - 1) * por_pagina
        bops = session.query(BOP).order_by(BOP.sonda).offset(offset).limit(por_pagina).all()
        
        # calcula o total de registros
        total_registros = session.query(BOP).count()

        # Calcula o total de páginas
        total_paginas = ceil(total_registros / por_pagina)

        # Calcula se tem próxima página
        tem_proximo = pagina < total_paginas

        # Calcula se tem página anterior
        tem_anterior = pagina > 1
        
        # Calcula a página atual
        pagina_atual = pagina

        # Realiza a paginaçaõ de forma manual
        offset = (pagina - 1) * por_pagina
        bops = session.query(BOP).order_by(BOP.sonda).offset(offset).limit(por_pagina).all()
        
        # retorna a representação de bop paginada
        return {
            "total_paginas": total_paginas,
            "total_registros": total_registros,
            "pagina_atual": pagina_atual,
            "tem_proximo": tem_proximo,
            "tem_anterior": tem_anterior,
            "items": apresenta_bops(bops)
        }, 200

@bp.delete('/', responses={"200": BOPDelSchema})
@jwt_required()
def del_bop(query: BOPBuscaSchema):
    """Deleta um BOP a partir do nome da sonda dona desse equipamento

    Retorna uma mensagem de confirmação da remoção.
    """
    bop_sonda = unquote(unquote(query.sonda))

    # criando conexão com a base
    session = Session()
    
    # encontrando o bop a ser deletado
    bop_id = session.query(BOP).filter(BOP.sonda == bop_sonda).first().id
    
    # deletando as válvulas associadas ao BOP em questão
    del_valvulas(bop_id)
    # deletando os preventores associados ao BOP em questão
    del_preventores(bop_id)
    
    # deletando o bop
    bop = session.query(BOP).filter(BOP.sonda == bop_sonda).delete()
    session.commit()

    if bop:
        # retorna a representação da mensagem de confirmação
        return {"mensagem": "BOP removido", "sonda": bop_sonda}
    else:
        # se o produto não foi encontrado
        error_msg = "BOP não encontrado na base :/"
        return {"mensagem": error_msg}, 404

@bp.get('/sondas', responses={"200": ListagemSondasSchema})
@jwt_required()
def get_sondas():
    """
    Retorna todas as sondas com BOPs salvos no sistema
    """
    # criando conexão com a base
    session = Session()

    # fazendo a busca
    bops = session.query(BOP).all()
            
    # retorna a representação de todas as sondas com BOP
    return {
    "items": [{"id": bop.id ,"sonda": bop.sonda} for bop in bops]
}, 200

def del_valvulas(bop_id):
    session = Session()
    
    # encontrando as válvulas associadas ao BOP em questão
    valvulas = session.query(Valvula).filter(Valvula.bop_id == bop_id).all()
    
    #deletando válvula por válvula associada a esse BOP
    [session.query(Valvula).filter(Valvula.id == v.id).delete() for v in valvulas]
    session.commit()

def del_preventores(bop_id):
    session = Session()
    
    # encontrando os preventores associadas ao BOP em questão
    preventores = session.query(Preventor).filter(Preventor.bop_id == bop_id).all()
    
    #deletando preventor por preventor associada a esse BOP
    [session.query(Preventor).filter(Preventor.id == p.id).delete() for p in preventores]
    session.commit()