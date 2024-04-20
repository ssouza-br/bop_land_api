from math import ceil
from zoneinfo import ZoneInfo
from flask import jsonify, request
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy import desc, exc

from model import Session
from model.bop import BOP
from model.preventor import Preventor
from model.teste import Teste
from model.usuario import Usuario
from model.valvula import Valvula
from schemas.error import ErrorSchema
from schemas.teste import AprovaTesteSchema, ListagemTestesSchema, StatusEnum, TesteBuscaSchema, TesteViewSchema, apresenta_testes
from datetime import datetime

teste_tag = Tag(name="Teste", description="Adição e visualização de testes à base")
security = [{"jwt": []}]

bp = APIBlueprint('teste',
                  __name__, 
                  url_prefix='/teste', 
                  abp_tags=[teste_tag], 
                  abp_security=security,
                  abp_responses={"400": ErrorSchema, "409": ErrorSchema}, 
                  doc_ui=True)
CORS(bp, supports_credentials=True)

@bp.post('/', responses={"200": TesteViewSchema})
@jwt_required()
def add_teste():
    """Adiciona um novo Teste a base de dados

    Retorna uma representação do teste recém adicionado com válvulas e preventores testados.
    """
    data = request.get_json() 
    if not data:
        return jsonify({"mensagem": "No JSON data provided"}), 400
    
    nome = data.get('nome')
    bop_id = data.get('bop_id')
    valvulas_testadas = data.get('valvulas_testadas', [])
    preventores_testados = data.get('preventores_testados', [])
    
    valvula_ids = [valvula.get('id') for valvula in valvulas_testadas]
    preventor_ids = [preventor.get('id') for preventor in preventores_testados]
    
    # criando um Teste
    teste = Teste(nome=nome, bop_id=bop_id)

    # criando conexão com a base
    session = Session()
    
    # buscando as válvulas existentes por id na base
    valvulas_existentes = session.query(Valvula).filter(Valvula.id.in_(valvula_ids)).all()
    
    # buscando os preventores existentes por id na base
    preventores_existentes = session.query(Preventor).filter(Preventor.id.in_(preventor_ids)).all()

    # adicionando as válvulas ao Teste criado acima
    for valvula in valvulas_existentes:
        teste.valvulas_testadas.append(valvula)
    
    # adicionando os preventores ao Teste criado acima
    for preventor in preventores_existentes:
        teste.preventores_testados.append(preventor)
        
    try:
        # adicionando teste
        session.add(teste)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        return apresenta_testes([teste]), 200

    except exc.IntegrityError:
        session.rollback()
        # como a duplicidade do nome para o mesmo bop_id é a provável razão do IntegrityError
        error_msg = "Teste já salvo na base :/"
        return {"mensagem": error_msg}, 409

    except Exception:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo teste :/"
        return {"mensagem": error_msg}, 400
    
@bp.get('/', responses={"200": ListagemTestesSchema})
@jwt_required()
def get_teste(query: TesteBuscaSchema):
    """Faz a busca por todos os Testes presentes no sistema, a partir do seu status no sistema: aprovado ou em_andamento

    Retorna uma representação dos Testes.
    """
    # criando conexão com a base
    session = Session()

    status, pagina, por_pagina = query.status, query.pagina, query.por_pagina
    # Realiza a paginação de forma manual
    offset = (pagina - 1) * por_pagina
    
    # lista os testes a partir do status
    # aprovado, caso haja data no campo data_aprovacao
    if(status == StatusEnum.aprovado):
        # coletando todos os registros de testes aprovados
        testes = session.query(Teste).order_by(desc(Teste.data_aprovacao)).filter(Teste.data_aprovacao != None).offset(offset).limit(por_pagina).all()
        # calcula o total de registros
        total_registros = session.query(Teste).filter(Teste.data_aprovacao != None).count()
        
        # pegando o nome do aprovador pelo usuario_id
        result = []
        for teste in testes:
            bop = session.query(BOP).filter(BOP.id == teste.bop_id).first()
            aprovador = session.query(Usuario).filter(Usuario.id == teste.aprovador_id).first() if teste.aprovador_id else None
            
            teste_data = {
                'id': teste.id,
                'nome': teste.nome,
                'sonda': bop.sonda,
                'aprovador': aprovador.nome,
                'data_aprovacao': teste.data_aprovacao,
                'valvulas_testadas': [v.acronimo for v in teste.valvulas_testadas],
                'preventores_testados': [p.acronimo for p in teste.preventores_testados]
            }
            result.append(teste_data)
    # em_andamento caso contrário 
    elif(status == StatusEnum.em_andamento):
        testes = session.query(Teste).order_by(desc(Teste.data_aprovacao)).filter(Teste.data_aprovacao == None).offset(offset).limit(por_pagina).all()
        # calcula o total de registros
        total_registros = session.query(Teste).filter(Teste.data_aprovacao == None).count()
        
        result = []
        for teste in testes:
            bop = session.query(BOP).filter(BOP.id == teste.bop_id).first()
               
            teste_data = {
                'id': teste.id,
                'nome': teste.nome,
                'sonda': bop.sonda,
                'valvulas_testadas': [v.acronimo for v in teste.valvulas_testadas],
                'preventores_testados': [p.acronimo for p in teste.preventores_testados]
            }
            result.append(teste_data)

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
        "items": {"content": result}
    }, 200
    

@bp.put('/aprovar', responses={"200": ListagemTestesSchema})
@jwt_required()
def aprovar_teste(query: AprovaTesteSchema):
    """Aprova um teste a partir do seu id
    """
    # criando conexão com a base
    session = Session()
    
    teste_id = query.id
    # pegando o usuário que aprovou o teste
    current_user = get_jwt_identity()
    aprovador = session.query(Usuario).filter_by(email=current_user).first()

    teste = session.query(Teste).filter(Teste.id == teste_id).first()
    if teste:
        # atribuindo o id do aprovador ao teste
        teste.aprovador_id = aprovador.id
        
        #atribuindo a data da aprovação
        teste.data_aprovacao = datetime.now(ZoneInfo("America/Sao_Paulo"))
        
        session.commit()
    else:
        # caso um erro fora do previsto
        error_msg = "Teste não encontrado no sistema :/"
        return {"mensagem": error_msg}, 400
    
    # retorna a representação de bop paginada
    return {
        "teste_id": teste_id,
        "aprovador": aprovador.nome,
        "data_aprovacao": teste.data_aprovacao
    }, 200