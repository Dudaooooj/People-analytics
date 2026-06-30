import streamlit as st
import pandas as pd
import plotly.express as px

def renderizar_painel_executivo(df):
    # --- TRATAMENTO INICIAL DE DATAS ---
    # Garantir que as colunas de data estão no formato correto do Pandas
    df["Admissão"] = pd.to_datetime(df["Admissão"], errors="coerce")
    df["Data Demissão"] = pd.to_datetime(df["Data Demissão"], errors="coerce")
    
    # --- CÁLCULO DOS KPIS ---
    # 1. Total de Colaboradores (Histórico total na base filtrada)
    total_colaboradores = len(df)
    
    # 2. Ativos (Filtrando pela coluna 'Situação')
    # Tratamos com .str.lower() e .str.strip() para evitar erros de digitação/espaços no Excel
    ativos = len(df[df["Situação"].str.lower().str.strip() == "ativo"])
    
    # 3. Fora de Operação (Férias + Afastados)
    fora_operacao = len(df[df["Situação"].str.lower().str.strip().isin(["férias", "ferias", "afastado"])])
    
    # 4. Desligados
    desligados = len(df[df["Situação"].str.lower().str.strip() == "desligado"])

    # --- RENDERIZAÇÃO DOS KPIS NO TOPO ---
    # Criando colunas no Streamlit para os cards ficarem lado a lado
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Histórico", value=f"{total_colaboradores} colab.")
    with col2:
        st.metric(label="🟢 Colaboradores Ativos", value=ativos)
    with col3:
        st.metric(label="🟡 Em Férias / Afastados", value=fora_operacao)
    with col4:
        st.metric(label="🔴 Total Desligados", value=desligados)
        
    st.markdown("---")
    
    # --- GRÁFICO TEMPORAL (MOVIMENTAÇÃO / TURNOVER) ---
    st.subheader("📈 Histórico de Movimentação (Admissões vs. Demissões)")
    
    # Criando agrupamentos por mês/ano para ver a evolução
    # Criamos uma coluna de Ano-Mês para agrupar as admissões
    df_adm = df[df["Data Admissão"].notna()].copy()
    df_adm["Mes_Ano"] = df_adm["Data Admissão"].dt.to_period("M")
    admissoes_no_tempo = df_adm.groupby("Mes_Ano").size().reset_index(name="Admissões")
    
    # Criamos uma coluna de Ano-Mês para agrupar as demissões
    df_dem = df[df["Data Demissão"].notna()].copy()
    df_dem["Mes_Ano"] = df_dem["Data Demissão"].dt.to_period("M")
    demissoes_no_tempo = df_dem.groupby("Mes_Ano").size().reset_index(name="Demissões")
    
    # Unir os dois históricos na mesma linha do tempo
    movimentacao = pd.merge(admissoes_no_tempo, demissoes_no_tempo, on="Mes_Ano", how="outer").fillna(0)
    
    # Converter 'Mes_Ano' de volta para string para o Plotly plotar corretamente
    movimentacao["Mes_Ano"] = movimentacao["Mes_Ano"].astype(str)
    movimentacao = movimentacao.sort_values("Mes_Ano")
    
    if not movimentacao.empty:
        # Plotando o gráfico de linhas comparativo
        fig = px.line(
            movimentacao, 
            x="Mes_Ano", 
            y=["Admissões", "Demissões"],
            labels={"value": "Quantidade de Funcionários", "Mes_Ano": "Período (Mês/Ano)", "variable": "Movimentação"},
            color_discrete_map={"Admissões": "#2ecc71", "Demissões": "#e74c3c"}, # Verde para Adm, Vermelho para Dem
            markers=True
        )
        
        fig.update_layout(hovermode="x unified", legend_orientation="h", legend_y=1.1)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados de datas suficientes para gerar o gráfico temporal de movimentação.")