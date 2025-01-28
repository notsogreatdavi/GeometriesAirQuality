import streamlit as st

st.set_page_config(
    page_title="Início",
    page_icon="📚",
    menu_items = {
        'About': '''Este sistema foi desenvolvido na primeira edição do *Summer Scientific Program* da *UFRPE/UFPE*
         e financiado pelo *CNPq/INCT-INES* busca monitorar a qualidade do ar em locais como salas de aula, ônibus e terminais e utilizar 
        autômatos celulares e geometrias para modelar a dinâmica espacial e temporal dos dados coletados.
        '''
    }
)

st.write("# Summer University BSI/UFRPE 📚")

st.sidebar.success("Selecione uma página.")

st.markdown(
    """
Monitoramento autônomo e modelagem da qualidade do ar em ambientes da UFRPE e UFPE utilizando sensores ambientais, estatística, autômatos celulares e geometrias.

### 📌 Objetivo
Este projeto, parte da *Summer Scientific Program* da *UFRPE/UFPE* e financiado pelo *CNPq/INCT-INES*, busca:
- Monitorar a qualidade do ar em locais como salas de aula, ônibus e terminais.
- Processar medições de CO2, HCHO, TVOC, temperatura e umidade para avaliar riscos à saúde pública.
- Utilizar autômatos celulares e geometrias para modelar a dinâmica espacial e temporal dos dados coletados.

### 🔬 Metodologia
1. **Coleta de Dados**:  
   - Sensores ambientais registrarão medições triplicadas em 10 horários distintos por local.
   - Entre 480 e 720 medições realizadas em até 72 localidades diferentes.
2. **Processamento Estatístico**:  
   - Cálculo de média, mediana, moda, variância e outros indicadores.
3. **Modelagem Matemática e Computacional**:  
   - Aplicação de autômatos celulares para modelar a distribuição dos dados no tempo e no espaço.
   - Análise fractal para inferir dimensões e padrões emergentes nos dados.

### 🛠️ Tecnologias Utilizadas
- **Sensores**: [Temtop Detector de Qualidade do Ar]
(https://www.amazon.com.br/Temtop-qualidade-detector-temperatura-escrit%C3%B3rio/dp/B0CGX22CR8/ref=sr_1_2?th=1)

### 👥 Participantes
- [Davi Vieira da Silva](http://lattes.cnpq.br/4965614576411977)
- [Leon Lourenço da Silva Santos](http://lattes.cnpq.br/2595559017029087)
- [Lívia Maria Reis Souza da Silva](http://lattes.cnpq.br/6839606379308318)
- [Lucas Gabriel Carvalho dos Ramos](https://lattes.cnpq.br/1733095457396125)
- [Rebeca Vitoria Tenorio da Costa](https://lattes.cnpq.br/8188503438162287)
- [Vithória Camila da Silva Bastos](https://lattes.cnpq.br/6527569192393672)
"""
)
