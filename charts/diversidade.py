import streamlit as st
import plotly.express as px
import pandas as pd

def renderizar_analise_diversidade(df):
    if df.empty:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
        return

    # --- LINHA 1: METRICA PCD E GRÁFICO DE GÊNERO ---
    col1, col2 = st.columns([1, 2]) # col2 ligeiramente maior para o gráfico de rosca

    with col1:
        st.markdown("### ♿ Inclusão PCD")
        col_pcd = "Pessoas com deficiência" if "Pessoas com deficiência" in df.columns else "PCD"
        
        if col_pcd in df.columns:
            # Tratamento para identificar quem é PCD (removendo nulos e normalizando texto)
            # Geralmente a coluna vem com "Sim"/"Não", o nome da deficiência, ou "Não informado"
            df_pcd_filtrado = df[col_pcd].astype(str).str.lower().str.strip()
            
            # Conta todos que não são "não", "não se aplica" ou "nan"
            total_pcd = len(df[~df_pcd_filtrado.isin(["não", "nao", "não se aplica", "nan", ""])])
            total_geral = len(df)
            percentual_pcd = (total_pcd / total_geral) * 100 if total_geral > 0 else 0
            
            # Card estilizado usando o container nativo
            with st.container(border=True):
                st.metric(
                    label="Colaboradores PCD", 
                    value=f"{total_pcd}", 
                    delta=f"{percentual_pcd:.1f}% do quadro geral",
                    delta_color="normal"
                )
                st.caption("Meta legal (Lei de Cotas) varia de 2% a 5% dependendo do headcount por CNPJ.")
        else:
            st.info("Coluna de PCD não encontrada na base.")

    with col2:
        st.markdown("### ⚧️ Identidade de Gênero")
        col_genero = "Gênero" if "Gênero" in df.columns else "Genero"
        
        if col_genero in df.columns:
            df_gen = df[col_genero].value_counts().reset_index(name="Quantidade")
            df_gen.columns = [col_genero, "Quantidade"]
            
            # Gráfico de Rosca (Pie com 'hole')
            fig_gen = px.pie(
                df_gen,
                names=col_genero,
                values="Quantidade",
                hole=0.5, # Cria o efeito de rosca
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            # Melhora o posicionamento do texto e rótulos
            fig_gen.update_traces(textinfo="percent+label", pull=[0.05] * len(df_gen))
            fig_gen.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_gen, use_container_width=True)
        else:
            st.info("Coluna de Gênero não encontrada na base.")

    st.markdown("---")

    # --- LINHA 2: RAÇA/ETNIA E ESTADO CIVIL ---
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### ✊🏽 Raça e Etnia")
        col_raca = "Raça e etnia" if "Raça e etnia" in df.columns else "Raça"
        
        if col_raca in df.columns:
            df_raca = df[col_raca].value_counts().reset_index(name="Quantidade")
            df_raca.columns = [col_raca, "Quantidade"]
            
            fig_raca = px.bar(
                df_raca,
                x="Quantidade",
                y=col_raca,
                orientation="h",
                color=col_raca,
                color_discrete_sequence=px.colors.qualitative.Muted,
                labels={col_raca: "Raça / Etnia", "Quantidade": "Nº de Colaboradores"}
            )
            fig_raca.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig_raca, use_container_width=True)
        else:
            st.info("Coluna de Raça/Etnia não encontrada na base.")

    with col4:
        st.markdown("### 💍 Estado Civil e Composição Familiar")
        col_civil = "Estado civil e composição familiar" if "Estado civil e composição familiar" in df.columns else "Estado Civil"
        
        if col_civil in df.columns:
            df_civil = df[col_civil].value_counts().reset_index(name="Quantidade")
            df_civil.columns = [col_civil, "Quantidade"]
            
            fig_civil = px.bar(
                df_civil,
                x=col_civil,
                y="Quantidade",
                color_discrete_sequence=["#ab63fa"],
                labels={col_civil: "Estado Civil / Família", "Quantidade": "Nº de Colaboradores"}
            )
            fig_civil.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_civil, use_container_width=True)
        else:
            st.info("Coluna de Estado Civil não encontrada na base.")