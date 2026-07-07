import streamlit as st

def renderizar_sidebar(df):
    st.sidebar.markdown("## Filtros Globais")
    
    # 1. IDENTIFICAÇÃO DAS COLUNAS DE FORMA SEGURA
    col_empresa = "Empresa" if "Empresa" in df.columns else ("Razão Emp" if "Razão Emp" in df.columns else None)
    # Adapte os nomes abaixo ("Status", "Situação") conforme estiver na sua planilha
    col_status = "Status" if "Status" in df.columns else ("Situação" if "Situação" in df.columns else None)
    
    # --- FILTRO 1: EMPRESAS ---
    if col_empresa:
        opcoes_empresas = sorted(list(df[col_empresa].dropna().unique()))
        empresas_selecionadas = st.sidebar.multiselect(
            "Selecione as Empresas",
            options=opcoes_empresas,
            default=opcoes_empresas,
            key="multiselect_empresas_sidebar_unica" 
        )
    else:
        empresas_selecionadas = []
        st.sidebar.info("Coluna de Empresa não identificada para filtros.")

    # --- FILTRO 2: STATUS DO FUNCIONÁRIO (NOVO) ---
    if col_status:
        # Pega as opções únicas de status (Desligado, Trabalhando, Férias, etc.)
        opcoes_status = sorted(list(df[col_status].dropna().unique()))
        status_selecionados = st.sidebar.multiselect(
            "Status do Funcionário",
            options=opcoes_status,
            default=opcoes_status, # Todos selecionados por padrão
            key="multiselect_status_sidebar_unica"
        )
    else:
        status_selecionados = []
        st.sidebar.info("Coluna de Status não identificada para filtros.")

    # --- APLICAÇÃO DOS FILTROS NO DATAFRAME ---
    # Aplica o filtro de Empresa
    if col_empresa and empresas_selecionadas: # Corrigido o erro de digitação aqui
        df = df[df[col_empresa].isin(empresas_selecionadas)]
        
    # Aplica o filtro de Status
    if col_status and status_selecionados:
        df = df[df[col_status].isin(status_selecionados)]
        
    return df