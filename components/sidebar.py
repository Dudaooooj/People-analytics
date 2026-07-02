import streamlit as st

def renderizar_sidebar(df):
    st.sidebar.markdown("## Filtros Globais")
    
    # Identifica a coluna de empresa de forma segura
    col_empresa = "Empresa" if "Empresa" in df.columns else ("Razão Emp" if "Razão Emp" in df.columns else None)
    
    if col_empresa:
        # Pega as opções únicas de empresas presentes na planilha
        opcoes_empresas = sorted(list(df[col_empresa].dropna().unique()))
        
        # 1. ADICIONADO A KEY ÚNICA AQUI PARA MATAR O ERRO
        empresas_selecionadas = st.sidebar.multiselect(
            "Selecione as Empresas",
            options=opcoes_empresas,
            default=opcoes_empresas,
            key="multiselect_empresas_sidebar_unica" 
        )
    else:
        empresas_selecionadas = []
        st.sidebar.info("Coluna de Empresa não identificada para filtros.")

    # --- FILTRAGEM DOS DADOS ---
    # Aplica o filtro no DataFrame se o usuário desmarcar alguma empresa
    if col_empresa and empresas_selecionadas:
        df = df[df[col_empresa].isin(empresas_selecionadas)]
        
    return df