import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = "https://zyusyevqbrdepnamqpon.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dXN5ZXZxYnJkZXBuYW1xcG9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MDk3MDgsImV4cCI6MjA1MzM4NTcwOH0.SjMQtU5g2cVR_BJAI4AWld-iHsJMxQLwf3Zrn6PrXNk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para deletar dados
def delete_data(table, id_column, record_id):
    response = supabase.table(table).delete().match({id_column: record_id}).execute()
    if response.data:
        st.success(f'Registro {record_id} deletado com sucesso da tabela {table}!')
    else:
        st.error(f'Erro ao deletar o registro {record_id} da tabela {table}!')

# Função para buscar dados de uma tabela
def get_data_from_table(table_name):
    response = supabase.table(table_name).select('*').execute()
    return response.data if response.data else []

# Interface do Streamlit
st.title('Deletar Dados no Supabase')

# Seleção da tabela para deletar dados
tabela = st.selectbox('Selecione a tabela para deletar:', ['rural', 'local', 'partes_local', 'medicoes'])

# Buscar dados da tabela selecionada
dados = get_data_from_table(tabela)

# Exibir dados para seleção
if dados:
    st.write(f'Dados da tabela {tabela}:')
    for record in dados:
        st.write(record)
    
    # Seleção do ID do registro a ser deletado
    if tabela == 'rural':
        id_column = 'id_rural'
    elif tabela == 'local':
        id_column = 'id_local'
    elif tabela == 'partes_local':
        id_column = 'id_partes_local'
    elif tabela == 'medicoes':
        id_column = 'id_medicao'
    
    record_id = st.selectbox(f'Selecione o ID do registro a ser deletado:', [record[id_column] for record in dados])

    # Botão para deletar
    if st.button('Deletar'):
        delete_data(tabela, id_column, record_id)
else:
    st.write(f'Nenhum dado encontrado na tabela {tabela}.')
