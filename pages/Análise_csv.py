import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Análise de CSVs", page_icon="📊")
st.title("Análise Comparativa de Dados Ambientais")

# Carregar dados
@st.cache_data
def load_data():
    apt = pd.read_csv("C:\codigos\projeto\GeometriesAirQuality\one_room_apartement.csv")
    lab = pd.read_csv("C:\codigos\projeto\GeometriesAirQuality\laboratory.csv")
    
    # Converter timestamp para datetime (ajustado para o formato correto)
    for df in [apt, lab]:
        df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
        df.sort_values('datetime', inplace=True)
    
    return apt, lab

apartment_df, laboratory_df = load_data()

# Sidebar controls
st.sidebar.header("Configurações de Visualização")

# Selecionar dataset
dataset = st.sidebar.selectbox(
    "Selecione o dataset:",
    ["Apartamento", "Laboratório"],
    key="dataset_selector"
)

# Selecionar parâmetro
current_df = apartment_df if dataset == "Apartamento" else laboratory_df
parameters = [col for col in current_df.columns if col not in ['timestamp', 'datetime', 'health']]

selected_param = st.sidebar.selectbox(
    "Parâmetro para análise:",
    options=parameters,
    key="param_selector"
)

# Selecionar intervalo temporal
if not current_df.empty:
    # Converter pandas.Timestamp para datetime.datetime
    min_date = current_df['datetime'].min().to_pydatetime()
    max_date = current_df['datetime'].max().to_pydatetime()
    
    date_range = st.sidebar.slider(
        "Intervalo Temporal:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="DD/MM/YYYY"
    )
else:
    st.sidebar.warning("Nenhum dado disponível para filtragem.")
    date_range = (None, None)

# Filtragem de dados
if date_range[0] and date_range[1]:
    filtered_df = current_df[
        (current_df['datetime'] >= date_range[0]) & 
        (current_df['datetime'] <= date_range[1])
    ]
else:
    filtered_df = pd.DataFrame()

# Gráfico principal
if not filtered_df.empty:
    st.subheader(f"Variação Temporal de {selected_param}")
    fig = px.line(
        filtered_df,
        x='datetime',
        y=selected_param,
        title=f"{selected_param} no {dataset}",
        labels={'value': 'Valor', 'datetime': 'Data/Hora'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado no intervalo selecionado.")

# Seção de anomalias
st.subheader("Anomalias Registradas")
anomalies = {
    '2023-07-09': "Erro de medição de material particulado devido a umidade elevada",
    '2023-04-17': "Queda de energia no laboratório",
    '2023-05-21': "Grande incêndio próximo ao local de medição"
}

show_anomalies = st.checkbox("Mostrar anomalias conhecidas")
if show_anomalies and not filtered_df.empty:
    for date_str, desc in anomalies.items():
        anomaly_date = datetime.strptime(date_str, '%Y-%m-%d')
        if date_range[0] <= anomaly_date <= date_range[1]:
            st.markdown(f"**{date_str}**: {desc}")
            fig.add_vline(x=anomaly_date, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)

# Estatísticas rápidas
if not filtered_df.empty:
    st.sidebar.subheader("Estatísticas do Período")
    try:
        st.sidebar.metric("Máximo", f"{filtered_df[selected_param].max():.2f}")
        st.sidebar.metric("Mínimo", f"{filtered_df[selected_param].min():.2f}")
        st.sidebar.metric("Média", f"{filtered_df[selected_param].mean():.2f}")
    except Exception as e:
        st.sidebar.error("Erro ao calcular estatísticas")

# Dados brutos
if not filtered_df.empty:
    expander = st.expander("Visualizar Dados Brutos")
    expander.dataframe(filtered_df[['datetime', selected_param, 'health']].sort_values('datetime'))

# Comparativo entre ambientes
st.subheader("Comparativo entre Ambientes")
compare_param = st.selectbox(
    "Selecione parâmetro para comparação:",
    parameters,
    key="compare_param"
)

col1, col2 = st.columns(2)
with col1:
    st.write("**Apartamento**")
    st.line_chart(apartment_df, x='datetime', y=compare_param)

with col2:
    st.write("**Laboratório**")
    st.line_chart(laboratory_df, x='datetime', y=compare_param)