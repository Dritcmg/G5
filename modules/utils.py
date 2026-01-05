"""
Módulo de Utilitários (Utils)
-----------------------------
Funções auxiliares para geração de dados falsos (Populate).
"""
import random
from datetime import date, timedelta
from modules.database import db_engine
from modules.services import AtletaService, TreinoService
from config import CATEGORY_RULES, VALID_ATHLETE_FLAGS, TRAINING_TYPES, VALID_TRAINING_FLAGS

def populate_dummy_data():
    """Gera dados massivos para testes visuais"""
    db = next(db_engine.get_db())
    atleta_service = AtletaService(db)
    treino_service = TreinoService(db)

    # 1. Limpar Banco (Opcional, mas bom para testes)
    # Por segurança, apenas adiciona se estiver vazio
    if len(atleta_service.listar_atletas()) > 0:
        return # Já populado

    print("Gerando dados fictícios...")

    # 2. Criar Atletas (Sub 14 - 2012 e Sub 15 - 2011)
    names_sub14 = [
        ("Gabriel Silva", "Goleiro"), ("Lucas Santos", "Zagueiro"), ("Matheus Oliveira", "Lateral"),
        ("Enzo Pereira", "Volante"), ("Pedro Rocha", "Meia"), ("João Souza", "Atacante"),
        ("Felipe Costa", "Meia"), ("Rafael Lima", "Zagueiro"), ("Bruno Alves", "Goleiro"),
        ("Gustavo Dias", "Atacante"), ("Thiago Mello", "Lateral"), ("Nicolas Ferreira", "Volante")
    ]
    
    for nome, pos in names_sub14:
        # Nascidos em 2012 (Sub 14)
        dta = date(2012, random.randint(1, 12), random.randint(1, 28))
        atleta_service.criar_atleta(nome, dta, pos, "(11) 9999-9999")

    # 3. Gerar Treinos para JANEIRO 2026 (Mês Completo)
    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 31)
    
    current = start_date
    while current <= end_date:
        if current.weekday() != 6: # Ignora Domingos
            
            # Sub 14
            # Randomiza tipos
            n_types = random.randint(1, 3)
            search_types = random.sample(TRAINING_TYPES, n_types)
            
            treino = treino_service.criar_sessao_treino(current, "Sub 14", search_types)
            
            # Avaliação Geral (Flag Treino)
            flag_t = random.choice(VALID_TRAINING_FLAGS)
            treino_service.salvar_avaliacao_geral(treino.id, flag_t, "Observação do dia gerada auto")
            
            # Performances Individuais
            for perf in treino.performances:
                # Randomiza Presença e Nota
                dice = random.random()
                if dice < 0.05: # 5% Faltou
                    treino_service.atualizar_performance(perf.id, None, "F", "F")
                elif dice < 0.08: # 3% DM
                    treino_service.atualizar_performance(perf.id, None, "DM", "dm")
                else: 
                    # Veio
                    # Nota 1, 2, 3 (Ponderada: mais 2 e 3)
                    nota = random.choices([1, 2, 3], weights=[10, 50, 40])[0]
                    flag_a = str(nota) # Usando a nota como flag visual principal
                    treino_service.atualizar_performance(perf.id, nota, flag_a, "P")
                    
        current += timedelta(days=1)

    print("Dados gerados com sucesso!")
