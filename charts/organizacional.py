import streamlit as st
import plotly.express as px
import pandas as pd

from assets.cores import AZUL_PRINCIPAL, LARANJA_DESTAQUE, BRANCO, PALETA_PRINCIPAL, generate_palette

PALETA_PRINCIPAL = [AZUL_PRINCIPAL, LARANJA_DESTAQUE, "#4e54c8", "#ff9233", "#7f7fd5"]

def _choose_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def renderizar_estrutura_organizacional(df):
    if df.empty:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
        return

    # --- ISOLAMENTO E LIMPEZA CRÍTICA ---
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Buscar colunas de forma flexível para evitar quebras por digitação
    col_situacao = _choose_column(df, ["Situação", "Situacao", "Status"])
    col_setor = _choose_column(df, ["Setor", "SETOR", "Departamento", "Descrição Dpto"])
    col_empresa = _choose_column(df, ["Empresa", "EMPRESA", "Razão Emp"])
    col_nome = _choose_column(df, ["Nome do Empregado", "Nome", "NOME", "Colaborador"])

    # Normalizar situação para letras minúsculas
    if col_situacao:
        df[col_situacao] = df[col_situacao].astype(str).str.lower().str.strip()
    else:
        st.error("Coluna de Situação/Status não localizada na planilha.")
        return

    # --- LINHA 1: ALOCAÇÃO DE SETOR POR EMPRESA ---
    st.markdown("###  Concentração de Colaboradores por Setor e Empresa")
    
    if col_setor and col_empresa:
        df_setor_emp = df.groupby([col_setor, col_empresa]).size().reset_index(name="Quantidade")
        
        fig_setor = px.bar(
            df_setor_emp,
            x=col_setor,
            y="Quantidade",
            color=col_empresa,
            barmode="stack",
            template="plotly_white",
            color_discrete_sequence=PALETA_PRINCIPAL,
            labels={"Quantidade": "Nº de Colaboradores"}
        )
        fig_setor.update_layout(
            paper_bgcolor=BRANCO,
            plot_bgcolor=BRANCO,
            xaxis={'categoryorder':'total descending'},
            height=380
        )
        st.plotly_chart(fig_setor, width="stretch")
    else:
        st.info("Colunas de Setor ou Empresa não encontradas.")

    st.markdown("---")

    # --- LINHA 2: GESTORES E CONTINGÊNCIA ---
    col3, col4 = st.columns(2)

   # --- PAINEL DE CONTINGÊNCIA EM LARGURA TOTAL (SEM COLUNAS) ---
    st.markdown("### Painel de Contingência (Férias e Afastados)")
    
    # Filtrar quem está fora da operação atual de forma tolerante a acentos
    df_ausentes = df[df[col_situacao].isin(["férias", "ferias", "afastado"])]
    
    if col_setor and not df_ausentes.empty:
        df_ausentes_setor = df_ausentes.groupby([col_setor, col_situacao]).size().reset_index()
        
        df_ausentes_setor.columns = ["Setor", "Situacao", "Quantidade"]
        df_ausentes_setor = df_ausentes_setor.sort_values(by="Quantidade", ascending=True)
        
        # Como o gráfico agora é largo, expandi a sequência de cores de forma elegante
        fig_ausentes = px.pie(
            df_ausentes_setor,
            names="Setor",
            values="Quantidade",
            hole=0.4,
            template="plotly_white",
            color_discrete_sequence=[LARANJA_DESTAQUE, AZUL_PRINCIPAL, "#4e54c8", "#e48f24"]
        )
        fig_ausentes.update_traces(
            textinfo="value",
            texttemplate="%{value}"
        )
        fig_ausentes.update_layout(
            paper_bgcolor=BRANCO,
            plot_bgcolor=BRANCO,
            height=380,
            # Centraliza a legenda horizontalmente abaixo do gráfico largo
            legend=dict(orientation="h", y=-0.1, x=0.3)
        )
        st.plotly_chart(fig_ausentes, width="stretch")
        
        # Mini tabela de apoio corrigida para usar col_nome de forma dinâmica
        st.caption("**Lista de Ausências Atuais:**")
        colunas_exibicao = [col for col in [col_nome, col_setor, col_situacao, col_empresa] if col]
        
        # Mudamos o width para None para que a tabela também se ajuste à largura total de forma elegante
        st.dataframe(
        df_ausentes[colunas_exibicao], 
        width="stretch", # Nova sintaxe padronizada para esticar a tabela
        hide_index=True
        )
    else:
        st.success("✅ Excelente! No momento, não há colaboradores em férias ou afastados na seleção atual.")
    st.markdown("---")

    # --- LINHA 3: COMPOSIÇÃO CORPORATIVA E TURNOVER ORGANIZACIONAL ---
    st.markdown("---")

    # --- LINHA 3: COMPOSIÇÃO CORPORATIVA E TURNOVER ORGANIZACIONAL ---
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("###  Divisão de Pessoal por Empresa")
        
        # Procura tanto a coluna criada no loader quanto a coluna real do Excel 'Razão Emp'
        col_empresa_real = _choose_column(df, ["Empresa", "Razão Emp", "Razao Emp", "Razão Emp "])
        
        if col_empresa_real and not df.empty:
            # Filtrar quem está ativo ou trabalhando para mapear o tamanho atual da estrutura
            df_ativos_emp = df[df[col_situacao].isin(["ativo", "trabalhando", "ferias", "férias", "afastado"])]
            
            if df_ativos_emp.empty:
                df_ativos_emp = df # Fallback caso a situação esteja confusa
                
            df_emp_count = df_ativos_emp[col_empresa_real].astype(str).str.strip().value_counts().reset_index()
            df_emp_count.columns = ["Empresa", "Quantidade"]
            df_emp_count = df_emp_count[df_emp_count["Empresa"].str.lower() != "nan"]
            
            fig_emp = px.pie(
                df_emp_count,
                names="Empresa",
                values="Quantidade",
                hole=0.4,
                template="plotly_white",
                color_discrete_sequence=PALETA_PRINCIPAL
            )
            fig_emp.update_traces(
                textinfo="value",
                texttemplate="%{value}"
            )
            fig_emp.update_layout(
                paper_bgcolor=BRANCO,
                height=350,
                legend=dict(orientation="h", y=-0.1, x=0.1)
            )
            st.plotly_chart(fig_emp, width="stretch")
        else:
            st.info("Dados de empresa insuficientes.")

    with col6:
        st.markdown("### Motivos de Desligamento Organizacional")
        
        # Buscar variações exatas da coluna informada
        col_motivo = _choose_column(df, ["Motivo Demissão", "Motivo demissão", "Motivo Desligamento", "Motivo"])
        
        if col_motivo:
            # CORREÇÃO CRÍTICA: Pegamos diretamente qualquer registro onde o motivo não esteja em branco
            df_demissoes = df.copy()
            df_demissoes[col_motivo] = df_demissoes[col_motivo].astype(str).str.strip()
            
            # Filtra tirando vazios, nulos ou 'nan' textuais
            df_filtro_motivos = df_demissoes[
                (df_demissoes[col_motivo] != "") & 
                (df_demissoes[col_motivo].str.lower() != "nan") &
                (df_demissoes[col_motivo].str.lower() != "null")
            ]
            
            if not df_filtro_motivos.empty:
                df_m_count = df_filtro_motivos[col_motivo].value_counts().reset_index()
                df_m_count.columns = ["Motivo", "Total"]
                df_m_count = df_m_count.head(6).sort_values(by="Total", ascending=True)

                cores_motivos = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_m_count))

                fig_motivos = px.bar(
                    df_m_count,
                    x="Total",
                    y="Motivo",
                    orientation="h",
                    template="plotly_white",
                    text="Total",
                    labels={"Total": "Quantidade de Desligamentos"}
                )
                fig_motivos.update_traces(marker_color=cores_motivos, textposition="outside", cliponaxis=False)
                fig_motivos.update_layout(
                    paper_bgcolor=BRANCO,
                    plot_bgcolor=BRANCO,
                    height=350,
                    margin=dict(l=180, r=20, t=40, b=40),
                    yaxis_title=None
                )
                st.plotly_chart(fig_motivos, width="stretch")
            else:
                st.info("Nenhum registro de motivo de demissão preenchido encontrado na base filtrada.")
        else:
            st.info("Coluna de Motivo Demissão não encontrada na base.")