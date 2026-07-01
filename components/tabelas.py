import streamlit as st
import pandas as pd

def renderizar_exploracao_dados(df: pd.DataFrame):
	st.markdown("### Explorar e Exportar Dados")

	if df is None or df.empty:
		st.warning("Nenhum dado disponível para os filtros selecionados.")
		return

	# Permitir seleção de colunas para visualização
	colunas = df.columns.tolist()
	col_selecionadas = st.multiselect("Colunas a exibir", options=colunas, default=colunas)

	# Filtros rápidos adicionais na área principal (além do filtro global na sidebar)
	with st.expander("Filtros rápidos (opcional)"):
		# Status
		if "Situação" in df.columns:
			status_sel = st.multiselect("Situação", options=sorted(df["Situação"].dropna().unique()), default=sorted(df["Situação"].dropna().unique()))
			df = df[df["Situação"].isin(status_sel)]

		# Setor
		if "Setor" in df.columns:
			setor_sel = st.multiselect("Setor", options=sorted(df["Setor"].dropna().unique()), default=sorted(df["Setor"].dropna().unique()))
			df = df[df["Setor"].isin(setor_sel)]

		# Cargo
		if "Cargo" in df.columns:
			cargo_sel = st.multiselect("Cargo", options=sorted(df["Cargo"].dropna().unique()), default=sorted(df["Cargo"].dropna().unique()))
			df = df[df["Cargo"].isin(cargo_sel)]

	# Exibir tabela com as colunas selecionadas
	st.dataframe(df[col_selecionadas], width="stretch")

	# Botão para download csv
	csv = df[col_selecionadas].to_csv(index=False).encode("utf-8")
	st.download_button(label="📥 Baixar CSV", data=csv, file_name="exploracao_dados.csv", mime="text/csv")
