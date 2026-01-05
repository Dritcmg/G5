"""
Módulo de Serviços (Business Logic)
-----------------------------------
Contém a lógica de negócio, interações com o banco de dados (CRUD) e algoritmos de controle.
"""

from sqlalchemy.orm import Session
from modules.models import Atleta, Treino, Performance
from datetime import date
import pandas as pd
from typing import List, Optional

class AtletaService:
    """Serviços relacionados a gestão de Atletas"""
    
    def __init__(self, db: Session):
        self.db = db

    def criar_atleta(self, nome: str, data_nasc: date, posicao: str, contato: str = "") -> Atleta:
        atleta = Atleta(nome=nome, data_nascimento=data_nasc, posicao=posicao, contato_pais=contato)
        self.db.add(atleta)
        self.db.commit()
        self.db.refresh(atleta)
        return atleta

    def listar_atletas(self, ativo_only: bool = True) -> List[Atleta]:
        query = self.db.query(Atleta)
        if ativo_only:
            query = query.filter(Atleta.status == "ATIVO")
        return query.all()

    def filtrar_por_categoria(self, categoria: str) -> List[Atleta]:
        """
        Filtra atletas dinamicamente baseado em sua Data de Nascimento e na Categoria Alvo.
        Lógica Python side (devido ao cálculo dinâmico de categoria).
        """
        todos = self.listar_atletas(ativo_only=True)
        # Filtra na memória (poderia ser query se categoria fosse campo persistido)
        return [a for a in todos if a.categoria_calculada == categoria]

    def get_atleta(self, atleta_id: int) -> Optional[Atleta]:
        return self.db.query(Atleta).filter(Atleta.id == atleta_id).first()


class TreinoService:
    """Serviços relacionados a Treinos e Performance"""
    
    def __init__(self, db: Session):
        self.db = db
        self.atleta_service = AtletaService(db)

    def criar_sessao_treino(self, data_treino: date, categoria: str, tipos: List[str]) -> Treino:
        """Cria e inicializa um treino novo"""
        # Verifica duplicidade
        existente = self.db.query(Treino).filter(Treino.data == data_treino, Treino.categoria_alvo == categoria).first()
        if existente:
            return existente # Retorna o já existente para edição
            
        tipos_str = ",".join(tipos)
        novo_treino = Treino(data=data_treino, categoria_alvo=categoria, tipos_realizados=tipos_str)
        self.db.add(novo_treino)
        self.db.commit()
        self.db.refresh(novo_treino)
        
        # Inicializa performances vazias para todos os atletas da categoria
        atletas = self.atleta_service.filtrar_por_categoria(categoria)
        for atl in atletas:
            perf = Performance(treino_id=novo_treino.id, atleta_id=atl.id, presenca="P") # Default Presente
            self.db.add(perf)
        self.db.commit()
        
        return novo_treino

    def get_treino_do_dia(self, data_ref: date, categoria: str) -> Optional[Treino]:
        return self.db.query(Treino).filter(Treino.data == data_ref, Treino.categoria_alvo == categoria).first()

    def atualizar_performance(self, perf_id: int, nota: int, flag: str, presenca: str):
        perf = self.db.query(Performance).filter(Performance.id == perf_id).first()
        if perf:
            perf.nota = nota
            perf.flag_atleta = flag
            perf.presenca = presenca
            self.db.commit()
            
    def salvar_avaliacao_geral(self, treino_id: int, flag: str, obs: str):
        treino = self.db.query(Treino).filter(Treino.id == treino_id).first()
        if treino:
            treino.flag_geral = flag
            treino.obs_geral = obs
            self.db.commit()

    def get_dataframe_performances(self, categoria: str) -> pd.DataFrame:
        """Retorna DataFrame pandas para Analytics"""
        # Join complexo
        results = self.db.query(
            Performance.id,
            Atleta.nome,
            Treino.data,
            Performance.nota,
            Performance.presenca,
            Performance.flag_atleta
        ).join(Treino).join(Atleta).filter(Treino.categoria_alvo == categoria).all()
        
        if not results:
            return pd.DataFrame()
            
        df = pd.DataFrame(results, columns=['id', 'atleta', 'data', 'nota', 'presenca', 'flag'])
        df['data'] = pd.to_datetime(df['data'])
        return df
