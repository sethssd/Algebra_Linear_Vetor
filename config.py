"""
config.py
---------
Configurações globais de estilo, tema e constantes da aplicação.
"""

# Cores Padrão (Tema Dark Elegante)
THEME_COLORS = {
    "bg": "#181825",
    "panel": "#1e1e2e",
    "card": "#2b2b3b",
    "card_border": "#44475a",
    "text": "#cdd6f4",
    "subtext": "#a6adc8",
    "accent": "#89b4fa",        # Azul destaque
    "shape_fill": "#89b4fa",    # Cor da figura transformada
    "shape_outline": "#74c7ec",
    "orig_shape": "#6c7086",     # Figura original
    "grid_orig": "#313244",     # Grade cartesiana original
    "grid_trans": "#45475a",    # Grade transformada
    "axis": "#7f849c",          # Eixos X e Y
    "point_dot": "#f38ba8"       # Cor dos pontos
}

# Configurações do Canvas
DEFAULT_ZOOM = 45.0             # Pixels por unidade
DEFAULT_PAN_X = 0.0
DEFAULT_PAN_Y = 0.0
