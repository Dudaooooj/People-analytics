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

MAPA_CORES_SITUACAO = {
    "ativo": "#28275a",       # Verde para ativo
    "férias": "#f1c40f",      # Amarelo para férias
    "ferias": "#f1c40f",
    "afastado": LARANJA_DESTAQUE, # Laranja destaque para afastados
    "desligado": "#d5741b"    # Vermelho para desligado
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
    if v in ("férias", "ferias", "férias/afastado"):
        return "ferias"
    if v in ("afastado", "afastamento"):
        return "afastado"
    return "outro"

def renderizar_painel_executivo(df):
    # --- ISOLAMENTO CRÍTICO ---
    df = df.copy()

    # Mapeando os nomes exatos encontrados no seu print
    adm_col_real = _choose_column(df, ["Admissao", "Admissão", "Data Admissão", "Data Admissao"])
    dem_col_real = _choose_column(df, ["Data demissão", "Data Demissão", "Data Desligamento", "Data demissao", "Data Demissao"])

    # --- TRATAMENTO SEGURO DE DATAS ---
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

    # ============================================================
    # INTERFACE GRÁFICA REESTRUTURADA E PERSONALIZADA COM CORES
    # ============================================================
    
    st.markdown("---")

    # 1. LINHA DE STATUS DO FUNCIONÁRIO (Com cores mapeadas)
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.metric(label="Total Histórico", value=f"{total_colaboradores} colab.")
    with col_t2:
        st.metric(label="🟢 Colaboradores Ativos", value=ativos)
    with col_t3:
        st.metric(label="🟡 Em Férias / Afastados", value=fora_operacao)
    with col_t4:
        st.metric(label="🔴 Total Desligados", value=desligados)
        
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

    # 3. SEÇÃO: DISTRIBUIÇÕES (LADO A LADO)
    st.subheader(" Distribuições")
    col_dist1, col_dist2 = st.columns(2)
    
    with col_dist1:
        if salario_col and 'salarios' in locals() and not salarios.dropna().empty:
            fig_sal = px.histogram(
                salarios.dropna(), 
                nbins=25, 
                labels={"value": "Salário (R$)", "count": "Frequência"}, 
                title="Distribuição Salarial", 
                template="plotly_white", 
                color_discrete_sequence=[AZUL_PRINCIPAL] # Aplicado Azul Principal
            )
            fig_sal.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO,
                height=350,
                showlegend=False,
                margin=dict(l=40, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_sal, width="stretch")
        else:
            st.info("Dados de salário insuficientes.")

    with col_dist2:
        if not tenure_series.empty:
            fig_tempo = px.histogram(
                tenure_series, 
                nbins=20, 
                labels={"value": "Tempo (Anos)", "count": "Frequência"}, 
                title="Distribuição de Tempo de Empresa", 
                template="plotly_white", 
                color_discrete_sequence=[LARANJA_DESTAQUE] # Aplicado Laranja Destaque
            )
            fig_tempo.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO,
                height=350,
                showlegend=False,
                margin=dict(l=40, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_tempo, width="stretch")
        else:
            st.info("Dados de tempo de empresa insuficientes.")

    st.markdown("---")

    # 4. SEÇÃO: ESTRUTURA ORGANIZACIONAL (Usa a paleta sequencial do projeto)
    # 4. SEÇÃO: ESTRUTURA ORGANIZACIONAL (Usa a paleta sequencial do projeto)
    st.subheader("Estrutura Organizacional")
    col_org1, col_org2 = st.columns(2)

    with col_org1:
        gestor_col = _choose_column(df, ["Gestor direto", "Gestor", "Gestor Direto", "Gestor imediato"])
        if gestor_col:
            df_gestores = df[gestor_col].astype(str).str.strip()
            df_gestores = df_gestores[(df_gestores != "") & (df_gestores.str.lower() != "nan")]
            df_gcount = df_gestores.value_counts().reset_index(name="Total")
            df_gcount.columns = ["Gestor", "Total"]
            df_gcount = df_gcount.head(8).sort_values(by="Total", ascending=True)
            
            # Aplicação da lógica de destaque da maior barra nos gestores
            max_gest = df_gcount["Total"].max()
            colors_gest = [LARANJA_DESTAQUE if t == max_gest else AZUL_PRINCIPAL for t in df_gcount["Total"]]
            
            fig_gest = px.bar(
                df_gcount, 
                x="Total", 
                y="Gestor", 
                orientation="h", 
                title="Top Gestores (Quantidade de Liderados)", 
                template="plotly_white"
            )
            fig_gest.update_traces(marker_color=colors_gest)
            fig_gest.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO, 
                height=380,
                margin=dict(l=180, r=20, t=40, b=40), 
                xaxis_title="Colaboradores",
                yaxis_title=None
            )
            st.plotly_chart(fig_gest, width="stretch")
        else:
            st.info("Coluna de gestor não identificada.")

    with col_org2:
        cargo_col = _choose_column(df, ["Cargo", "CARGO", "Função", "Funcao", "nome cargo", "Nome Cargo", "Nome cargo"]) 
        if cargo_col:
            # --- LIMPEZA E PADRONIZAÇÃO AVANÇADA DE TEXTO ---
            df_cargo = df[cargo_col].astype(str).str.strip().str.upper()
            
            # Remove acentuações comuns para unificar (MANUTENÇÃO -> MANUTENCAO)
            df_cargo = df_cargo.str.replace("ÇÃO", "CAO", regex=True)
            df_cargo = df_cargo.str.replace("Ã", "A", regex=True)
            
            # CORREÇÃO CRÍTICA AQUI: Adicionado o .str antes do .lower()
            df_cargo = df_cargo[(df_cargo != "") & (df_cargo.str.lower() != "nan")]
            
            df_cc = df_cargo.value_counts().reset_index(name="Quantidade")
            df_cc.columns = ["Cargo", "Quantidade"]
            df_cc = df_cc.head(8).sort_values(by="Quantidade", ascending=True)
            
            # --- LÓGICA DE DESTAQUE DINÂMICO (MAIOR BARRA EM LARANJA) ---
            max_cargo = df_cc["Quantidade"].max()
            colors_cargo = [LARANJA_DESTAQUE if q == max_cargo else AZUL_PRINCIPAL for q in df_cc["Quantidade"]]
            
            fig_cargo = px.bar(
                df_cc, 
                x="Quantidade", 
                y="Cargo", 
                orientation="h", 
                title="Principais Cargos", 
                template="plotly_white"
            )
            fig_cargo.update_traces(marker_color=colors_cargo)
            fig_cargo.update_layout(
                paper_bgcolor=BRANCO, 
                plot_bgcolor=BRANCO, 
                height=380,
                margin=dict(l=180, r=20, t=40, b=40), 
                xaxis_title="Quantidade",
                yaxis_title=None
            )
            st.plotly_chart(fig_cargo, width="stretch")
        else:
            st.info("Coluna de cargo não identificada.")
    st.markdown("---")

    # 5. SEÇÃO: MOVIMENTAÇÃO AO LONGO DO TEMPO (Mapeamento explícito de Admissões/Demissões)
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
    
    if not admissoes_no_tempo.empty or not demissoes_no_tempo.empty:
        movimentacao = pd.merge(admissoes_no_tempo, demissoes_no_tempo, on="Mes_Ano", how="outer").fillna(0)
        movimentacao = movimentacao.sort_values("Mes_Ano")
        
        fig = px.line(
            movimentacao, 
            x="Mes_Ano", 
            y=["Admissões", "Demissões"],
            labels={"value": "Quantidade", "Mes_Ano": "Período (Mês/Ano)", "variable": "Movimentação"},
            color_discrete_map={
                "Admissões": MAPA_CORES_SITUACAO["ativo"],      
                "Demissões": MAPA_CORES_SITUACAO["desligado"]   
            },
            markers=True,
            title="Linha Admissão x Demissão"
        )
        fig.update_layout(
            hovermode="x unified", 
            legend_orientation="h", 
            legend_y=1.1, 
            paper_bgcolor=BRANCO, 
            plot_bgcolor=BRANCO,
            height=400
        )
        fig.update_traces(marker=dict(line=dict(width=0)))
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Sem dados históricos de datas suficientes para gerar a linha temporal.")