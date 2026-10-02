"""
config.py
---------
Configuração global da aplicação Transformador Linear 2D.
Contém os dicionários de temas (escuro e claro) e constantes padrão do canvas.
"""

# Definições de temas para os modos Escuro e Claro.
# As cores são expressas como strings hexadecimais.
THEMES = {
    "dark": {
        "bg": "#181825",
        "panel": "#1e1e2e",
        "card": "#2b2b3b",
        "card_border": "#44475a",
        "text": "#cdd6f4",
        "subtext": "#a6adc8",
        "accent": "#89b4fa",
        "shape_fill": "#89b4fa",
        "shape_outline": "#74c7ec",
        "orig_shape": "#6c7086",
        "grid_orig": "#313244",
        "grid_trans": "#45475a",
        "axis": "#7f849c",
        "point_dot": "#f38ba8",
    },
    "light": {
        "bg": "#f8f9fa",
        "panel": "#ffffff",
        "card": "#ffffff",
        "card_border": "#e0e0e0",
        "text": "#212529",
        "subtext": "#6c757d",
        "accent": "#0d6efd",
        "shape_fill": "#0d6efd",
        "shape_outline": "#0a58ca",
        "orig_shape": "#6c757d",
        "grid_orig": "#dee2e6",
        "grid_trans": "#ced4da",
        "axis": "#495057",
        "point_dot": "#d63384",
    },
}

# Nome do tema ativo — pode ser alternado em tempo de execução.
CURRENT_THEME = "dark"


def get_theme(name: str | None = None) -> dict:
    """Retorna o dicionário de cores do tema solicitado.
    Se *name* for ``None``, retorna o tema atualmente ativo.
    """
    theme_name = CURRENT_THEME if name is None else name
    return THEMES[theme_name]


# Alias retrocompatível utilizado em todo o código.
# Será atualizado por ``apply_theme`` em tempo de execução.
THEME_COLORS = get_theme()

# Valores padrão do Canvas
DEFAULT_ZOOM = 45.0   # Pixels por unidade
DEFAULT_PAN_X = 0.0   # Deslocamento horizontal inicial
DEFAULT_PAN_Y = 0.0   # Deslocamento vertical inicial
