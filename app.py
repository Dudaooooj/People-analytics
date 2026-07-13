import os
import glob
import streamlit as st
import pandas as pd
from PIL import Image 
from services.loader import carregar_dados_consolidados
from components.sidebar import renderizar_sidebar

# Ajuste o nome da pasta se for 'charts' em vez de 'chats'
from charts.executivo import renderizar_painel_executivo
from charts.demografia import renderizar_analise_demografica
from charts.organizacional import renderizar_estrutura_organizacional
from charts.adicionais import renderizar_analise_atestados
from components.tabelas import renderizar_exploracao_dados

def carregar_atestados_consolidados(arquivos_carregados=None):
    """
    Consolida os dados de atestados. 
    Se 'arquivos_carregados' for fornecido, lê os arquivos do uploader.
    Caso contrário, lê os arquivos locais padrão em .ods.
    """
    dfs = []
    
    # SE O USUÁRIO SUBIU ARQUIVOS PELO BOTÃO
    if arquivos_carregados:
        for arquivo in arquivos_carregados:
            try:
                # Como o ODS deu certo antes, mantemos a engine odf se for o caso
                if arquivo.name.endswith(".ods"):
                    df_temp = pd.read_excel(arquivo, engine="odf", sheet_name=0)
                elif arquivo.name.endswith(".csv"):
                    df_temp = pd.read_csv(arquivo)
                else:
                    df_temp = pd.read_excel(arquivo, sheet_name=0)
                
                # Correção de cabeçalho deslocado
                if df_temp.shape[0] > 0 and ("CID" in df_temp.iloc[0].values or "Nome" in df_temp.iloc[0].values):
                    df_temp.columns = df_temp.iloc[0]
                    df_temp = df_temp[1:].reset_index(drop=True)
                
                df_temp = df_temp.dropna(how="all", axis=0).dropna(how="all", axis=1)
                df_temp.columns = [str(c).strip() for c in df_temp.columns]
                dfs.append(df_temp)
            except Exception as e:
                st.sidebar.error(f"Erro ao ler o arquivo importado {arquivo.name}: {e}")

    # SE NÃO HOUVER ARQUIVOS CARREGADOS, USA O FALLBACK LOCAL PADRÃO
    else:
        import os
        
        # Garante o mapeamento correto do caminho independente do sistema operacional (Windows/Linux)
        diretorio_base = os.path.dirname(__file__) if "__file__" in locals() else "."
        
        arquivos_locais = [
            os.path.join(diretorio_base, "dados", "GP4 _ Relatorio.ods"),
            os.path.join(diretorio_base, "dados", "Ledinternet_ Relatorio.ods"),
            os.path.join(diretorio_base, "dados", "Ledservicos _ Relatorio.ods")
        ]
        
        for arquivo in arquivos_locais:
            if os.path.exists(arquivo): # Só tenta ler se o arquivo fisicamente existir na nuvem
                try:
                    df_temp = pd.read_excel(arquivo, engine="odf", sheet_name=0)
                    if df_temp.shape[0] > 0 and ("CID" in df_temp.iloc[0].values or "Nome" in df_temp.iloc[0].values):
                        df_temp.columns = df_temp.iloc[0]
                        df_temp = df_temp[1:].reset_index(drop=True)
                    df_temp = df_temp.dropna(how="all", axis=0).dropna(how="all", axis=1)
                    df_temp.columns = [str(c).strip() for c in df_temp.columns]
                    dfs.append(df_temp)
                except Exception as e:
                    st.sidebar.error(f"Erro ao ler arquivo local na nuvem: {e}")
            
    if dfs:
        df_consolidado = pd.concat(dfs, ignore_index=True)
        return df_consolidado
        
    return pd.DataFrame()
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

st.sidebar.markdown("### 🩺 Atualizar Atestados (Mensal)")
arquivos_atestados_mensais = st.sidebar.file_uploader(
    "Importar relatórios de afastamento (.ods / .xlsx)",
    type=["ods", "xlsx", "xls"],
    accept_multiple_files=True, # Permite selecionar os 3 arquivos de uma vez só!
    help="Selecione ou arraste os novos relatórios de afastamento das empresas para atualizar a aba médica."
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
    sub_aba = st.tabs(["Demografia & Ciclo", "Estrutura Organizacional", "Informações Adicionais"])
    
    with sub_aba[0]:
        st.subheader("Análise Demográfica e Ciclo de Vida")
        # Foco em: Faixa etária, Tempo de empresa, Escolaridade, Cidade/Nacionalidade
        renderizar_analise_demografica(df_filtrado)
        
    with sub_aba[1]:
        st.subheader("Desenho e Estrutura Organizacional")
        # Foco em: Setor, Cargo, Gestores, Status (Férias, Afastados)
        renderizar_estrutura_organizacional(df_filtrado)

    with sub_aba[2]:
        st.subheader("Atestados e Afastamentos")
        
        df_atestados_total = carregar_atestados_consolidados(arquivos_atestados_mensais)
        
        if not df_atestados_total.empty:
            if arquivos_atestados_mensais:
                st.success(f"✅ Exibindo dados dos {len(arquivos_atestados_mensais)} arquivos mensais importados!")
                
            renderizar_analise_atestados(df_atestados_total)
        else:
            st.info("Não foi possível carregar as bases de afastamento/atestados. Use o botão na barra lateral para importar.")

elif aba_selecionada == "Explorar Dados":
    st.title("Explorar Dados")
    st.subheader("Tabela Dinâmica de Colaboradores")
    
    # Foco em: Exibir st.dataframe com filtros adicionais e st.download_button
    renderizar_exploracao_dados(df_filtrado)