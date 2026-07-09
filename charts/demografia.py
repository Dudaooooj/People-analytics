import streamlit as st
import pandas as pd
import plotly.express as px

from assets.cores import AZUL_PRINCIPAL, LARANJA_DESTAQUE, BRANCO, PALETA_PRINCIPAL, generate_palette


def renderizar_analise_demografica(df):
    if df.empty:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
        return

    df = df.copy()
    df.columns = df.columns.str.strip() # Remove espaços extras invisíveis das colunas

    # LINHA 1: IDADE E GRAU DE INSTRUÇÃO
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Distribuição por Idade")
        col_idade = None
        for c in ["Idade", "Faixa etária e gerações", "Faixa Etária", "Idade (Anos)"]:
            if c in df.columns:
                col_idade = c
                break
        
        if col_idade:
            # Importações necessárias para processar as faixas e cores
            import numpy as np
            import plotly.colors

            # Mapeamento do gradiente azul para ciano
            # Mapeamento do gradiente ligando o seu Azul diretamente ao seu Laranja
            # Adicionei um tom intermediário (roxo/marrom discreto) para a transição não passar por um cinza morto
            combinacao_azul_laranja = ["#28275a", "#5a3a5f", "#8d4e5a", "#bd6448", "#d5741b"]

            if pd.api.types.is_numeric_dtype(df[col_idade]):
                idades_limpas = pd.to_numeric(df[col_idade], errors="coerce").dropna()
                
                if not idades_limpas.empty:
                    # --- FAIXAS LIMPAS: De 5 em 5 anos ---
                    min_idade = int(np.floor(idades_limpas.min() / 5) * 5)
                    max_idade = int(np.ceil(idades_limpas.max() / 5) * 5)
                    bins_custom_idade = list(range(min_idade, max_idade + 6, 5))
                    
                    bins_id = pd.cut(idades_limpas, bins=bins_custom_idade, right=False)
                    df_idade_bar = bins_id.value_counts().sort_index().reset_index()
                    df_idade_bar.columns = ["Intervalo", "Nº de Colaboradores"]
                    
                    df_idade_bar["Intervalo_Str"] = df_idade_bar["Intervalo"].apply(lambda x: f"{int(x.left)}-{int(x.right)}")
                    
                    # Amostra as cores ao longo da nova escala de transição Azul -> Laranja
                    cores_idade = plotly.colors.sample_colorscale(combinacao_azul_laranja, len(df_idade_bar))

                    fig_idade = px.bar(
                        df_idade_bar,
                        x="Intervalo_Str",
                        y="Nº de Colaboradores",
                        title="Distribuição de Idades (Histograma Padronizado)",
                        template="plotly_white",
                        color="Intervalo_Str", 
                        color_discrete_sequence=cores_idade, # Aplica o degradê misto
                        labels={"Intervalo_Str": "Idade (Anos)", "Nº de Colaboradores": "Nº de Colaboradores"},
                        text_auto=True 
                    )
                else:
                    fig_idade = None
            else:
                # Caso a base de dados já venha com texto/faixas prontas (ex: "De 20 a 30 anos")
                df_idade = df[col_idade].value_counts().reset_index(name="Quantidade")
                df_idade.columns = [col_idade, "Quantidade"]
                df_idade = df_idade.sort_values(by="Quantidade", ascending=True)
                
                cores_idade = plotly.colors.sample_colorscale(combinacao_azul_ciano, len(df_idade))
                
                fig_idade = px.bar(
                    df_idade,
                    x="Quantidade",
                    y=col_idade,
                    orientation="h",
                    title="Distribuição por Faixa Etária",
                    template="plotly_white",
                    color=col_idade,
                    color_discrete_sequence=cores_idade,
                    text="Quantidade", 
                    labels={col_idade: "Faixa Etária", "Quantidade": "Nº de Colaboradores"}
                )
            
            if fig_idade:
                fig_idade.update_traces(textposition="outside", cliponaxis=False)
                fig_idade.update_layout(
                    paper_bgcolor=BRANCO, 
                    plot_bgcolor=BRANCO, 
                    height=380,
                    showlegend=False, # Oculta a legenda repetitiva
                    margin=dict(l=60, r=40, t=80, b=40), 
                    title_pad=dict(b=20) 
                )
                if not pd.api.types.is_numeric_dtype(df[col_idade]):
                    # Ajuste de margem caso o gráfico seja o horizontal textual
                    fig_idade.update_layout(margin=dict(l=120, r=40, t=80, b=40))
                
                st.plotly_chart(fig_idade, width="stretch")
            else:
                st.info("Dados de idade insuficientes.")
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
            
            cores_esc = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_cc))
            
            fig_esc = px.bar(
                df_cc,
                x="Quantidade",
                y=col_esc,
                orientation="h",
                title="Nível de Formação",
                template="plotly_white",
                text="Quantidade", # Ativa o número na barra horizontal
                labels={col_esc: "Graduação", "Quantidade": "Nº de Colaboradores"}
            )
            fig_esc.update_traces(marker_color=cores_esc, textposition="outside", cliponaxis=False)
            fig_esc.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO, 
                height=380,
                margin=dict(l=150, r=40, t=80, b=40), # Margens ajustadas
                title_pad=dict(b=20)
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
            
            cores_raca = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_rcc))
            
            fig_raca = px.bar(
                df_rcc,
                x="Quantidade",
                y=col_raca,
                orientation="h",
                title="Distribuição por Raça / Etnia",
                template="plotly_white",
                text="Quantidade", # Ativa o número na barra horizontal
                labels={col_raca: "Raça / Cor", "Quantidade": "Nº de Colaboradores"}
            )
            fig_raca.update_traces(marker_color=cores_raca, textposition="outside", cliponaxis=False)
            fig_raca.update_layout(
                paper_bgcolor=BRANCO,
                plot_bgcolor=BRANCO,
                height=380,
                margin=dict(l=120, r=40, t=80, b=40),
                title_pad=dict(b=20)
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
            
            cores_civil = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_cvc))
            
            fig_civil = px.bar(
                df_cvc,
                x="Quantidade",
                y=col_civil,
                orientation="h",
                title="Composição por Estado Civil",
                template="plotly_white",
                text="Quantidade", # Ativa o número na barra horizontal
                labels={col_civil: "Estado Civil", "Quantidade": "Nº de Colaboradores"}
            )
            fig_civil.update_traces(marker_color=cores_civil, textposition="outside", cliponaxis=False)
            fig_civil.update_layout(
                paper_bgcolor=BRANCO,
                plot_bgcolor=BRANCO,
                height=380,
                margin=dict(l=120, r=40, t=80, b=40),
                title_pad=dict(b=20),
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
                title="Distribuição por Sexo (Valores Absolutos)",
                template="plotly_white",
                color_discrete_sequence=[AZUL_PRINCIPAL, LARANJA_DESTAQUE]
            )
            
            # --- CONFIGURAÇÃO PARA EXIBIR NÚMEROS REAIS ---
            fig_sexo.update_traces(
                textinfo="value",  # Define para mostrar o valor bruto em vez de 'percent'
                texttemplate="%{value}"  # Garante a formatação pura do número inteiro
            )
            
            fig_sexo.update_layout(
                paper_bgcolor=BRANCO, 
                height=380,
                margin=dict(t=80, b=40),
                title_pad=dict(b=20),
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
            
            cores_cidade = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_cid_count))
            
            fig_cid = px.bar(
                df_cid_count,
                x="Quantidade",
                y=col_cidade,
                orientation="h",
                title="Top 8 Cidades com mais Colaboradores",
                template="plotly_white",
                text="Quantidade", # Ativa o número na barra horizontal
                labels={col_cidade: "Cidade", "Quantidade": "Nº de Colaboradores"}
            )
            fig_cid.update_traces(marker_color=cores_cidade, textposition="outside", cliponaxis=False)
            fig_cid.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO, 
                height=380,
                margin=dict(l=120, r=40, t=80, b=40),
                title_pad=dict(b=20),
                yaxis_title=None
            )
            st.plotly_chart(fig_cid, width="stretch")
        else:
            st.info("Coluna de Cidade não encontrada na base.")