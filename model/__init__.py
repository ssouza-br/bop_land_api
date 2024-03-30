from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# importando os elementos definidos no modelo
from model.base import Base
from model.bop import BOP
from model.usuario import Usuario
from model.valvula import Valvula
from model.preventor import Preventor


def load_initial_data(session):
    # cria um usuário
    usuario = Usuario(nome='admin', email='admin@admin.com', senha='12345')
    # cria uma instancia de BOP    
    bop = BOP('NSXX')
     
    # adiciona instancias de válvulas ao BOP   
    valvulas = ['LICHOKE', 'LOCHOKE', 'MICHOKE','MOCHOKE', 'UICHOKE', 'UOCHOKE', 'LIKILL', 'LOKILL', 'MIKILL', 'MOKILL', 'UIKILL', 'UOKILL', 'IGUANNULAR', 'IGLANNULAR', 'OGUANNULAR', 'OGLANNULAR']
    [bop.adiciona_valvula(Valvula(acronimo=v)) for v in valvulas]
    
    # adiciona instancias de prevntores ao BOP   
    preventores = ['TPIPERAM','LPIPERAM','MPIPERAM','UPIPERAM','LBSR','UBSR','LANNULAR','UANNULAR']
    [bop.adiciona_preventor(Preventor(acronimo=p)) for p in preventores]
    
    bop2 = BOP('NSYY')
     
    # adiciona instancias de válvulas ao BOP   
    valvulas = ['LICHOKE', 'LOCHOKE', 'MICHOKE','MOCHOKE', 'UICHOKE', 'UOCHOKE', 'LIKILL', 'LOKILL', 'UIKILL', 'UOKILL', 'IGUANNULAR', 'IGLANNULAR', 'OGUANNULAR', 'OGLANNULAR']
    [bop2.adiciona_valvula(Valvula(acronimo=v)) for v in valvulas]
    
    # adiciona instancias de prevntores ao 2   
    preventores = ['LPIPERAM','MPIPERAM','UPIPERAM','LBSR','UBSR','LANNULAR','UANNULAR']
    [bop2.adiciona_preventor(Preventor(acronimo=p)) for p in preventores]
    
    session.add_all([bop, bop2, usuario])
    session.commit()
    

db_path = "database/"
# Verifica se o diretorio não existe
if not os.path.exists(db_path):
   # então cria o diretorio
   os.makedirs(db_path)
   initial_load_needed = True

db_file = 'db.sqlite3'   
if not os.path.isfile(db_path + db_file):
    initial_load_needed = True
else:
    initial_load_needed = False

# url de acesso ao banco (essa é uma url de acesso ao sqlite local)
db_url = 'sqlite:///%s/db.sqlite3' % db_path

# cria a engine de conexão com o banco
engine = create_engine(db_url, echo=False)

# Instancia um criador de seção com o banco
Session = sessionmaker(bind=engine)
session = Session()

if initial_load_needed:
    # cria o banco se ele não existir 
    create_database(engine.url) 
        
    # cria as tabelas do banco, caso não existam
    Base.metadata.create_all(engine)
    
    # carrega os dados iniciais
    load_initial_data(session)
else:
    print("Banco de dados já criado. Ignorando o carregamento inicial de dados.")