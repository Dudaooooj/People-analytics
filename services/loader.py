import pandas as pd
import streamlit as st
import os
import glob

def _ler_excel_flexivel(caminho_base, dtype_dict):
    """Tenta ler o arquivo como .xlsx ou .xls automaticamente"""
    extensoes = [".xlsx", ".xls"]
    for ext in extensoes:
        caminho_completo = caminho_base + ext
        if os.path.exists(caminho_completo):
            try:
                if ext == ".xls":
                    return pd.read_excel(caminho_completo, dtype=dtype_dict, engine="xlrd")
                else:
                    return pd.read_excel(caminho_completo, dtype=dtype_dict)
            except Exception:
                return pd.read_excel(caminho_completo, dtype=dtype_dict)
                
    st.error(f"Arquivo não encontrado: {caminho_base}.xls ou .xlsx")
    return pd.DataFrame()


def _find_and_read(patterns, dtype_dict=None):
    """Procura por arquivos que casem com os padrões (glob) e lê o primeiro encontrado."""
    for p in patterns:
        matches = glob.glob(p)
        if matches:
            caminho = matches[0]
            try:
                return pd.read_excel(caminho, dtype=dtype_dict)
            except Exception:
                return pd.read_excel(caminho)
    return pd.DataFrame()

@st.cache_data
def carregar_dados_consolidados():
    # 1. Definir colunas de identificação como string para evitar quebras no PyArrow
    tipos_obrigatorios = {
        "Celular": str,
        "CPF": str,
        "Telefone": str,
        "Matrícula": str,
        "Matricula": str
    }
    
    # 2. Carregar as planilhas tentando vários padrões de nome (tolerante a espaços e prefixos numéricos)
    df_servicos = _find_and_read([
        "dados/Empregados_Ledservicos.*",
        "dados/*servicos*.xls*",
        "dados/*Led*servicos*.xls*",
        "dados/1314*",
    ], tipos_obrigatorios)
    if not df_servicos.empty:
        df_servicos["Empresa"] = "Led Serviços"

    df_internet = _find_and_read([
        "dados/Empregados_Ledinternet.*",
        "dados/*internet*.xls*",
        "dados/*Led*internet*.xls*",
        "dados/1315*",
    ], tipos_obrigatorios)
    if not df_internet.empty:
        df_internet["Empresa"] = "Led Internet"

    df_gp4 = _find_and_read([
        "dados/Empregados_GP4.*",
        "dados/*GP4*.xls*",
        "dados/1629*",
    ], tipos_obrigatorios)
    if not df_gp4.empty:
        df_gp4["Empresa"] = "GP4"
    
    # Filtrar apenas os DataFrames que não estão vazios antes de juntar
    bases = [df for df in [df_servicos, df_internet, df_gp4] if not df.empty]
    
    if not bases:
        st.warning("Nenhuma base de dados foi carregada com sucesso. Verifique a pasta 'dados'.")
        return pd.DataFrame()
        
    # Concatenar as bases de forma limpa
    df_consolidado = pd.concat(bases, ignore_index=True)
    
    # 3. LIMPEZA DA COLUNA DE SALÁRIO
    col_salario = None
    for c in ["Salário", "Salario"]:
        if c in df_consolidado.columns:
            col_salario = c 
            break
            
    if col_salario:
        # Limpar formatação de moeda com segurança antes de converter para float
        df_consolidado[col_salario] = (
            df_consolidado[col_salario]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)  # Remove pontos de milhar
            .str.replace(",", ".", regex=False)  # Converte vírgula decimal para ponto
            .str.strip()
        )
        # Transforma em numérico real. O que for inválido vira NaN
        df_consolidado[col_salario] = pd.to_numeric(df_consolidado[col_salario], errors="coerce")

    # 4. TRATAMENTO SEGURO DE TEXTOS PARA O PYARROW
    colunas_texto = ["Celular", "CPF", "Telefone", "Matrícula", "Matricula", "Cargo", "CARGO", "Função", "Funcao", "Gestor direto", "Gestor", "Gestor Direto"]
    for col in colunas_texto:
        if col in df_consolidado.columns:
            df_consolidado[col] = df_consolidado[col].astype(str).replace("nan", "").fillna("")

    return df_consolidado