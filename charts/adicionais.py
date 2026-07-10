import streamlit as st
import pandas as pd
import plotly.express as px

from assets.cores import AZUL_PRINCIPAL, LARANJA_DESTAQUE, BRANCO, generate_palette


def _encontrar_coluna(df, candidatos):
    for c in candidatos:
        if c in df.columns:
            return c
    # procurar versão insensível a caixa
    lowmap = {col.lower(): col for col in df.columns}
    for c in candidatos:
        if c.lower() in lowmap:
            return lowmap[c.lower()]
    return None

def renderizar_analise_atestados(df):
    
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
        return

    df = df.copy()
    
    # --- BLINDAGEM MÁXIMA DE CABEÇALHO ---
    df.columns = [str(c).strip() for c in df.columns]
    colunas_minusculas = [c.lower() for c in df.columns]

    # 1. Busca Manual Direta para o CID (Case-Insensitive)
    col_cid = None
    candidatos_cid_lower = ["cid", "cid principal", "codigo cid", "código cid", "cid1", "cid_1"]
    
    for i, col_low in enumerate(colunas_minusculas):
        if col_low in candidatos_cid_lower:
            col_cid = df.columns[i]
            break

    # 2. Busca para os demais campos usando a sua função padrão
    candidatos_pessoa = ["CPF", "Matrícula", "Matricula", "Nome", "Nome completo", "Funcionário", "Funcionario", "Registro"]
    candidatos_data_inicio = ["Início Afast.", "Início Afast", "Data início", "Data Inicio", "Data_Inicio"]
    candidatos_data_fim = ["Fim Afast.", "Fim Afast", "Data término", "Data Termino", "Data_Fim"]
    candidatos_dias = ["Dias afastado", "Dias Afastado", "Dias Afastamento", "Dias"]

    col_pessoa = _encontrar_coluna(df, candidatos_pessoa)
    col_data_inicio = _encontrar_coluna(df, candidatos_data_inicio)
    col_data_fim = _encontrar_coluna(df, candidatos_data_fim)
    col_dias = _encontrar_coluna(df, candidatos_dias)

    # --- TRATAMENTO DINÂMICO DE AFASTAMENTOS EM ABERTO ---
    if col_data_inicio and col_data_fim:
        df[col_data_inicio] = pd.to_datetime(df[col_data_inicio], errors="coerce")
        df[col_data_fim] = pd.to_datetime(df[col_data_fim], errors="coerce")
        
        # LÓGICA ATUAL: Se tem início mas não tem fim, preenche com a data de hoje (afastamento ativo)
        hoje = pd.to_datetime("today")
        fim_ajustado = df[col_data_fim].fillna(hoje)
        
        # Se a coluna de dias nativa não existir, calcula usando o fim ajustado
        if not col_dias:
            df["Dias Afastado Calculado"] = (fim_ajustado - df[col_data_inicio]).dt.days + 1
            col_dias = "Dias Afastado Calculado"
        else:
            # Se a coluna nativa existir mas estiver vazia onde o fim está em branco, recalculamos ali
            dias_calc = (fim_ajustado - df[col_data_inicio]).dt.days + 1
            df[col_dias] = pd.to_numeric(df[col_dias], errors="coerce").fillna(dias_calc)

    # ------------------ Gráfico top CIDs ------------------
    st.markdown("### Top CIDs (atestados)")
    if col_cid:
        s = df[col_cid].astype(str).str.strip()
        s = s[(s != "") & (s.str.lower() != "nan") & (s.str.lower() != "none")]
        
        if s.empty:
            st.info("Coluna de CID encontrada mas sem valores relevantes.")
        else:
            df_cid_count = s.value_counts().reset_index(name="Quantidade")
            df_cid_count.columns = [col_cid, "Quantidade"]
            df_cid_count = df_cid_count.head(8).sort_values(by="Quantidade", ascending=True)

            cores = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_cid_count))
            fig = px.bar(
                df_cid_count,
                x="Quantidade",
                y=col_cid,
                orientation="h",
                title=f"Top {len(df_cid_count)} CIDs mais frequentes",
                template="plotly_white",
                text="Quantidade",
                labels={col_cid: "CID", "Quantidade": "Nº de Atestados"}
            )
            fig.update_traces(marker_color=cores, textposition="outside", cliponaxis=False)
            fig.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO, 
                height=380, 
                margin=dict(l=120, r=40, t=80, b=40)
            )
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("Coluna de CID não encontrada na base.")

    st.markdown("---")

    # ------------------ Tabela por pessoa ------------------
    st.markdown("### Quantidade de atestados e tempo de afastamento por pessoa")

    if not col_pessoa:
        st.info("Não foi possível identificar uma coluna de identificação de pessoa (CPF / Matrícula / Nome).")
        return

    working = df[[col_pessoa]].copy()
    working[col_pessoa] = working[col_pessoa].astype(str).str.strip()

    # Puxa os dias já tratados e corrigidos com a data de hoje lá de cima
    if col_dias:
        dias_series = pd.to_numeric(df[col_dias], errors="coerce")
    else:
        dias_series = pd.Series([0] * len(df))

    working["_dias_atestado"] = dias_series

    # Contabiliza por pessoa de forma limpa
    grp = working.groupby(col_pessoa).agg(
        Quantidade_Atestados=(col_pessoa, "size"),
        Total_Dias_Afastamento=("_dias_atestado", "sum")
    ).reset_index()

    # Garante formatação como número inteiro na tabela
    grp["Total_Dias_Afastamento"] = grp["Total_Dias_Afastamento"].fillna(0).astype(int)
    grp = grp.sort_values(by="Quantidade_Atestados", ascending=False)

    # Formatação e exibição final
    grp_display = grp.copy()
    grp_display.columns = [col_pessoa, "Quantidade de Atestados", "Total Dias Afastamento"]

    st.dataframe(grp_display.reset_index(drop=True), width="stretch")

    st.markdown("\n> 💡 **Nota métrica:** Para registros sem data de término informada, o sistema considera a data atual para o cálculo volumétrico de dias em aberto.")