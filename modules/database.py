"""
Módulo de Banco de Dados (Database Engine)
------------------------------------------
Gerencia a conexão com o SQLite e fornece a sessão do SQLAlchemy.
Implementa o padrão Singleton para conexão.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_PATH

# Base declarativa para os Models herdarem
Base = declarative_base()

class DatabaseEngine:
    """
    Gerenciador de Conexão com Banco de Dados.
    Responsável por inicializar o engine e prover sessões.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa o Engine SQLite"""
        # check_same_thread=False é necessário para SQLite com Streamlit/Multithreading
        connection_url = f"sqlite:///{DB_PATH}"
        self.engine = create_engine(connection_url, connect_args={"check_same_thread": False}, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def get_db(self):
        """Dependency Injection para obter sessão de banco"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    def init_tables(self):
        """Cria as tabelas no banco de dados se não existirem"""
        # Importar models aqui para garantir que Base conheça eles antes do create_all
        import modules.models
        Base.metadata.create_all(bind=self.engine)

# Instância Global
db_engine = DatabaseEngine()
