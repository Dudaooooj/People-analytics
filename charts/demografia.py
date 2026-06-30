import streamlit as st
import plotly.express as px
import pandas as pd

def renderizar_analise_demografica(df):
    if df.empty:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
        return

    # --- LINHA 1: FAIXA ETÁRIA E ESCOLARIDADE ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎂 Distribuição por Faixa Etária e Gerações")
        # Verifica qual coluna exata você tem na base (ajuste o nome se necessário)
        col_idade = "Faixa etária e gerações" if "Faixa etária e gerações" in df.columns else "Faixa Etária"
        
        if col_idade in df.columns:
            # Contar colaboradores por faixa
            df_idade = df[col_idade].value_counts().reset_index(name="Quantidade")
            df_idade.columns = [col_idade, "Quantidade"]
            
            # Gráfico de barras horizontais (bom para ler nomes longos de faixas/gerações)
            fig_idade = px.bar(
                df_idade,
                x="Quantidade",
                y=col_idade,
                orientation="h",
                color="Quantidade",
                color_continuous_scale="Blues",
                labels={col_idade: "Faixa / Geração", "Quantidade": "Nº de Colaboradores"}
            )
            fig_idade.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig_idade, use_container_width=True)
        else:
            st.info("Coluna de Faixa Etária não encontrada na base.")

    with col2:
        st.markdown("### 🎓 Nível de Escolaridade e Formação")
        col_esc = "Escolaridade e formação" if "Escolaridade e formação" in df.columns else "Escolaridade"
        
        if col_esc in df.columns:
            df_esc = df[col_esc].value_counts().reset_index(name="Quantidade")
            df_esc.columns = [col_esc, "Quantidade"]
            
            fig_esc = px.bar(
                df_esc,
                x=col_esc,
                y="Quantidade",
                color=col_esc,
                color_discrete_sequence=px.colors.qualitative.Safe,
                labels={col_esc: "Escolaridade", "Quantidade": "Nº de Colaboradores"}
            )
            fig_esc.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_esc, use_container_width=True)
        else:
            st.info("Coluna de Escolaridade não encontrada na base.")

    st.markdown("---")

    # --- LINHA 2: TEMPO DE EMPRESA E GEOGRAFIA ---
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### ⏳ Tempo de Empresa (Distribuição)")
        col_tempo = "Tempo de empresa" if "Tempo de empresa" in df.columns else "Tempo de Empresa"
        
        if col_tempo in df.columns:
            # Se a coluna for numérica (ex: meses ou anos), o histograma funciona perfeitamente
            # Caso seja texto (ex: '1 a 3 anos'), troque 'px.histogram' por 'px.bar' igual aos de cima.
            fig_tempo = px.histogram(
                df,
                x=col_tempo,
                nbins=15,
                color_discrete_sequence=["#2bc0d3"],
                labels={col_tempo: "Tempo de Casa", "count": "Quantidade de Colaboradores"}
            )
            fig_tempo.update_layout(yaxis_title="Nº de Colaboradores", showlegend=False)
            st.plotly_chart(fig_tempo, use_container_width=True)
        else:
            st.info("Coluna de Tempo de Empresa não encontrada na base.")

    with col4:
        st.markdown("### 📍 Distribuição por Cidade e Mobilidade")
        col_cidade = "Cidade" if "Cidade" in df.columns else "Cidade"
        
        if col_cidade in df.columns:
            df_cid = df[col_cidade].value_counts().reset_index(name="Quantidade")
            df_cid.columns = [col_cidade, "Quantidade"]
            
            # Gráfico de barras para Cidades
            fig_cid = px.bar(
                df_cid.head(10), # Mostra as 10 principais cidades para não poluir
                x="Quantidade",
                y=col_cidade,
                orientation="h",
                color_discrete_sequence=["#636EFA"],
                labels={col_cidade: "Cidade", "Quantidade": "Nº de Colaboradores"}
            )
            fig_cid.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_cid, use_container_width=True)
            
            # Nota de rodapé sobre nacionalidade/origem
            col_nac = "Nacionalidade, origem e mobilidade geográfica"
            if col_nac in df.columns:
                nacionais = df[col_nac].dropna().unique()
                if len(nacionais) > 0:
                    st.caption(f"**Origens/Mobilidade presentes na base:** {', '.join(map(str, nacionais[:5]))}...")
        else:
            st.info("Coluna de Cidade não encontrada na base.")