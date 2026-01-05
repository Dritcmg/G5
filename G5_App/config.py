"""
Módulo de Configuração (Config)
-------------------------------
Define constantes globais, paletas de cores e configurações do sistema G5 Futebol.
"""

import os
from datetime import datetime

# --- SYSTEM PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "g5_system.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- CATEGORIES LOGIC ---
CURRENT_YEAR = 2026
CATEGORY_RULES = {
    "Sub 17": [2009, 2010],
    "Sub 15": [2011],
    "Sub 14": [2012],
    "Sub 13": [2013],
    "Sub 12": [2014],
    "Sub 11": [2015],
    "Sub 10": [2016],
    "Sub 9":  [2017]
}

# --- TRAINING TYPES (ROWS) ---
TRAINING_TYPES = [
    "Físico", "Técnico", "Tático", "Vídeo", 
    "Coletivo", "Amistoso", "Paulista", "Academia",
    "Teste Físico", "Palestra", "Regenerativo"
]

# --- FLAGS & LEGENDS ---
LEGEND_ATHLETE = {
    "1": "Abaixo (1)",
    "2": "Na Média (2)",
    "3": "Se Destacou (3)",
    "F": "Faltou",
    "DM": "Lesão"
}
VALID_ATHLETE_FLAGS = list(LEGEND_ATHLETE.keys())

LEGEND_TRAINING = {
    "1": "Treino Ruim (1)",
    "2": "Na Média (2)",
    "3": "Treino Bom (3)",
    "FO": "Folga",
    "AM": "Amistoso",
    "CH": "Choveu"
}
VALID_TRAINING_FLAGS = list(LEGEND_TRAINING.keys())

# --- UI THEME COLORS (DARK MODE) ---
class Colors:
    # Cores Principais
    PRIMARY = "#00E676"      # Verde Neon (Destaque no preto)
    SECONDARY = "#00B0FF"    # Azul Neon
    ACCENT = "#FFD600"       # Amarelo Ouro
    
    # Backgrounds (Preto Total)
    BG_LIGHT = "#000000"     # Background Geral
    BG_CARD = "#121212"      # Cards/Sidebar (Cinza muito escuro)
    
    # Estados (Cores Vibrantes para Dark Mode)
    SUCCESS = "#00E676"      # Verde Brilhante
    WARNING = "#FFEA00"      # Amarelo Brilhante
    DANGER = "#FF1744"       # Vermelho Brilhante
    INFO = "#2979FF"         # Azul Brilhante

    # Texto
    TEXT_MAIN = "#FFFFFF"    # Branco Puro
    TEXT_LIGHT = "#B0BEC5"   # Cinza Claro
