import streamlit as st

def renderizar_sidebar(df):
    st.sidebar.title("Filtros Globais")
    
    # Filtro de Empresa (Multiselect para permitir selecionar uma, duas ou as três juntas)
    empresas_disponiveis = df["Empresa"].unique().tolist()
    empresas_selecionadas = st.sidebar.multiselect(
        "Selecione as Empresas",
        options=empresas_disponiveis,
        default=empresas_disponiveis # Começa com tudo selecionado (Consolidado)
    )
    
    # Filtrar o dataframe com base na seleção
    df_filtrado = df[df["Empresa"].isin(empresas_selecionadas)]
    
    return df_filtrado