# Cores Principais do Projeto
AZUL_PRINCIPAL = "#28275a"
LARANJA_DESTAQUE = "#d5741b"

# Cores Neutras de Suporte (para fundos, textos e bordas)
BRANCO = "#ffffff"
CINZA_CLARO = "#f8f9fa"
CINZA_TEXTO = "#495057"

# Paletas Sequenciais e Qualitativas para os gráficos do Plotly
PALETA_PRINCIPAL = [AZUL_PRINCIPAL, LARANJA_DESTAQUE, "#4e54c8", "#ff9233", "#7f7fd5"]

# Dicionários de mapeamento explícito (ex: para a situação do colaborador)
MAPA_CORES_SITUACAO = {
    "ativo": "#2ecc71",       # Verde para ativo
    "férias": "#f1c40f",      # Amarelo para férias
    "ferias": "#f1c40f",
    "afastado": LARANJA_DESTAQUE, # Laranja destaque para afastados
    "desligado": "#e74c3c"    # Vermelho para desligado
}