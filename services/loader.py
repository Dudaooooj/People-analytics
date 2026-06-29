import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados_consolidados():
    df_servicos = pd.read_excel("dados/1314 - Empregados Led servicos.xls")
    df_servicos["Empresa"] = "Led Serviços"
    
    df_internet = pd.read_excel("dados/1315 - Empregados Led internet.xls")
    df_internet["Empresa"] = "Led Internet"
    
    df_gp4 = pd.read_excel("dados/1629 - Empregados GP4.xls")
    df_gp4["Empresa"] = "GP4"
    
    # Concatenar todas as empresas em um único banco de dados
    df_consolidado = pd.concat([df_servicos, df_internet, df_gp4], ignore_index=True)
    
    return df_consolidado