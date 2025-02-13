import streamlit as st
from supabase import create_client, Client
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = "https://zyusyevqbrdepnamqpon.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dXN5ZXZxYnJkZXBuYW1xcG9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MDk3MDgsImV4cCI6MjA1MzM4NTcwOH0.SjMQtU5g2cVR_BJAI4AWld-iHsJMxQLwf3Zrn6PrXNk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Monitoramento Ar", page_icon="📈")
st.title("Análise de Dados de Qualidade do Ar")

# Buscar dados do Supabase
@st.cache_data(ttl=600)  # Cache por 10 minutos
def load_data():
    response = supabase.table("medicoes").select("*").execute()
    return pd.DataFrame(response.data)

df = load_data()

# Converter campos de data/hora
if not df.empty:
    df['datetime'] = pd.to_datetime(df['data'].astype(str) + ' ' + df['hora'].astype(str))
    df = df.sort_values('datetime')

# Sidebar - Seleção de parâmetros
st.sidebar.header("Configurações")
parameter = st.sidebar.selectbox(
    "Selecione o parâmetro para plotar:",
    options=['ppm', 'mg_m3', 'mg_m2', 'umidade', 'temperatura']
)

# Converter campos de data/hora
if not df.empty:
    # Converter para datetime do Python
    df['datetime'] = pd.to_datetime(df['data'].astype(str) + ' ' + df['hora'].astype(str)).dt.to_pydatetime()
    df = df.sort_values('datetime')

# Sidebar - Seleção de parâmetros
st.sidebar.header("Configurações")

if not df.empty:
    # Usar objetos datetime nativos para o slider
    min_date = df['datetime'].min().to_pydatetime()
    max_date = df['datetime'].max().to_pydatetime()
    
    selected_range = st.sidebar.slider(
        "Selecione o intervalo temporal:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="DD/MM/YY HH:mm"  # Formato opcional para exibição
    )
    
else:
    st.sidebar.warning("Nenhum dado disponível para filtragem")
    parameter = None

# Criar o selectbox fora de qualquer loop ou função
parameter = st.sidebar.selectbox(
    "Selecione o parâmetro para plotar:",
    options=['ppm', 'mg_m3', 'mg_m2', 'umidade', 'temperatura'],
    key="unique_selectbox_key"
)

# Restante do código
if not df.empty:
    filtered_df = df[(df['datetime'] >= selected_range[0]) & 
                    (df['datetime'] <= selected_range[1])]
    
    st.subheader(f"Variação de {parameter} ao longo do tempo")
    st.line_chart(
        data=filtered_df,
        x='datetime',
        y=parameter,
        use_container_width=True
    )
    
    # Mostrar dados brutos
    st.subheader("Dados Brutos")
    st.dataframe(filtered_df[['datetime', parameter, 'descricao', 'id_partes_local']])
else:
    st.warning("Nenhum dado encontrado na base de dados!")

# Atualização manual dos dados
if st.sidebar.button("Atualizar Dados"):
    df = load_data()
    st.experimental_rerun()

# Estatísticas rápidas
if not df.empty:
    st.sidebar.subheader("Estatísticas")
    st.sidebar.metric(
        label=f"Máximo de {parameter}",
        value=f"{filtered_df[parameter].max():.2f}"
    )
    st.sidebar.metric(
        label=f"Média de {parameter}",
        value=f"{filtered_df[parameter].mean():.2f}"
    )