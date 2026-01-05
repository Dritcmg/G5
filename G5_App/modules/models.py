"""
Módulo de Modelos de Dados (ORM Models)
---------------------------------------
Define a estrutura das tabelas usando SQLAlchemy.
Entidades: Atleta, Treino, Frequencia (Performance).
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Float, Text
from sqlalchemy.orm import relationship
from modules.database import Base
import datetime

class Atleta(Base):
    """
    Representa um Atleta no sistema.
    """
    __tablename__ = "atletas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    posicao = Column(String, nullable=True) # Ex: Goleiro, Atacante
    status = Column(String, default="ATIVO") # ATIVO, INATIVO
    contato_pais = Column(String, nullable=True)
    obs = Column(Text, nullable=True)
    foto_path = Column(String, nullable=True)
    
    # Relationships
    performances = relationship("Performance", back_populates="atleta", cascade="all, delete-orphan")
    
    @property
    def idade(self):
        """Calcula idade baseado no ano atual"""
        today = datetime.date.today()
        return today.year - self.data_nascimento.year

    @property
    def categoria_calculada(self):
        """Retorna a categoria (ex: Sub 14) baseado na configuração de anos"""
        from config import CATEGORY_RULES
        ano_nasc = self.data_nascimento.year
        for cat, anos in CATEGORY_RULES.items():
            if ano_nasc in anos:
                return cat
        return "Sem Categoria"

    def __repr__(self):
        return f"<Atleta(nome={self.nome}, cat={self.categoria_calculada})>"


class Treino(Base):
    """
    Representa uma Sessão de Treino Diária.
    Pode ter múltiplos tipos (Físico, Técnico) mas aqui simplificamos para 
    uma sessão principal com flags de tipos.
    """
    __tablename__ = "treinos"
    
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)
    categoria_alvo = Column(String, nullable=False) # Ex: Sub 14
    
    # Avaliação Geral do Treino pelo Treinador
    flag_geral = Column(String, nullable=True) # 1-3, FO, AM, CH (Legenda Treino)
    obs_geral = Column(Text, nullable=True)
    
    # Checklist de Tipos (Armazenado como string separada por virgula ou JSON simples)
    # Ex: "Físico,Tático"
    tipos_realizados = Column(String, default="") 
    
    # Relationships
    performances = relationship("Performance", back_populates="treino", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Treino(data={self.data}, cat={self.categoria_alvo})>"


class Performance(Base):
    """
    Registro Individual de Performance/Frequência de um Atleta em um Treino.
    Tabela de junção entre Atleta e Treino com atributos extras.
    """
    __tablename__ = "performances"
    
    id = Column(Integer, primary_key=True, index=True)
    treino_id = Column(Integer, ForeignKey("treinos.id"), nullable=False)
    atleta_id = Column(Integer, ForeignKey("atletas.id"), nullable=False)
    
    # Dados de Performance
    presenca = Column(String, default="P") # P=Presente, F=Falta, J=Justificada
    nota = Column(Integer, nullable=True) # 1, 2, 3
    flag_atleta = Column(String, nullable=True) # Flag específica (DM, Destacou...)
    obs_individual = Column(String, nullable=True)
    
    # Relationships
    treino = relationship("Treino", back_populates="performances")
    atleta = relationship("Atleta", back_populates="performances")
    
    def __repr__(self):
        return f"<Perf(atleta={self.atleta_id}, nota={self.nota})>"
