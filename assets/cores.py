# Cores Principais do Projeto
AZUL_PRINCIPAL = "#28275a"
LARANJA_DESTAQUE = "#d5741b"
PALETA_SALARIO = [
    "#28275a",  # AZUL_PRINCIPAL original
    "#3a3973",
    "#4e4c8d",
    "#6361a8",
    "#7977c3",
    "#918fde",
    "#aaa9f9"
]
PALETA_TEMPO = [
    "#d5741b",  # LARANJA_DESTAQUE original
    "#e28633",
    "#ee984b",
    "#faa964",
    "#ffbb7d",
    "#ffcc97",
    "#ffdeb1"
]

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


def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb_tuple):
    return "#{:02x}{:02x}{:02x}".format(*[int(round(c)) for c in rgb_tuple])


def generate_palette(color_start: str, color_end: str, n: int):
    """Gera uma paleta com n cores interpolando linearmente entre duas cores hex.

    Retorna lista de hex strings ordenada do `color_start` ao `color_end`.
    """
    if n <= 0:
        return []
    if n == 1:
        return [color_start]

    r1, g1, b1 = _hex_to_rgb(color_start)
    r2, g2, b2 = _hex_to_rgb(color_end)
    palette = []
    for i in range(n):
        t = i / (n - 1)
        r = r1 + (r2 - r1) * t
        g = g1 + (g2 - g1) * t
        b = b1 + (b2 - b1) * t
        palette.append(_rgb_to_hex((r, g, b)))
    return palette