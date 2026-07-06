import streamlit as st
import pandas as pd
from PIL import Image 
from services.loader import carregar_dados_consolidados
from components.sidebar import renderizar_sidebar

# Ajuste o nome da pasta se for 'charts' em vez de 'chats'
from charts.executivo import renderizar_painel_executivo
from charts.demografia import renderizar_analise_demografica
from charts.organizacional import renderizar_estrutura_organizacional
from components.tabelas import renderizar_exploracao_dados

logo_empresa = Image.open("assets/logo.png")

# Configuração da página do Streamlit
st.set_page_config(page_title="Dash People Analytics", page_icon=logo_empresa, layout="wide")

# Função para carregar o CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.sidebar.image(logo_empresa, width=150)
# 2. Carregar e consolidar os dados das 3 empresas

st.sidebar.markdown("### 📥 Atualizar Base de Dados")
arquivo_importado = st.sidebar.file_uploader(
    "Importar planilha de funcionários atualizada",
    type=["xlsx", "xls", "csv"],
    help="Arraste o novo relatório do sistema de RH aqui para atualizar os gráficos."
)

# 2. Carregar os dados (Se houver arquivo importado, lê ele; senão, carrega a base padrão)
if arquivo_importado is not None:
    try:
        # Verifica a extensão para ler corretamente
        if arquivo_importado.name.endswith('.csv'):
            df_total = pd.read_csv(arquivo_importado)
        else:
            df_total = pd.read_excel(arquivo_importado)
            
        st.sidebar.success("✅ Nova base importada com sucesso!")
    except Exception as e:
        st.sidebar.error(f"Erro ao ler o arquivo: {e}")
        df_total = carregar_dados_consolidados() # Fallback em caso de erro
else:
    # Se o RH não subiu nada, carrega o banco de dados padrão do projeto
    df_total = carregar_dados_consolidados()


df_filtrado = renderizar_sidebar(df_total)

df_total = carregar_dados_consolidados()

# 3. Aplicar componentes de filtro na barra lateral (Empresa, Status, etc.)


# 4. Menu de Navegação Principal
aba_selecionada = st.sidebar.radio(
    "Menu Principal",
    ["Dashboard Executivo", "Perfil dos Colaboradores", "Explorar Dados"]
)

# 5. Direcionamento e renderização das telas com base nos dados filtrados
if aba_selecionada == "Dashboard Executivo":
    st.title("Dashboard Executivo")
    st.subheader("Visão Estratégica e KPIs Consolidados")
    
    # Passa o dataframe filtrado para gerar os KPIs macros (Headcount, Turnover, Ativos)
    renderizar_painel_executivo(df_filtrado)

elif aba_selecionada == "Perfil dos Colaboradores":
    st.title("Perfil dos Colaboradores")
    
    # Criando sub-abas para organizar a densidade de informações
    sub_aba = st.tabs(["Demografia & Ciclo", "Estrutura Organizacional"])
    
    with sub_aba[0]:
        st.subheader("Análise Demográfica e Ciclo de Vida")
        # Foco em: Faixa etária, Tempo de empresa, Escolaridade, Cidade/Nacionalidade
        renderizar_analise_demografica(df_filtrado)
        
    with sub_aba[1]:
        st.subheader("Desenho e Estrutura Organizacional")
        # Foco em: Setor, Cargo, Gestores, Status (Férias, Afastados)
        renderizar_estrutura_organizacional(df_filtrado)

elif aba_selecionada == "Explorar Dados":
    st.title("Explorar Dados")
    st.subheader("Tabela Dinâmica de Colaboradores")
    
    # Foco em: Exibir st.dataframe com filtros adicionais e st.download_button
    renderizar_exploracao_dados(df_filtrado)