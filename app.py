import streamlit as st
import sqlite3
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('judo_app.db')
c = conn.cursor()

# Dropar tabela se existir
c.execute('''DROP TABLE IF EXISTS observations''')

# Criar tabela para armazenar observações e informações do vídeo
c.execute('''
    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        action TEXT,
        athlete_name TEXT,
        age_category TEXT,
        sex TEXT,
        competition_name TEXT,
        competition_date DATE,
        athlete_club TEXT,
        opponent_name TEXT,
        opponent_club TEXT,
        opponent_type TEXT,
        weight_category TEXT,
        video_timestamp INTEGER DEFAULT 0,
        effectiveness TEXT,
        shido_nature TEXT,
        effect_score TEXT
    )
''')
conn.commit()

# Função para adicionar observação e informações do vídeo ao banco de dados
def add_observation(action, athlete_name, age_category, sex, competition_name, competition_date, athlete_club, opponent_name, opponent_club, opponent_type, weight_category, video_timestamp, effectiveness=None, shido_nature=None, effect_score=None):
    c.execute("INSERT INTO observations (action, athlete_name, age_category, sex, competition_name, competition_date, athlete_club, opponent_name, opponent_club, opponent_type, weight_category, video_timestamp, effectiveness, shido_nature, effect_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (action, athlete_name, age_category, sex, competition_name, competition_date, athlete_club, opponent_name, opponent_club, opponent_type, weight_category, video_timestamp, effectiveness, shido_nature, effect_score))
    conn.commit()

# Aplicativo Streamlit
st.title("Judo Observation App")

# Informações do vídeo
st.header("Informações do Vídeo")
athlete_name = st.text_input("Nome do Atleta")
athlete_club = st.text_input("Clube ou Pais do Atleta")
sex = st.selectbox("Sexo do Atleta", ["M", "F"], index=0)
age_category_options = ["Sênior", "Sub-18", "Sub-21"]
age_category = st.selectbox("Categoria de Idade", age_category_options, index=0)

# Selecionar categoria de peso com base no sexo e na categoria de idade
weight_categories = {
    "M": {
        "Sênior": ["-60", "-66", "-73", "-81", "-90", "-100", "+100"],
        "Sub-18": ["-50", "-55", "-60", "-66", "-73", "-81", "-90", "+90"],
        "Sub-21": ["-60", "-66", "-73", "-81", "-90", "-100", "+100"]
    },
    "F": {
        "Sênior": ["-48", "-52", "-57", "-63", "-70", "-78", "+78"],
        "Sub-18": ["-40", "-44", "-48", "-52", "-57", "-63", "-70", "+70"],
        "Sub-21": ["-48", "-52", "-57", "-63", "-70", "-78", "+78"]
    }
}

weight_category = st.selectbox("Categoria de Peso", weight_categories[sex][age_category] )
competition_name = st.text_input("Nome da Competição" )
competition_date = st.date_input("Data da Competição", datetime.date.today(), format="DD/MM/YYYY", key="competition_date")
opponent_name = st.text_input("Nome do Atleta Adversário")
opponent_club = st.text_input("Clube ou País do Oponente")
opponent_type = st.selectbox("Lado Dominante do Oponente", ('Destro', 'Canhoto'))
if not (athlete_name and age_category and age_category_options and weight_categories and sex and competition_name and competition_date and athlete_club and opponent_club and opponent_name and weight_category):
    st.error("Por favor, preencha todos os campos")
    st.stop()
# Carregar o vídeo
video_file = st.file_uploader("Faça o upload do vídeo", type=["mp4", "mov"])

if video_file is not None:
    # Exibe o vídeo
    st.video(video_file)

    # Aplicativo Streamlit para registro de ações
    st.title("Registro de Ações")
    video_time_input = st.text_input("Informe o tempo do vídeo (minuto e segundo):", "0:00")

    try:
        minutes, seconds = map(int, video_time_input.split(':'))
        current_video_time = minutes * 60 + seconds
    except ValueError:
        st.error("Formato de tempo inválido. Use o formato minuto:segundo, por exemplo, 0:42.")
        st.stop()

    # Selecionar tipo de ação
    action_type = st.selectbox("Selecione o tipo de ação:", ["Pegadas", "Golpes", "Shidos","Ne-Waza"])

    # Dicionário de ações por tipo
    actions = {
        "Pegadas": ["Tradicional Esquerda", "Tradicional Direita", "Cruzada Gola Esquerda", 
                    "Cruzada Gola Direita", "Cruzada Por Cima Esquerda", "Cruzada Por Cima Direita",
                    "Abraço", "Cruzada Manga e Costas Esquerda", "Cruzada Manga e Costas Direita","Manga e Manga", "Gola e Gola"],
        "Golpes": ["Ashi-Waza", "Te-Waza", "Koshi-Waza", "Transição"],
        "Shidos": ["Falta de Combatividade", "Passar a Cabeça", "Pegada Cruzada", "Chute", "Falso Ataque", "Pegar na Perna", "Cabeça Baixa", "Mão na Faixa"],
        "Ne-Waza": ["Sankaku","Shime", "Ura-Gatame", "Juji-Gatame"]
    }

    # Selecionar ação específica com base no tipo escolhido
    selected_action = st.selectbox(f"Selecione a {action_type.lower()}:", actions[action_type])

    # Se o tipo de ação for "Pegadas" ou "Golpes", exibir o pop-up de efetividade automaticamente
    if action_type in ["Pegadas", "Golpes", "Ne-Waza"]:
        # Popup para selecionar a efetividade
        with st.form("efetividade_form"):
            efetividade = st.radio("Foi efetivo?", ["Sim", "Não"])
            if efetividade == "Sim" and action_type in ["Golpes", "Ne-Waza"]:
                effect_score = st.radio("Ponto efetivado?", ["Wazari", "Ippon"])
            else:
                effect_score = None
            submit_button = st.form_submit_button("Registrar")
            
        # Lidar com a submissão do formulário
        if submit_button:
            add_observation(selected_action, athlete_name, age_category, sex, competition_name, competition_date, athlete_club, opponent_name, opponent_club,opponent_type, weight_category, current_video_time, effectiveness=efetividade, effect_score=effect_score)
            st.success(f"Observação adicionada: {selected_action} - Atleta: {athlete_name}")
    elif action_type == "Shidos":
        # Popup para selecionar a natureza do Shido
        with st.form("shido_form"):
            shido_nature = st.radio("O Shido foi a favor ou contra?", ["A favor", "Contra","Para ambos"])
            submit_button = st.form_submit_button("Registrar")

        # Lidar com a submissão do formulário
        if submit_button:
            add_observation(selected_action, athlete_name, age_category, sex, competition_name, competition_date, athlete_club, opponent_name, opponent_club, opponent_type ,weight_category, current_video_time, shido_nature=shido_nature)
            st.success(f"Observação adicionada: {selected_action} - Atleta: {athlete_name}")
    else:
        # Se o tipo de ação for diferente de "Pegadas", "Golpes" ou "Shidos", registrar a ação diretamente
        if st.button("Registrar Ação"):
            add_observation(selected_action, athlete_name, age_category, sex, competition_name, competition_date, athlete_club, opponent_name, opponent_club,opponent_type, weight_category, current_video_time)
            st.success(f"Ação registrada: {selected_action} - Atleta: {athlete_name}")

# Botão para finalizar a análise e recarregar a página
if st.button("Finalizar Análise"):
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

# Fechar a conexão com o banco de dados
conn.close()