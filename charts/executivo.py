import streamlit as st
import pandas as pd
import plotly.express as px
from pandas.tseries.offsets import MonthEnd

from assets.cores import AZUL_PRINCIPAL, LARANJA_DESTAQUE, BRANCO, generate_palette

MAPA_CORES_SITUACAO = {
    "ativo": AZUL_PRINCIPAL,
    "férias": "#f1c40f",
    "ferias": "#f1c40f",
    "afastado": LARANJA_DESTAQUE,
    "desligado": LARANJA_DESTAQUE
}

def _choose_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _normalize_status(val: str) -> str:
    if not isinstance(val, str):
        return "outro"
    v = val.strip().lower()
    if v in ("ativo", "trabalhando", "trabalhando(a)"):
        return "ativo"
    if v in ("demitido", "desligado", "demissão", "demissao", "demitida", "demitidos"):
        return "desligado"
    
    if v in ("férias", "ferias", "férias/afastado", "acid. trabalho período superior a 15 dias", "novo afast. mesma doença"):
        return "ferias"
        
    if v in ("afastado", "afastamento"):
        return "afastado"
    return "outro"

def renderizar_painel_executivo(df):
    df = df.copy()

    adm_col_real = _choose_column(df, ["Admissao", "Admissão", "Data Admissão", "Data Admissao"])
    dem_col_real = _choose_column(df, ["Data demissão", "Data Demissão", "Data Desligamento", "Data demissao", "Data Demissao"])

    if adm_col_real:
        df[adm_col_real] = pd.to_datetime(df[adm_col_real], dayfirst=True, errors="coerce")
    if dem_col_real:
        df[dem_col_real] = pd.to_datetime(df[dem_col_real], dayfirst=True, errors="coerce")
    
    # --- CÁLCULO DOS KPIS DE STATUS ---
    total_colaboradores = len(df)

    situacao_col = _choose_column(df, ["Situação", "Situacao", "Status", "Situacao "])
    situacao_series = pd.Series([None] * len(df))
    if situacao_col:
        situacao_series = df[situacao_col].astype(str).fillna("").apply(_normalize_status)

    ativos = int((situacao_series == "ativo").sum()) if situacao_col else 0
    fora_operacao = int(situacao_series.isin(["ferias", "afastado"]).sum()) if situacao_col else 0
    desligados = int(situacao_series.isin(["desligado"]).sum()) if situacao_col else 0

    # --- CÁLCULO DOS INDICADORES (MÉDIA, MEDIANA, TEMPO MÉDIO) ---
    salario_col = _choose_column(df, ["Salário", "Salario", "Remuneração", "Remuneracao", "Salario Base"])
    media_salarial_val = "—"
    mediana_salarial_val = "—"
    
    if salario_col:
        salarios = pd.to_numeric(df[salario_col], errors="coerce")
        media_salarial = salarios.mean()
        mediana_salarial = salarios.median()
        if pd.notna(media_salarial):
            media_salarial_val = f"R$ {media_salarial:,.2f}"
        if pd.notna(mediana_salarial):
            mediana_salarial_val = f"R$ {mediana_salarial:,.2f}"

    tempo_medio_val = "—"
    tenure_series = pd.Series(dtype=float)
    if adm_col_real:
        hoje = pd.to_datetime("today")
        adm_dates = df[adm_col_real]
        dem_dates = df[dem_col_real] if dem_col_real else pd.Series(pd.NaT, index=df.index)
        tenure_days = (dem_dates.fillna(hoje) - adm_dates).dt.days
        tenure_years = tenure_days / 365.25
        tenure_series = tenure_years.dropna()
        if not tenure_series.empty:
            tempo_medio_val = f"{tenure_series.mean():.2f} anos"

    
    # INTERFACE GRÁFICA REESTRUTURADA E PERSONALIZADA COM CORES

    
    st.markdown("---")

    # --- CÁLCULO DE PORCENTAGENS DOS KPIS ---
    pct_ativos = (ativos / total_colaboradores * 100) if total_colaboradores > 0 else 0
    pct_fora = (fora_operacao / total_colaboradores * 100) if total_colaboradores > 0 else 0
    pct_desligados = (desligados / total_colaboradores * 100) if total_colaboradores > 0 else 0

    # 1. LINHA DE STATUS DO FUNCIONÁRIO (Com cores mapeadas e deltas percentuais)
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.metric(
            label="Total Histórico", 
            value=f"{total_colaboradores} colab."
        )
    with col_t2:
        st.metric(
            label="🟢 Colaboradores Ativos", 
            value=ativos,
            delta=f"{pct_ativos:.1f}% da base",
            delta_color="off" 
        )
    with col_t3:
        st.metric(
            label="🟡 Em Férias / Afastados", 
            value=fora_operacao,
            delta=f"{pct_fora:.1f}% da base",
            delta_color="off"
        )
    with col_t4:
        st.metric(
            label="🔴 Total Desligados", 
            value=desligados,
            delta=f"{pct_desligados:.1f}% da base",
            delta_color="off"
        )
        
    st.markdown("---")

    # 2. SEÇÃO: INDICADORES EXECUTIVOS
    st.subheader(" Indicadores")
    col_ind1, col_ind2, col_ind3 = st.columns(3)
    with col_ind1:
        st.metric(label="Média Salarial", value=media_salarial_val)
    with col_ind2:
        st.metric(label="Mediana Salarial", value=mediana_salarial_val)
    with col_ind3:
        st.metric(label="Tempo Médio de Empresa", value=tempo_medio_val)

    st.markdown("---")

  # 3. SEÇÃO: DISTRIBUIÇÕES (FILTRADO APENAS ATIVOS / TRABALHANDO)
    # 3. SEÇÃO: DISTRIBUIÇÕES (FILTRADO APENAS ATIVOS / TRABALHANDO)
    st.subheader("Distribuições")
    col_dist1, col_dist2 = st.columns(2)
    
    if situacao_col:
        df_ativos_dist = df[situacao_series.isin(["ativo", "ferias", "afastado"])].copy()
    else:
        df_ativos_dist = df.copy()

    import numpy as np

    with col_dist1:
        if salario_col and 'salarios' in locals():
            salarios_ativos = pd.to_numeric(df_ativos_dist[salario_col], errors="coerce").dropna()
            
            if not salarios_ativos.empty:
                # --- FAIXAS LIMPAS: De 500 em 500 reais ---
                min_sal = int(np.floor(salarios_ativos.min() / 500) * 500)
                max_sal = int(np.ceil(salarios_ativos.max() / 500) * 500)
                bins_custom_sal = list(range(min_sal, max_sal + 501, 500))
                
                bins_sal = pd.cut(salarios_ativos, bins=bins_custom_sal, right=False)
                df_sal_bar = bins_sal.value_counts().sort_index().reset_index()
                df_sal_bar.columns = ["Intervalo", "Frequência"]
                
                # Formatação limpa e direta
                df_sal_bar["Intervalo_Str"] = df_sal_bar["Intervalo"].apply(lambda x: f"R$ {int(x.left)}-{int(x.right)}")
                
                cores_sal = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_sal_bar))

                fig_sal = px.bar(
                    df_sal_bar, 
                    x="Intervalo_Str", 
                    y="Frequência",
                    labels={"Intervalo_Str": "Faixa Salarial", "Frequência": "Frequência"}, 
                    title="Distribuição Salarial (Apenas Ativos)", 
                    template="plotly_white", 
                    color="Intervalo_Str",
                    color_discrete_sequence=cores_sal,
                    text_auto=True
                )
                fig_sal.update_traces(textposition="outside", cliponaxis=False)
                fig_sal.update_layout(
                    paper_bgcolor=BRANCO, plot_bgcolor=BRANCO, height=380,
                    showlegend=False, margin=dict(l=40, r=20, t=80, b=60), title_pad=dict(b=20),
                    # AJUSTE: Redução da fonte (size=10) e mantido reto (tickangle=0)
                    xaxis={
                        "type": "category", 
                        "tickangle": 0, 
                        "tickfont": {"size": 10}
                    } 
                )
                st.plotly_chart(fig_sal, width="stretch")
            else:
                st.info("Dados de salário de colaboradores ativos insuficientes.")
        else:
            st.info("Dados de salário insuficientes.")

    with col_dist2:
        if adm_col_real:
            hoje = pd.to_datetime("today")
            adm_dates_at = df_ativos_dist[adm_col_real]
            dem_dates_at = df_ativos_dist[dem_col_real] if dem_col_real else pd.Series(pd.NaT, index=df_ativos_dist.index)
            
            tenure_days_at = (dem_dates_at.fillna(hoje) - adm_dates_at).dt.days
            tenure_years_at = (tenure_days_at / 365.25).dropna()
            
            if not tenure_years_at.empty:
                # --- FAIXAS LIMPAS: De 1 em 1 ano ---
                max_ano = int(np.ceil(tenure_years_at.max()))
                bins_custom_tempo = list(range(0, max_ano + 2, 1))
                
                bins_tempo = pd.cut(tenure_years_at, bins=bins_custom_tempo, right=False)
                df_tempo_bar = bins_tempo.value_counts().sort_index().reset_index()
                df_tempo_bar.columns = ["Intervalo", "Frequência"]
                
                df_tempo_bar["Intervalo_Str"] = df_tempo_bar["Intervalo"].apply(
                    lambda x: f"{int(x.left)}-{int(x.right)} Ano" if int(x.left) <= 1 else f"{int(x.left)}-{int(x.right)} Anos"
                )
                
                cores_tempo = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_tempo_bar))

                fig_tempo = px.bar(
                    df_tempo_bar, 
                    x="Intervalo_Str", 
                    y="Frequência",
                    labels={"Intervalo_Str": "Tempo de Casa", "Frequência": "Frequência"}, 
                    title="Distribuição de Tempo de Empresa (Apenas Ativos)", 
                    template="plotly_white", 
                    color="Intervalo_Str",
                    color_discrete_sequence=cores_tempo,
                    text_auto=True
                )
                fig_tempo.update_traces(textposition="outside", cliponaxis=False)
                fig_tempo.update_layout(
                    paper_bgcolor=BRANCO, plot_bgcolor=BRANCO, height=380,
                    showlegend=False, margin=dict(l=40, r=20, t=80, b=60), title_pad=dict(b=20),
                    # AJUSTE: Redução da fonte (size=10) e mantido reto (tickangle=0)
                    xaxis={
                        "type": "category", 
                        "tickangle": 0, 
                        "tickfont": {"size": 10}
                    }
                )
                st.plotly_chart(fig_tempo, width="stretch")
            else:
                st.info("Dados de tempo de empresa de colaboradores ativos insuficientes.")
        else:
            st.info("Dados de tempo de empresa insuficientes.")
    st.markdown("---")
    # # 4. SEÇÃO: ESTRUTURA ORGANIZACIONAL (Usa a paleta sequencial do projeto)
    st.subheader("Estrutura Organizacional")
    
    # --- IDENTIFICAÇÃO DO CARGO ---
    cargo_col = _choose_column(df, ["Cargo", "CARGO", "Função", "Funcao", "nome cargo", "Nome Cargo", "Nome cargo"]) 

    # --- GRÁFICO DE CARGOS EM LARGURA TOTAL ---
    if cargo_col:
        # --- LIMPEZA E PADRONIZAÇÃO AVANÇADA DE TEXTO ---
        df_cargo = df[cargo_col].astype(str).str.strip().str.upper()
        
        # Remove acentuações comuns para unificar (MANUTENÇÃO -> MANUTENCAO)
        df_cargo = df_cargo.str.replace("ÇÃO", "CAO", regex=True)
        df_cargo = df_cargo.str.replace("Ã", "A", regex=True)
        
        df_cargo = df_cargo[(df_cargo != "") & (df_cargo.str.lower() != "nan")]
        
        df_cc = df_cargo.value_counts().reset_index(name="Quantidade")
        df_cc.columns = ["Cargo", "Quantidade"]
        
        # Pega o top 8 e ordena do menor para o maior volume
        df_cc = df_cc.head(8).sort_values(by="Quantidade", ascending=True)
        
        # Gera uma paleta que transita do azul ao laranja para os cargos
        cores_degrade = generate_palette(AZUL_PRINCIPAL, LARANJA_DESTAQUE, len(df_cc))
        cores_degrade.reverse()
        
        fig_cargo = px.bar(
            df_cc, 
            x="Quantidade", 
            y="Cargo", 
            orientation="h", 
            title="Principais Cargos na Organização", 
            template="plotly_white",
            text="Quantidade" 
        )
        fig_cargo.update_traces(
            marker_color=cores_degrade, 
            textposition="outside", 
            cliponaxis=False        
        )
        fig_cargo.update_layout(
            paper_bgcolor=BRANCO, 
            plot_bgcolor=BRANCO, 
            height=380,
            margin=dict(l=180, r=50, t=60, b=40), 
            title_pad=dict(b=15),                
            xaxis_title="Quantidade de Colaboradores",
            yaxis_title=None
        )
        st.plotly_chart(fig_cargo, width="stretch")
    else:
        st.info("Coluna de cargo não identificada.")
        
    st.markdown("---")
    # 5. SEÇÃO: MOVIMENTAÇÃO AO LONGO DO TEMPO (Com cálculo dinâmico de Turnover Geral)
    col_status_atual = "Status" if "Status" in df.columns else ("Situação" if "Situação" in df.columns else None)
    status_presentes = df[col_status_atual].unique() if col_status_atual else []

    if any(s in status_presentes for s in ["Trabalhando", "Desligado"]):
        st.subheader("Movimentação ao Longo do Tempo")
        
        admissoes_no_tempo = pd.DataFrame(columns=["Mes_Ano", "Admissões"])
        demissoes_no_tempo = pd.DataFrame(columns=["Mes_Ano", "Demissões"])

        if adm_col_real and not df[df[adm_col_real].notna()].empty:
            df_adm = df[df[adm_col_real].notna()].copy()
            df_adm["Mes_Ano"] = df_adm[adm_col_real].dt.strftime("%Y-%m")
            admissoes_no_tempo = df_adm.groupby("Mes_Ano").size().reset_index(name="Admissões")
        
        if dem_col_real and not df[df[dem_col_real].notna()].empty:
            df_dem = df[df[dem_col_real].notna()].copy()
            df_dem["Mes_Ano"] = df_dem[dem_col_real].dt.strftime("%Y-%m")
            demissoes_no_tempo = df_dem.groupby("Mes_Ano").size().reset_index(name="Demissões")
        
        if (not admissoes_no_tempo.empty or not demissoes_no_tempo.empty):
            # 1. Consolidamos o histórico total primeiro
            movimentacao = pd.merge(admissoes_no_tempo, demissoes_no_tempo, on="Mes_Ano", how="outer").fillna(0)
            movimentacao = movimentacao.sort_values("Mes_Ano")
            
            # 2. Calculamos os ativos varrendo o histórico completo para garantir a herança de ativos de anos passados
            movimentacao["Ativos_No_Mes"] = 0
            for i, row in movimentacao.iterrows():
                ultimo_dia = pd.to_datetime(row["Mes_Ano"]) + MonthEnd(1)
                # Garantimos que a varredura olhe para o mesmo DataFrame filtrado (df) de forma segura
                ativos = (
                    (df[adm_col_real] <= ultimo_dia) &
                    (df[dem_col_real].isna() | (df[dem_col_real] > ultimo_dia))
                ).sum()
                movimentacao.loc[i, "Ativos_No_Mes"] = ativos
            
            # 3. Calculamos o Turnover histórico
            movimentacao["Turnover (%)"] = movimentacao.apply(
                lambda r: (((r["Admissões"] + r["Demissões"]) / 2) / r["Ativos_No_Mes"] * 100) if r["Ativos_No_Mes"] > 0 else 0, 
                axis=1
            )
            
            # --- FILTRO VISUAL AQUI: Cortamos para exibir na tela apenas de Janeiro/2026 em diante ---
            movimentacao = movimentacao[movimentacao["Mes_Ano"] >= "2026-01"].reset_index(drop=True)

            if not movimentacao.empty:
                # Criando rótulos amigáveis para o eixo X (Ex: "jan/26")
                meses_map = {"01": "jan", "02": "fev", "03": "mar", "04": "abr", "05": "mai", "06": "jun",
                             "07": "jul", "08": "ago", "09": "set", "10": "out", "11": "nov", "12": "dez"}
                
                def formatar_mes_ano(txt):
                    ano, mes = txt.split("-")
                    return f"{meses_map[mes]}/{ano[2:]}"
                    
                movimentacao["Periodo_Exibicao"] = movimentacao["Mes_Ano"].apply(formatar_mes_ano)

                # --- CONSTRUÇÃO DO GRÁFICO MISTO CUSTOMIZADO (Plotly Graph Objects) ---
                import plotly.graph_objects as go
                fig = go.Figure()

                # 1. Barras de Admitidos (Azul Escuro Principal)
                fig.add_trace(
                    go.Bar(
                        x=movimentacao["Periodo_Exibicao"],
                        y=movimentacao["Admissões"],
                        name="Admitidos",
                        marker_color=AZUL_PRINCIPAL,
                        text=movimentacao["Admissões"],
                        textposition="outside"
                    )
                )

                # 2. Barras de Demitidos (Laranja Destaque)
                fig.add_trace(
                    go.Bar(
                        x=movimentacao["Periodo_Exibicao"],
                        y=movimentacao["Demissões"],
                        name="Demitidos",
                        marker_color=LARANJA_DESTAQUE,  
                        text=movimentacao["Demissões"],
                        textposition="outside"
                    )
                )

                # 3. Linha do Turnover Geral (Roxo)
                fig.add_trace(
                    go.Scatter(
                        x=movimentacao["Periodo_Exibicao"],
                        y=movimentacao["Turnover (%)"],
                        name="Turnover Geral (%)",
                        mode="lines+markers+text",
                        line=dict(color="#5a3a5f", width=3), 
                        marker=dict(size=6),
                        text=movimentacao["Turnover (%)"].apply(lambda x: f"{x:.1f}%" if x > 0 else ""),
                        textposition="top center",
                        yaxis="y2" 
                    )
                )

                # 4. Linha da Meta Fixa (Azul Claro / Ciano)
                meta_valor = 10.0
                fig.add_trace(
                    go.Scatter(
                        x=movimentacao["Periodo_Exibicao"],
                        y=[meta_valor] * len(movimentacao),
                        name="Meta",
                        mode="lines",
                        line=dict(color="#4ebec8", width=2, dash="solid"),
                        yaxis="y2"
                    )
                )

                # --- CONFIGURAÇÃO VISUAL COMPLETA DOS DOIS EIXOS (CORRIGIDA) ---
                fig.update_layout(
                    barmode="group", 
                    hovermode="x unified", 
                    legend=dict(orientation="h", y=1.15, x=0.2),
                    paper_bgcolor=BRANCO, 
                    plot_bgcolor=BRANCO,
                    height=480,
                    title="Movimentações Mensais: Admitidos vs Demitidos vs Turnover Geral",
                    yaxis=dict(
                        title=dict(text="Quantidade de Colaboradores", font=dict(color=AZUL_PRINCIPAL)),
                        tickfont=dict(color=AZUL_PRINCIPAL),
                        gridcolor="#f0f0f0"
                    ),
                    yaxis2=dict(
                        title=dict(text="Taxa de Turnover / Meta", font=dict(color="#5a3a5f")),
                        tickfont=dict(color="#5a3a5f"),
                        anchor="x",
                        overlaying="y",
                        side="right",
                        ticksuffix="%",
                        range=[0, max(movimentacao["Turnover (%)"].max() + 5, 15)]
                    )
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.warning("Sem dados históricos para exibir a partir do filtro selecionado.")
        else:
            st.warning("Sem dados históricos de datas suficientes a partir de 2026 para gerar a linha temporal.")
    else:
        st.info("O gráfico de movimentações histórica e Turnover é exibido apenas para filtros que incluam funcionários ativos 'Trabalhando' ou 'Desligados'.")