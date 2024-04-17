from flask import jsonify, request
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy import exc

from model import Session
from model.bop import BOP
from model.preventor import Preventor
from model.teste import Teste
from model.valvula import Valvula
from schemas.error import ErrorSchema
from schemas.teste import TesteViewSchema, apresenta_testes

teste_tag = Tag(name="teste", description="Adição e visualização de testes à base")
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