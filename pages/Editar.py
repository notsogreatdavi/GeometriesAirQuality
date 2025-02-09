import streamlit as st
from supabase import create_client, Client
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

# Função para buscar IDs de tabelas relacionadas
def get_ids_from_table(table_name, id_column):
    response = supabase.table(table_name).select(id_column).execute()
    return [record[id_column] for record in response.data] if response.data else []

# Interface do Streamlit
st.title('Edição de Dados no Supabase')

# Seleção da tabela para editar
tabela = st.selectbox('Selecione a tabela para editar:', ['rural', 'local', 'partes_local', 'medicoes'])

if tabela == 'rural':
    # Buscar IDs válidos de 'id_rural' a partir da tabela 'rural'
    rural_ids = get_ids_from_table('rural', 'id_rural')

    # Permitir selecionar um ID de 'rural'
    id_rural = st.selectbox('Escolha um ID de Rural para editar:', rural_ids)
    
    if id_rural:
        # Buscar os dados existentes para o ID selecionado
        response = supabase.table('rural').select('*').eq('id_rural', id_rural).execute()
        if response.data:
            rural_data = response.data[0]
            # Exibir dados existentes
            st.write(f"Dados existentes: {rural_data}")
            area = st.number_input('Área (em hectares):', min_value=0, step=1, value=rural_data['area'])
            
            if st.button('Atualizar'):
                updated_data = {'id_rural': id_rural, 'area': area}
                response_update = supabase.table('rural').update(updated_data).eq('id_rural', id_rural).execute()
                if response_update.data:
                    st.success(f'Dados da tabela {tabela} atualizados com sucesso!')
                else:
                    st.error(f'Erro ao atualizar dados na tabela {tabela}')
        else:
            st.error(f'Não foi encontrado nenhum dado para o ID {id_rural}')

elif tabela == 'local':
    # Buscar nomes de locais a partir da tabela 'local'
    locais = supabase.table('local').select('id_local', 'local').execute()
    
    # Criar uma lista de nomes de locais para exibir na selectbox
    nome_locais = [local['local'] for local in locais.data]
    
    nome_local = st.selectbox('Escolha um Local para editar:', nome_locais)
    
    if nome_local:
        # Encontrar o id_local correspondente ao nome selecionado
        local_selecionado = next(local for local in locais.data if local['local'] == nome_local)
        id_local = local_selecionado['id_local']
        
        # Buscar os dados existentes para o ID selecionado
        response = supabase.table('local').select('*').eq('id_local', id_local).execute()
        if response.data:
            local_data = response.data[0]
            # Exibir dados existentes
            st.write(f"Dados existentes: {local_data}")
            local = st.text_input('Nome do Local:', value=local_data['local'])
            descricao = st.text_area('Descrição:', value=local_data['descricao'])
            
            if st.button('Atualizar'):
                updated_data = {'id_local': id_local, 'local': local, 'descricao': descricao}
                response_update = supabase.table('local').update(updated_data).eq('id_local', id_local).execute()
                if response_update.data:
                    st.success(f'Dados da tabela {tabela} atualizados com sucesso!')
                else:
                    st.error(f'Erro ao atualizar dados na tabela {tabela}')
        else:
            st.error(f'Não foi encontrado nenhum dado para o ID {id_local}')

elif tabela == 'partes_local':
    # Buscar nomes de lugares a partir da tabela 'partes_local'
    partes_local = supabase.table('partes_local').select('id_partes_local', 'lugar').execute()
    
    # Criar uma lista de nomes de lugares para exibir na selectbox
    nome_lugares = [parte['lugar'] for parte in partes_local.data]
    
    lugar_selecionado = st.selectbox('Escolha um Lugar para editar:', nome_lugares)
    
    if lugar_selecionado:
        # Encontrar o id_partes_local correspondente ao nome selecionado
        parte_selecionada = next(parte for parte in partes_local.data if parte['lugar'] == lugar_selecionado)
        id_partes_local = parte_selecionada['id_partes_local']
        
        # Buscar os dados existentes para o ID selecionado
        response = supabase.table('partes_local').select('*').eq('id_partes_local', id_partes_local).execute()
        if response.data:
            partes_local_data = response.data[0]
            # Exibir dados existentes
            st.write(f"Dados existentes: {partes_local_data}")
            lugar = st.text_input('Lugar:', value=partes_local_data['lugar'])
            descricao = st.text_area('Descrição:', value=partes_local_data['descricao'])
            
            if st.button('Atualizar'):
                updated_data = {'id_partes_local': id_partes_local, 'lugar': lugar, 'descricao': descricao}
                response_update = supabase.table('partes_local').update(updated_data).eq('id_partes_local', id_partes_local).execute()
                if response_update.data:
                    st.success(f'Dados da tabela {tabela} atualizados com sucesso!')
                else:
                    st.error(f'Erro ao atualizar dados na tabela {tabela}')
        else:
            st.error(f'Não foi encontrado nenhum dado para o ID {id_partes_local}')

elif tabela == 'medicoes':
    # Buscar IDs válidos de 'id_medicao' a partir da tabela 'medicoes'
    medicoes_ids = get_ids_from_table('medicoes', 'id_medicao')
    
    id_medicao = st.selectbox('Escolha um ID de Medição para editar:', medicoes_ids)
    
    if id_medicao:
        # Buscar os dados existentes para o ID selecionado
        response = supabase.table('medicoes').select('*').eq('id_medicao', id_medicao).execute()
        if response.data:
            medicoes_data = response.data[0]
            # Exibir dados existentes
            st.write(f"Dados existentes: {medicoes_data}")
            ppm = st.number_input('PPM:', value=medicoes_data['ppm'])
            mg_m3 = st.number_input('mg/m³:', value=medicoes_data['mg_m3'])
            mg_m2 = st.number_input('mg/m²:', value=medicoes_data['mg_m2'])
            umidade = st.number_input('Umidade:', value=medicoes_data['umidade'])
            temperatura = st.number_input('Temperatura:', value=medicoes_data['temperatura'])
            hora = st.text_input('Hora (HH:MM:SS):', value=medicoes_data['hora'])
            data = st.text_input('Data (YYYY-MM-DD):', value=medicoes_data['data'])
            descricao = st.text_area('Descrição:', value=medicoes_data['descricao'])

            # Buscar a lista de partes locais
            partes_local = supabase.table('partes_local').select('id_partes_local', 'lugar').execute()
            
            # Criar uma lista de tuplas (id_partes_local, nome_partes_local) para exibir na selectbox
            id_nome_partes_local = [(parte['id_partes_local'], parte['lugar']) for parte in partes_local.data]
            
            # Escolher a parte local através do nome na selectbox
            parte_local_selecionada = st.selectbox('Escolha a Parte Local:', [parte[1] for parte in id_nome_partes_local])
            
            if parte_local_selecionada:
                # Encontrar o id_partes_local correspondente ao nome selecionado
                id_partes_local = next(parte[0] for parte in id_nome_partes_local if parte[1] == parte_local_selecionada)
                
                if st.button('Atualizar'):
                    updated_data = {
                        'id_medicao': id_medicao, 'ppm': ppm, 'mg_m3': mg_m3, 'mg_m2': mg_m2,
                        'umidade': umidade, 'temperatura': temperatura, 'hora': hora, 'data': data,
                        'descricao': descricao, 'id_partes_local': id_partes_local
                    }
                    response_update = supabase.table('medicoes').update(updated_data).eq('id_medicao', id_medicao).execute()
                    if response_update.data:
                        st.success(f'Dados da tabela {tabela} atualizados com sucesso!')
                    else:
                        st.error(f'Erro ao atualizar dados na tabela {tabela}')
        else:
            st.error(f'Não foi encontrado nenhum dado para o ID {id_medicao}')
