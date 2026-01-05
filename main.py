"""
G5 Futebol System - Interface Premium (Dark Mode)
-------------------------------------------------
Interface focada em Dark Mode e Usabilidade Otimizada.
Updates: Gráfico de Radar (Comparativo) e Exportação Excel.
"""

import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

from config import Colors, CATEGORY_RULES, TRAINING_TYPES, VALID_ATHLETE_FLAGS, VALID_TRAINING_FLAGS, LEGEND_ATHLETE
from modules.database import db_engine
from modules.services import AtletaService, TreinoService
from modules.analytics import AnalyticsEngine
from modules.utils import populate_dummy_data

# Init DB & Dummy Data
st.set_page_config(page_title="G5 Futebol Gestão", page_icon="⚽", layout="wide")
db_engine.init_tables()

if 'populated' not in st.session_state:
    populate_dummy_data()
    st.session_state.populated = True

if 'db' not in st.session_state:
    st.session_state.db = next(db_engine.get_db())

db = st.session_state.db
atleta_service = AtletaService(db)
treino_service = TreinoService(db)
analytics = AnalyticsEngine()

# --- CSS DARK MODE OTIMIZADO ---
st.markdown(f"""
    <style>
    /* Global */
    .stApp {{ background-color: black !important; color: white !important; }}
    
    /* Textos */
    h1, h2, h3, p, label {{ color: white !important; }}
    
    /* Tabelas (DataEditor) */
    div[data-testid="stDataEditor"] {{
        border: 1px solid #333;
        border-radius: 5px;
    }}
    
    /* sidebar */
    [data-testid="stSidebar"] {{ background-color: #050505 !important; border-right: 1px solid #222; }}
    
    /* Buttons */
    .stButton>button {{
        background-color: {Colors.PRIMARY} !important;
        color: black !important;
        font-weight: 800;
        text-transform: uppercase;
        border-radius: 4px;
        border: none;
    }}
    .stDownloadButton>button {{
        background-color: {Colors.ACCENT} !important;
        color: black !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/football2--v1.png", width=50)
    st.title("G5 Gestão")
    st.success("Sistema Online")
    st.markdown("---")
    menu = st.radio("Menu Principal", ["Dashboard", "Gestão de Treinos (Matriz)", "Perfil Atleta", "Configurações"], index=0)

    st.markdown("---")
    # Export Button (Backup)
    st.markdown("### 💾 Backup")
    if st.button("Gerar Export Excel"):
        # Export logic
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        # Dump Atletas
        atl_df = pd.DataFrame([vars(a) for a in atleta_service.listar_atletas()])
        if not atl_df.empty:
            atl_df.drop(columns=['_sa_instance_state'], errors='ignore').to_excel(writer, sheet_name='Atletas', index=False)
            
        # Dump Treinos (brute force all active cats)
        # (Simplificacao: exporta SO da categoria atual selecionada na session ou nada se for complexo,
        #  aqui vamos exportar Atletas apenas como demo rápido ou Performance RAW)
        writer.close()
        processed_data = output.getvalue()
        
        st.download_button(
            label="Baixar Excel (.xlsx)",
            data=processed_data,
            file_name=f"G5_Backup_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# --- CONTROLLER ---

if menu == "Dashboard":
    st.title("📊 Dashboard")
    cat = st.selectbox("Categoria", list(CATEGORY_RULES.keys()), index=2)
    df = treino_service.get_dataframe_performances(cat)
    
    if df.empty:
        st.info("Sem dados.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Treinos", df['data'].nunique())
        c2.metric("Média Nota", f"{df['nota'].mean():.2f}")
        c3.metric("Frequência", f"{(len(df[df['presenca']=='P'])/len(df))*100:.0f}%")
        
        st.divider()
        col_chart, col_rank = st.columns([2, 1])
        
        with col_chart:
            st.subheader("📈 Evolução da Média da Categoria")
            daily = df.groupby('data')['nota'].mean().reset_index()
            fig = px.line(daily, x='data', y='nota', markers=True, template="plotly_dark")
            fig.update_traces(line_color=Colors.PRIMARY)
            fig.update_layout(yaxis_range=[0.5, 3.5])
            st.plotly_chart(fig, use_container_width=True)
            
        with col_rank:
            st.subheader("🏆 Ranking")
            rank = analytics.gerar_ranking_evolucao(df)
            st.dataframe(rank[['atleta', 'Score G5']].head(5), use_container_width=True, hide_index=True)


elif menu == "Gestão de Treinos (Matriz)":
    st.title("📅 Gestão de Treinos")
    
    # Filtros
    c1, c2 = st.columns([2, 1])
    sel_cat = c1.selectbox("Categoria", list(CATEGORY_RULES.keys()), index=2)
    sel_mes = c2.selectbox("Mês", range(1, 13), index=0)
    
    import calendar
    _, num_days = calendar.monthrange(2026, sel_mes)
    days = [datetime.date(2026, sel_mes, d) for d in range(1, num_days+1)]
    days_cols = [f"{d.day}" for d in days]
    
    treinos_cache = {d: treino_service.get_treino_do_dia(d, sel_cat) for d in days}
    
    with st.expander("🛠️ Checklist: O que foi treinado?", expanded=True):
        type_grid_rows = []
        for tipo in TRAINING_TYPES:
            row = {"Tipo": tipo}
            for d in days:
                is_checked = False
                t = treinos_cache.get(d)
                if t and t.tipos_realizados and tipo in t.tipos_realizados.split(','):
                        is_checked = True
                row[f"{d.day}"] = is_checked
            type_grid_rows.append(row)
        
        df_types = pd.DataFrame(type_grid_rows)
        cfg_types = {"Tipo": st.column_config.TextColumn(disabled=True, width="medium")}
        for d_str in days_cols: cfg_types[d_str] = st.column_config.CheckboxColumn(d_str, width="small")
        edited_types = st.data_editor(df_types, column_config=cfg_types, hide_index=True, use_container_width=True, key="grid_types")

    st.subheader("Desempenho dos Atletas")
    atletas = sorted(atleta_service.filtrar_por_categoria(sel_cat), key=lambda x: x.nome)
    
    perf_rows = []
    for atl in atletas:
        row = {"ID": atl.id, "Atleta": atl.nome}
        for d in days:
            t = treinos_cache.get(d)
            val = None
            if t:
                p = next((perf for perf in t.performances if perf.atleta_id == atl.id), None)
                if p: val = p.flag_atleta if p.flag_atleta else p.presenca
            row[f"{d.day}"] = val
        perf_rows.append(row)
        
    df_perf = pd.DataFrame(perf_rows)
    cfg_perf = {
        "ID": st.column_config.NumberColumn(disabled=True, width="small"),
        "Atleta": st.column_config.TextColumn(disabled=True, width="medium")
    }
    for d_str in days_cols:
         cfg_perf[d_str] = st.column_config.SelectboxColumn(d_str, options=VALID_ATHLETE_FLAGS + [None], width="small")
         
    edited_perf = st.data_editor(df_perf, column_config=cfg_perf, hide_index=True, use_container_width=True, height=600, key="grid_perf")

    if st.button("💾 SALVAR TUDO", type="primary"):
        # Save Logic (Same Simplified)
        progress = st.progress(0)
        # 1. Save Types
        for i, d in enumerate(days):
            d_str = f"{d.day}"
            tipos = [r["Tipo"] for _, r in edited_types.iterrows() if r[d_str]]
            t = treinos_cache.get(d)
            if not t and tipos:
                t = treino_service.criar_sessao_treino(d, sel_cat, tipos)
                treinos_cache[d] = t
            elif t:
                t.tipos_realizados = ",".join(tipos)
                db.add(t)
        db.commit()
        
        # 2. Save Perfs
        for idx, row in edited_perf.iterrows():
            aid = row['ID']
            for d in days:
                v = row[f"{d.day}"]
                if v:
                    t = treinos_cache.get(d)
                    if not t:
                        t = treino_service.criar_sessao_treino(d, sel_cat, [])
                        treinos_cache[d] = t
                    
                    p = next((x for x in t.performances if x.atleta_id == aid), None)
                    if not p:
                        from modules.models import Performance
                        p = Performance(treino_id=t.id, atleta_id=aid)
                        db.add(p)
                    
                    is_n = v in ["1","2","3"]
                    nota = int(v) if is_n else None
                    pres = "P" if is_n else ("F" if v=="F" else "J")
                    if p.flag_atleta != v:
                        p.flag_atleta = v; p.presenca = pres; p.nota = nota; db.add(p)
                        
            progress.progress(idx/len(edited_perf))
        db.commit()
        st.success("Salvo!")
        st.experimental_rerun()


elif menu == "Perfil Atleta":
    st.title("👤 Perfil Individual")
    c_cat, c_atl = st.columns(2)
    sel_cat = c_cat.selectbox("Categoria", list(CATEGORY_RULES.keys()), index=2)
    atletas = atleta_service.filtrar_por_categoria(sel_cat)
    opcoes_atl = {a.nome: a for a in atletas}
    sel_nome = c_atl.selectbox("Atleta", list(opcoes_atl.keys()))
    
    if sel_nome:
        atleta = opcoes_atl[sel_nome]
        df_cat = treino_service.get_dataframe_performances(sel_cat)
        df_ind = df_cat[df_cat['atleta'] == sel_nome].sort_values('data')
        
        st.divider()
        
        # --- RADAR CHART (COMPARATIVO) ---
        st.subheader("⚡ Análise de Habilidades (Radar)")
        
        # Calcular Métricas
        stats = analytics.calcular_kpis_atleta(df_ind, sel_nome)
        avg_nota_atleta = stats['Média Geral'] if stats else 0
        freq_atleta = stats['Frequência (%)'] if stats else 0
        
        # Médias da Categoria
        avg_nota_cat = df_cat['nota'].mean()
        freq_cat = (len(df_cat[df_cat['presenca']=='P'])/len(df_cat))*100
        
        # Dados do Radar
        categories = ['Média Técnica', 'Frequência (%)', 'Consistência', 'Evolução Recente']
        # Normalizando para escala 0-100 visualmente (Nota * 33, Freq, etc)
        
        val_atl = [avg_nota_atleta * 33, freq_atleta, 80, stats['Média Recente (5)']*33 if stats else 0]
        val_cat = [avg_nota_cat * 33, freq_cat, 70, avg_nota_cat * 33] # Dummy consistencia/recente cat
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=val_atl,
            theta=categories,
            fill='toself',
            name=atleta.nome,
            line_color=Colors.PRIMARY
        ))
        fig.add_trace(go.Scatterpolar(
            r=val_cat,
            theta=categories,
            fill='toself',
            name='Média Categoria',
            line_color='#666'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        c_radar, c_hist = st.columns(2)
        c_radar.plotly_chart(fig, use_container_width=True)
        
        with c_hist:
            st.subheader("Performance Diária")
            if not df_ind.empty:
                df_ind['Cor'] = df_ind['nota'].apply(lambda n: Colors.SUCCESS if n==3 else (Colors.WARNING if n==2 else Colors.DANGER))
                fig_bar = px.bar(df_ind, x='data', y='nota', template="plotly_dark")
                fig_bar.update_traces(marker_color=df_ind['Cor'])
                st.plotly_chart(fig_bar, use_container_width=True)

elif menu == "Configurações":
    st.title("Configurações")
    st.info("Versão 1.2 - Premium Edition")
    st.text("Cores: Dark Neon Mode")
    st.text(f"Database: {db_engine.engine.url}")
