import streamlit as st
from services.loader import carregar_dados_consolidados
from components.sidebar import renderizar_sidebar

# 1. Importações dos seus módulos de visualização (baseado na estrutura da image_e7af3c.png)
# Ajuste o nome da pasta se for 'charts' em vez de 'chats'
from chats.executivo import renderizar_painel_executivo
from chats.demografia import renderizar_analise_demografica
from chats.diversidade import renderizar_analise_diversidade
from chats.organizacional import renderizar_estrutura_organizacional
from components.tabelas import renderizar_exploracao_dados

# Configuração da página do Streamlit
st.set_page_config(
    page_title="People Analytics Dashboard", 
    page_icon="👥", 
    layout="wide"
)

# 2. Carregar e consolidar os dados das 3 empresas
df_total = carregar_dados_consolidados()

# 3. Aplicar componentes de filtro na barra lateral (Empresa, Status, etc.)
df_filtrado = renderizar_sidebar(df_total)

# 4. Menu de Navegação Principal
aba_selecionada = st.sidebar.radio(
    "Menu Principal",
    ["📊 Dashboard Executivo", "👥 Perfil dos Colaboradores", "🔍 Explorar Dados"]
)

# 5. Direcionamento e renderização das telas com base nos dados filtrados
if aba_selecionada == "📊 Dashboard Executivo":
    st.title("📊 Dashboard Executivo")
    st.subheader("Visão Estratégica e KPIs Consolidados")
    
    # Passa o dataframe filtrado para gerar os KPIs macros (Headcount, Turnover, Ativos)
    renderizar_painel_executivo(df_filtrado)

elif aba_selecionada == "👥 Perfil dos Colaboradores":
    st.title("👥 Perfil dos Colaboradores")
    
    # Criando sub-abas para organizar a densidade de informações
    sub_aba = st.tabs(["📊 Demografia & Ciclo", "🌈 Diversidade & Inclusão", "🏢 Estrutura Organizacional"])
    
    with sub_aba[0]:
        st.subheader("Análise Demográfica e Ciclo de Vida")
        # Foco em: Faixa etária, Tempo de empresa, Escolaridade, Cidade/Nacionalidade
        renderizar_analise_demografica(df_filtrado)
        
    with sub_aba[1]:
        st.subheader("Indicadores de Diversidade e Inclusão (D&I)")
        # Foco em: Gênero, Raça/Etnia, Pessoas com deficiência (PCD)
        renderizar_analise_diversidade(df_filtrado)
        
    with sub_aba[2]:
        st.subheader("Desenho e Estrutura Organizacional")
        # Foco em: Setor, Cargo, Gestores, Status (Férias, Afastados)
        renderizar_estrutura_organizacional(df_filtrado)

elif aba_selecionada == "🔍 Explorar Dados":
    st.title("🔍 Explorar Dados")
    st.subheader("Tabela Dinâmica de Colaboradores")
    
    # Foco em: Exibir st.dataframe com filtros adicionais e st.download_button
    renderizar_exploracao_dados(df_filtrado)