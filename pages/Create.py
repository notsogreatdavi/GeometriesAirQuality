import streamlit as st
import json
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = "https://zyusyevqbrdepnamqpon.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dXN5ZXZxYnJkZXBuYW1xcG9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MDk3MDgsImV4cCI6MjA1MzM4NTcwOH0.SjMQtU5g2cVR_BJAI4AWld-iHsJMxQLwf3Zrn6PrXNk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para inserir dados manualmente
def insert_manual_data(table, data):
    response = supabase.table(table).insert(data).execute()
    if response.data:
        st.success(f'Dados inseridos com sucesso na tabela {table}!')
    else:
        st.error('Erro ao inserir dados!')

# Função para inserir dados a partir de um arquivo JSON
def insert_json_data(json_data):
    for table, records in json_data.items():
        response = supabase.table(table).insert(records).execute()
        if not response.data:
            st.error(f'Erro ao inserir dados na tabela {table}!')
            return
    st.success('Dados do JSON inseridos com sucesso!')

# Função para buscar IDs de tabelas relacionadas
def get_ids_from_table(table_name, id_column):
    response = supabase.table(table_name).select(id_column).execute()
    return [record[id_column] for record in response.data] if response.data else []

# Interface do Streamlit
st.title('Inserção de Dados no Supabase')

# Seleção do modo de inserção
modo_insercao = st.radio('Selecione o modo de inserção:', ('Manual', 'JSON'))

if modo_insercao == 'Manual':
    st.header('Inserção Manual de Dados')
    tabela = st.selectbox('Selecione a tabela:', ['rural', 'local', 'partes_local', 'medicoes'])

    if tabela == 'rural':
        # Buscar IDs válidos de 'id_rural' a partir da tabela 'area_rural'
        rural_ids = get_ids_from_table('rural', 'id_rural')
        
        # Encontrar o maior ID de 'id_rural' e adicionar 1
        if rural_ids:
            next_id_rural = max(rural_ids) + 1
        else:
            next_id_rural = 1  # Caso não haja IDs, começamos de 1
            
        st.write(f'O próximo ID da Rural é: {next_id_rural}')
        id_rural = next_id_rural
        
        area = int(st.number_input('Área (em hectares):', min_value=0, step=1))
        if st.button('Inserir'):
            data = {'id_rural':id_rural,'area': area}
            insert_manual_data(tabela, data)

    elif tabela == 'local':
        # Buscar IDs válidos de 'id_area_rural' a partir da tabela 'area_rural'
        area_rural_ids = get_ids_from_table('rural', 'id_rural')
        local_ids = get_ids_from_table('local', 'id_local')
        
        # Encontrar o maior ID de 'id_local' e adicionar 1
        if local_ids:
            next_id_local = max(local_ids) + 1
        else:
            next_id_local = 1  # Caso não haja IDs, começamos de 1
            
        st.write(f'O próximo ID da Rural é: {next_id_local}')
        id_local = next_id_local
        
        local = st.text_input('Nome do Local:')
        descricao = st.text_area('Descrição:')
        
        # Permitir selecionar ou adicionar um novo ID da Área Rural
        id_area_rural_option = st.selectbox('Escolha um ID de Área Rural ou insira um novo:', ['Selecione um ID existente'] + area_rural_ids)
        
        if id_area_rural_option == 'Selecione um ID existente':
            id_area_rural = st.selectbox('ID da Área Rural:', area_rural_ids)
        else:
            id_area_rural = int(st.number_input('Novo ID da Área Rural:', min_value=1, step=1))

        if st.button('Inserir'):
            data = {'id_local':id_local, 'local': local, 'descricao': descricao, 'id_area_rural': id_area_rural}
            insert_manual_data(tabela, data)

    elif tabela == 'partes_local':
        # Buscar IDs válidos de 'id_partes_local' a partir da tabela 'partes_local'
        partes_local_ids = get_ids_from_table('partes_local', 'id_partes_local')
        local_ids = get_ids_from_table('local', 'id_local')

        # Encontrar o maior ID de 'id_partes_local' e adicionar 1
        if partes_local_ids:
            next_id_partes_local = max(partes_local_ids) + 1
        else:
            next_id_partes_local = 1  # Caso não haja IDs, começamos de 1

        st.write(f'O próximo ID para Parte do Local é: {next_id_partes_local}')
        id_partes_local = next_id_partes_local

        lugar = st.text_input('Lugar:')
        descricao = st.text_area('Descrição:')

        # Permitir selecionar ou adicionar um novo ID de Parte do Local
        id_local_option = st.selectbox('Escolha um ID do Local ou insira um novo:', ['Selecione um ID existente'] + ['Novo ID'])

        if id_local_option == 'Selecione um ID existente':
            id_local = st.selectbox('ID do Local:', local_ids)
        else:
            id_local = int(st.number_input('Novo ID do Local:', min_value=1, step=1))

        if st.button('Inserir'):
            data = {'id_partes_local':id_partes_local, 'lugar': lugar, 'descricao': descricao, 'id_local': id_local}
            insert_manual_data(tabela, data)

    elif tabela == 'medicoes':
        # Buscar IDs válidos de 'id_medicao' a partir da tabela 'medicoes' e 'id_partes_local' a partir da tabela 'partes_local'
        medicao_ids = get_ids_from_table('medicoes', 'id_medicao')
        partes_local_ids = get_ids_from_table('partes_local', 'id_partes_local')

        # Encontrar o maior ID de medição e adicionar 1
        if medicao_ids:
            next_id_medicao = max(medicao_ids) + 1
        else:
            next_id_medicao = 1  # Caso não haja IDs, começamos de 1

        st.write(f'O próximo ID para Medição é: {next_id_medicao}')
        id_medicao = next_id_medicao

        ppm = st.number_input('PPM:')
        mg_m3 = st.number_input('mg/m³:')
        mg_m2 = st.number_input('mg/m²:')
        umidade = st.number_input('Umidade:')
        temperatura = st.number_input('Temperatura:')
        hora = st.text_input('Hora (HH:MM:SS):')
        data = st.text_input('Data (YYYY-MM-DD):')
        descricao = st.text_area('Descrição:')
        
        # Permitir selecionar ou adicionar um novo ID das Partes Local
        id_partes_local_option = st.selectbox('Escolha um ID de Parte do Local ou insira um novo:', ['Selecione um ID existente'] + ['Novo ID'])
        
        if id_partes_local_option == 'Selecione um ID existente':
            id_partes_local = st.selectbox('ID da Parte do Local:', partes_local_ids)
        else:
            id_partes_local = int(st.number_input('Novo ID da Parte do Local:', min_value=1, step=1))

        if st.button('Inserir'):
            data = {
                'id_medicao':id_medicao, 'ppm': ppm, 'mg_m3': mg_m3, 'mg_m2': mg_m2,
                'umidade': umidade, 'temperatura': temperatura,
                'hora': hora, 'data': data, 'descricao': descricao,
                'id_partes_local': id_partes_local
            }
            insert_manual_data(tabela, data)
else:
    st.header('Inserção de Dados via JSON')
    uploaded_file = st.file_uploader('Carregue um arquivo JSON', type=['json'])
    if uploaded_file is not None:
        json_data = json.load(uploaded_file)
        if st.button('Inserir Dados do JSON'):
            insert_json_data(json_data)
