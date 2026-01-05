"""
Módulo de Analytics (Data Science)
----------------------------------
Responsável por cálculos estatísticos, rankings e detecção de padrões.
"""

import pandas as pd
import numpy as np

class AnalyticsEngine:
    
    @staticmethod
    def calcular_kpis_atleta(df_performances: pd.DataFrame, atleta_nome: str):
        """Calcula KPIs individuais para o dashboard"""
        df = df_performances[df_performances['atleta'] == atleta_nome].sort_values('data')
        
        if df.empty:
            return None
            
        total_treinos = len(df)
        presencas = len(df[df['presenca'] == 'P'])
        freq = (presencas / total_treinos) * 100 if total_treinos > 0 else 0
        
        # Média de notas (ignora NaNs)
        media_notas = df['nota'].mean()
        
        # Tendência (Últimos 5 treinos vs Anterior)
        last_5 = df.tail(5)
        media_recente = last_5['nota'].mean()
        
        return {
            "Total Treinos": total_treinos,
            "Frequência (%)": round(freq, 1),
            "Média Geral": round(media_notas, 2),
            "Média Recente (5)": round(media_recente, 2),
            "Tendência": "⬆️" if media_recente > media_notas else "⬇️"
        }

    @staticmethod
    def gerar_ranking_evolucao(df_all: pd.DataFrame):
        """
        Gera um ranking baseado na consistência (Desvio Padrão Inverso) e Média.
        Top Evolução = Alta Média + Baixo Desvio Padrão.
        """
        if df_all.empty:
            return pd.DataFrame()
            
        # Agrupa por atleta
        stats = df_all.groupby('atleta')['nota'].agg(['mean', 'std', 'count']).reset_index()
        stats = stats[stats['count'] >= 3] # Mínimo 3 treinos para ranking
        
        stats['std'] = stats['std'].fillna(0) # Se só 1 treino, std é NaN
        
        # Score = Média * (1 - (StdDev / 5)) -> Penaliza instabilidade
        stats['Score G5'] = stats['mean'] * (1 - (stats['std'] / 10))
        
        return stats.sort_values('Score G5', ascending=False).head(10)

    @staticmethod
    def alertas_criticos(df_all: pd.DataFrame):
        """Retorna lista de atletas que precisam de atenção (Faltas > 3 ou Média < 1.5)"""
        if df_all.empty:
            return []
            
        alertas = []
        for atleta in df_all['atleta'].unique():
            df_g = df_all[df_all['atleta'] == atleta]
            
            # Checa Faltas
            faltas = len(df_g[df_g['presenca'] == 'F'])
            if faltas >= 3:
                alertas.append({"atleta": atleta, "tipo": "Faltas", "msg": f"{faltas} Faltas registradas"})
                
            # Checa Notas Baixas Recentes
            last_3 = df_g.tail(3)
            if not last_3.empty and last_3['nota'].mean() < 1.8:
                alertas.append({"atleta": atleta, "tipo": "Performance", "msg": "Média recente crítica (< 1.8)"})
                
        return alertas
