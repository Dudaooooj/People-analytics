import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIGURAÇÃO DE CORES (IDÊNTICO AO CORES.PY)
# ============================================================
AZUL_PRINCIPAL = "#28275a"
LARANJA_DESTAQUE = "#d5741b"
BRANCO = "#ffffff"
CINZA_CLARO = "#f8f9fa"
CINZA_TEXTO = "#495057"

PALETA_PRINCIPAL = [AZUL_PRINCIPAL, LARANJA_DESTAQUE, "#4e54c8", "#ff9233", "#7f7fd5"]

def renderizar_analise_demografica(df):
    if df.empty:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
        return

    # --- ISOLAMENTO E LIMPEZA DE COLUNAS CRÍTICA ---
    df = df.copy()
    df.columns = df.columns.str.strip() # Remove espaços extras invisíveis das colunas

    # ============================================================
    # LINHA 1: IDADE E GRAU DE INSTRUÇÃO
    # ============================================================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Distribuição por Idade")
        col_idade = None
        for c in ["Idade", "Faixa etária e gerações", "Faixa Etária", "Idade (Anos)"]:
            if c in df.columns:
                col_idade = c
                break
        
        if col_idade:
            if pd.api.types.is_numeric_dtype(df[col_idade]):
                fig_idade = px.histogram(
                    df,
                    x=col_idade,
                    nbins=15,
                    title="Distribuição de Idades (Histograma)",
                    template="plotly_white",
                    color_discrete_sequence=[AZUL_PRINCIPAL],
                    labels={col_idade: "Idade (Anos)", "count": "Nº de Colaboradores"}
                )
                fig_idade.update_layout(yaxis_title="Nº de Colaboradores")
            else:
                df_idade = df[col_idade].value_counts().reset_index(name="Quantidade")
                df_idade.columns = [col_idade, "Quantidade"]
                df_idade = df_idade.sort_values(by="Quantidade", ascending=True)
                
                # Destacar dinamicamente a maior barra
                max_val = df_idade["Quantidade"].max()
                cores_idade = [LARANJA_DESTAQUE if q == max_val else AZUL_PRINCIPAL for q in df_idade["Quantidade"]]
                
                fig_idade = px.bar(
                    df_idade,
                    x="Quantidade",
                    y=col_idade,
                    orientation="h",
                    title="Distribuição por Faixa Etária",
                    template="plotly_white",
                    labels={col_idade: "Faixa Etária", "Quantidade": "Nº de Colaboradores"}
                )
                fig_idade.update_traces(marker_color=cores_idade)
                fig_idade.update_layout(margin=dict(l=120, r=20, t=40, b=40))
            
            fig_idade.update_layout(paper_bgcolor=BRANCO, plot_bgcolor=BRANCO, height=350)
            st.plotly_chart(fig_idade, width="stretch")
        else:
            st.info("Coluna de Idade não encontrada na base.")

    with col2:
        st.markdown("### Nível de Formação")
        col_esc = None
        for c in ["Grau instrução", "Grau Instrução", "Grau de instrução", "Grau de Instrução", "Escolaridade"]:
            if c in df.columns:
                col_esc = c
                break
        
        if col_esc:
            df_esc = df[col_esc].astype(str).str.strip()
            df_esc = df_esc[(df_esc != "") & (df_esc.str.lower() != "nan")]
            df_cc = df_esc.value_counts().reset_index(name="Quantidade")
            df_cc.columns = [col_esc, "Quantidade"]
            df_cc = df_cc.sort_values(by="Quantidade", ascending=True)
            
            # Destacar dinamicamente a maior barra
            max_val = df_cc["Quantidade"].max()
            cores_esc = [LARANJA_DESTAQUE if q == max_val else AZUL_PRINCIPAL for q in df_cc["Quantidade"]]
            
            fig_esc = px.bar(
                df_cc,
                x="Quantidade",
                y=col_esc,
                orientation="h",
                title="Nível de Formação",
                template="plotly_white",
                labels={col_esc: "Graduação", "Quantidade": "Nº de Colaboradores"}
            )
            fig_esc.update_traces(marker_color=cores_esc)
            fig_esc.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO, 
                height=350,
                margin=dict(l=150, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_esc, width="stretch")
        else:
            st.info("Coluna de Grau Instrução não encontrada na base.")

    st.markdown("---")

    # ============================================================
    # LINHA 2: RAÇA/ETNIA E ESTADO CIVIL
    # ============================================================
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Raça e Etnia")
        col_raca = None
        for c in ["Raça/Cor", "Raça/cor", "Raça e etnia", "Raça", "Raca", "Raça / Cor"]:
            if c in df.columns:
                col_raca = c
                break
        
        if col_raca:
            df_raca = df[col_raca].astype(str).str.strip()
            df_raca = df_raca[(df_raca != "") & (df_raca.str.lower() != "nan")]
            df_rcc = df_raca.value_counts().reset_index(name="Quantidade")
            df_rcc.columns = [col_raca, "Quantidade"]
            df_rcc = df_rcc.sort_values(by="Quantidade", ascending=True)
            
            # Destacar dinamicamente a maior barra
            max_val = df_rcc["Quantidade"].max()
            cores_raca = [LARANJA_DESTAQUE if q == max_val else AZUL_PRINCIPAL for q in df_rcc["Quantidade"]]
            
            fig_raca = px.bar(
                df_rcc,
                x="Quantidade",
                y=col_raca,
                orientation="h",
                title="Distribuição por Raça / Etnia",
                template="plotly_white",
                labels={col_raca: "Raça / Cor", "Quantidade": "Nº de Colaboradores"}
            )
            fig_raca.update_traces(marker_color=cores_raca)
            fig_raca.update_layout(
                paper_bgcolor=BRANCO,
                plot_bgcolor=BRANCO,
                height=350,
                margin=dict(l=120, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_raca, width="stretch")
        else:
            st.info("Coluna de Raça/Cor não encontrada na base.")

    with col4:
        st.markdown("### Estado Civil")
        col_civil = None
        for c in ["Estado civil", "Estado Civil", "Estado civil e composição familiar", "Situação Conjugal"]:
            if c in df.columns:
                col_civil = c
                break
                
        if col_civil:
            df_civil = df[col_civil].astype(str).str.strip()
            df_civil = df_civil[(df_civil != "") & (df_civil.str.lower() != "nan")]
            df_cvc = df_civil.value_counts().reset_index(name="Quantidade")
            df_cvc.columns = [col_civil, "Quantidade"]
            df_cvc = df_cvc.sort_values(by="Quantidade", ascending=True)
            
            # Destacar dinamicamente a maior barra
            max_val = df_cvc["Quantidade"].max()
            cores_civil = [LARANJA_DESTAQUE if q == max_val else AZUL_PRINCIPAL for q in df_cvc["Quantidade"]]
            
            fig_civil = px.bar(
                df_cvc,
                x="Quantidade",
                y=col_civil,
                orientation="h",
                title="Composição por Estado Civil",
                template="plotly_white",
                labels={col_civil: "Estado Civil", "Quantidade": "Nº de Colaboradores"}
            )
            fig_civil.update_traces(marker_color=cores_civil)
            fig_civil.update_layout(
                paper_bgcolor=BRANCO,
                plot_bgcolor=BRANCO,
                height=350,
                margin=dict(l=120, r=20, t=40, b=40),
                yaxis_title=None
            )
            st.plotly_chart(fig_civil, width="stretch")
        else:
            st.info("Coluna de Estado Civil não encontrada na base.")

    st.markdown("---")

    # ============================================================
    # LINHA 3: GÊNERO E GEOGRAFIA
    # ============================================================
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("### Gênero / Sexo")
        col_sexo = "Sexo" if "Sexo" in df.columns else ("Gênero" if "Gênero" in df.columns else "Sexo ")
        
        if col_sexo in df.columns:
            df_sexo = df[col_sexo].astype(str).str.strip()
            df_sexo = df_sexo[(df_sexo != "") & (df_sexo.str.lower() != "nan")]
            df_scc = df_sexo.value_counts().reset_index(name="Quantidade")
            df_scc.columns = [col_sexo, "Quantidade"]
            
            fig_sexo = px.pie(
                df_scc,
                names=col_sexo,
                values="Quantidade",
                hole=0.5,
                title="Proporção por Sexo",
                template="plotly_white",
                color_discrete_sequence=[AZUL_PRINCIPAL, LARANJA_DESTAQUE]
            )
            fig_sexo.update_layout(
                paper_bgcolor=BRANCO, 
                height=350,
                legend=dict(orientation="h", y=-0.1, x=0.2)
            )
            st.plotly_chart(fig_sexo, width="stretch")
        else:
            st.info("Coluna de Sexo/Gênero não encontrada na base.")

    with col6:
        st.markdown("### Distribuição por Cidade")
        col_cidade = "Cidade" if "Cidade" in df.columns else "Cidade"
        
        if col_cidade in df.columns:
            df_cid = df[col_cidade].astype(str).str.strip()
            df_cid = df_cid[(df_cid != "") & (df_cid.str.lower() != "nan")]
            df_cid_count = df_cid.value_counts().reset_index(name="Quantidade")
            df_cid_count.columns = [col_cidade, "Quantidade"]
            df_cid_count = df_cid_count.head(8).sort_values(by="Quantidade", ascending=True)
            
            # Destacar dinamicamente a maior barra
            max_val = df_cid_count["Quantidade"].max()
            cores_cidade = [LARANJA_DESTAQUE if q == max_val else AZUL_PRINCIPAL for q in df_cid_count["Quantidade"]]
            
            fig_cid = px.bar(
                df_cid_count,
                x="Quantidade",
                y=col_cidade,
                orientation="h",
                title="Top 8 Cidades com mais Colaboradores",
                template="plotly_white",
                labels={col_cidade: "Cidade", "Quantidade": "Nº de Colaboradores"}
            )
            fig_cid.update_traces(marker_color=cores_cidade)
            fig_cid.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO, 
                height=350,
                margin=dict(l=120, r=20, t=40, b=40),
                yaxis_title=None
            )
            st.plotly_chart(fig_cid, width="stretch")
        else:
            st.info("Coluna de Cidade não encontrada na base.")