"""
ui/theme.py
-----------
Tema visual minimalista para o Transformador Linear 2D.
Fornece estilos ttk refinados, widgets customizados (botões circulares,
cards com sombra, seções com ícones SVG desenhados em canvas).
"""

import tkinter as tk
from tkinter import ttk
from config import get_theme


# ---------------------------------------------------------------------------#
#  Paleta refinada
# ---------------------------------------------------------------------------#

PALETTE = {
    "bg":          "#0f0f17",   # Fundo principal — quase preto
    "panel":       "#16161f",   # Painéis laterais
    "card":        "#1e1e2c",   # Cards / seções
    "card_alt":    "#252535",   # Card alternativo (hover, destaque)
    "border":      "#2e2e42",   # Bordas sutis
    "border_glow": "#7c6af7",   # Borda de destaque (accent)
    "text":        "#e4e4f0",   # Texto principal
    "subtext":     "#7878a0",   # Texto secundário
    "accent":      "#7c6af7",   # Roxo accent
    "accent2":     "#56b0f5",   # Azul claro
    "success":     "#4ecb91",   # Verde
    "warn":        "#f5a742",   # Laranja
    "danger":      "#f56b6b",   # Vermelho
    "shadow":      "#0a0a12",   # Cor de sombra
}


def apply_global_styles(root: tk.Tk) -> None:
    """Aplica os estilos ttk globais na janela principal."""
    T = PALETTE
    style = ttk.Style(root)
    style.theme_use("default")

    # -- Base --
    style.configure(
        ".",
        background=T["panel"],
        foreground=T["text"],
        font=("Segoe UI", 10),
        relief="flat",
        borderwidth=0,
    )

    # -- Frame --
    style.configure("TFrame", background=T["panel"])
    style.configure("Card.TFrame", background=T["card"])
    style.configure("CardAlt.TFrame", background=T["card_alt"])

    # -- Label --
    style.configure("TLabel", background=T["panel"], foreground=T["text"])
    style.configure("Card.TLabel", background=T["card"], foreground=T["text"])
    style.configure("Sub.TLabel", background=T["card"], foreground=T["subtext"], font=("Segoe UI", 9))
    style.configure("Title.TLabel", background=T["panel"], foreground=T["text"], font=("Segoe UI", 11, "bold"))
    style.configure("Accent.TLabel", background=T["card"], foreground=T["accent"], font=("Segoe UI", 9, "bold"))

    # -- Separator --
    style.configure("TSeparator", background=T["border"])

    # -- Checkbutton / Radiobutton --
    style.configure("TCheckbutton", background=T["card"], foreground=T["text"])
    style.map("TCheckbutton", background=[("active", T["card"])])
    style.configure("TRadiobutton", background=T["card"], foreground=T["text"])
    style.map("TRadiobutton", background=[("active", T["card"])])

    # -- Scale (slider) --
    style.configure(
        "TScale",
        background=T["card"],
        troughcolor=T["border"],
        sliderrelief="flat",
    )

    # -- Scrollbar --
    style.configure(
        "Vertical.TScrollbar",
        troughcolor=T["panel"],
        background=T["border"],
        bordercolor=T["panel"],
        arrowcolor=T["subtext"],
        relief="flat",
        arrowsize=12,
    )
    style.map("Vertical.TScrollbar", background=[("active", T["accent"])])

    # -- Entry --
    style.configure(
        "TEntry",
        fieldbackground=T["card_alt"],
        foreground=T["text"],
        insertcolor=T["accent"],
        bordercolor=T["border"],
        lightcolor=T["border"],
        darkcolor=T["border"],
    )

    # -- Combobox --
    style.configure(
        "TCombobox",
        fieldbackground=T["card_alt"],
        background=T["card"],
        foreground=T["text"],
        arrowcolor=T["accent"],
        bordercolor=T["border"],
        selectbackground=T["accent"],
        selectforeground=T["text"],
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", T["card_alt"])],
        foreground=[("readonly", T["text"])],
    )

    # -- LabelFrame (seções) --
    style.configure(
        "TLabelframe",
        background=T["card"],
        bordercolor=T["border"],
        relief="flat",
        labeloutside=False,
    )
    style.configure(
        "TLabelframe.Label",
        background=T["card"],
        foreground=T["accent"],
        font=("Segoe UI", 9, "bold"),
        padding=(4, 2),
    )


# ---------------------------------------------------------------------------#
#  Ícones SVG desenhados em Canvas
# ---------------------------------------------------------------------------#

def _svg_icon(parent, size: int, draw_fn, bg: str) -> tk.Canvas:
    """Cria um mini canvas com um ícone desenhado pela função draw_fn."""
    c = tk.Canvas(parent, width=size, height=size, bg=bg,
                  highlightthickness=0, bd=0)
    draw_fn(c, size)
    return c


def icon_rotate(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de rotação — seta circular."""
    def draw(c, s):
        m = s // 2
        r = s * 0.35
        import math
        pts = []
        for i in range(300):
            a = math.radians(i * 1.2)
            pts.extend([m + r * math.cos(a), m - r * math.sin(a)])
        c.create_line(*pts, fill=PALETTE["accent"], width=2, smooth=True)
        # Arrowhead
        c.create_polygon(m + r, m - 2, m + r + 5, m + 4, m + r - 4, m + 4,
                         fill=PALETTE["accent"], outline="")
    return _svg_icon(parent, size, draw, bg)


def icon_scale(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de escala — duas setas diagonais opostas."""
    def draw(c, s):
        p = 3
        c.create_line(p, p, s - p, s - p, fill=PALETTE["accent2"], width=2)
        # ponta superior esquerda
        c.create_polygon(p, p, p + 6, p, p, p + 6, fill=PALETTE["accent2"], outline="")
        # ponta inferior direita
        c.create_polygon(s - p, s - p, s - p - 6, s - p, s - p, s - p - 6,
                         fill=PALETTE["accent2"], outline="")
    return _svg_icon(parent, size, draw, bg)


def icon_shear(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de cisalhamento — paralelogramo."""
    def draw(c, s):
        p = 3
        pts = [p + 5, s - p, s - p, s - p, s - p - 5, p, p, p]
        c.create_polygon(pts, outline=PALETTE["warn"], fill="", width=2)
    return _svg_icon(parent, size, draw, bg)


def icon_reflect(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de reflexão — linha central + triângulos espelhados."""
    def draw(c, s):
        m = s // 2
        c.create_line(m, 2, m, s - 2, fill=PALETTE["subtext"], width=1, dash=(3, 2))
        p = 3
        c.create_polygon(p, m - 4, m - 4, p, m - 4, s - p,
                         outline=PALETTE["accent"], fill="", width=2)
        c.create_polygon(s - p, m - 4, m + 4, p, m + 4, s - p,
                         outline=PALETTE["accent2"], fill="", width=2)
    return _svg_icon(parent, size, draw, bg)


def icon_undo(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de desfazer — seta curvada para a esquerda."""
    def draw(c, s):
        import math
        m = s // 2
        r = s * 0.32
        pts = []
        for i in range(200):
            a = math.radians(180 + i * 0.9)
            pts.extend([m + r * math.cos(a), m - r * math.sin(a)])
        c.create_line(*pts, fill=PALETTE["warn"], width=2, smooth=True)
        # Arrowhead
        x0, y0 = m - r, m
        c.create_polygon(x0 - 1, y0 - 5, x0 + 5, y0, x0 - 1, y0 + 5,
                         fill=PALETTE["warn"], outline="")
    return _svg_icon(parent, size, draw, bg)


def icon_reset(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de restaurar — círculo com seta cheia."""
    def draw(c, s):
        import math
        m, r, p = s // 2, s * 0.35, 3
        pts = []
        for i in range(360):
            a = math.radians(i)
            pts.extend([m + r * math.cos(a), m - r * math.sin(a)])
        c.create_line(*pts, fill=PALETTE["danger"], width=2, smooth=True)
        c.create_rectangle(m - 3, m - 3, m + 3, m + 3, fill=PALETTE["danger"], outline="")
    return _svg_icon(parent, size, draw, bg)


def icon_color(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de cor — círculo preenchido com gradient visual."""
    def draw(c, s):
        import math
        m, r = s // 2, s * 0.38
        colors = [PALETTE["accent"], PALETTE["accent2"], PALETTE["success"], PALETTE["warn"]]
        for i, col in enumerate(colors):
            a0 = math.radians(i * 90 - 45)
            a1 = math.radians((i + 1) * 90 - 45)
            x1, y1 = m + r * math.cos(a0), m - r * math.sin(a0)
            x2, y2 = m + r * math.cos(a1), m - r * math.sin(a1)
            c.create_polygon(m, m, x1, y1, x2, y2, fill=col, outline="")
    return _svg_icon(parent, size, draw, bg)


def icon_points(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de pontos — 3 círculos."""
    def draw(c, s):
        positions = [(4, 4), (s - 4, s - 4), (4, s - 4)]
        col = PALETTE["success"]
        for x, y in positions:
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=col, outline="")
    return _svg_icon(parent, size, draw, bg)


def icon_matrix(parent, size=18, bg=PALETTE["card"]) -> tk.Canvas:
    """Ícone de matriz — grade 2x2."""
    def draw(c, s):
        p, col = 4, PALETTE["accent2"]
        # linhas da grade
        c.create_line(s // 2, p, s // 2, s - p, fill=col, width=1)
        c.create_line(p, s // 2, s - p, s // 2, fill=col, width=1)
        # borda
        c.create_rectangle(p, p, s - p, s - p, outline=col, width=1)
    return _svg_icon(parent, size, draw, bg)


# ---------------------------------------------------------------------------#
#  Widget: Card container com borda sutil e "sombra"
# ---------------------------------------------------------------------------#

class CardFrame(tk.Frame):
    """Frame estilizado como card com borda arredondada simulada e sombra."""

    def __init__(self, parent, title: str = "", icon_fn=None, **kw):
        T = PALETTE

        # Camada de sombra (deslocamento de 2px)
        shadow = tk.Frame(parent, bg=T["shadow"])
        shadow.pack(fill=tk.X, padx=(10, 6), pady=(6, 0))

        # Frame principal (card)
        super().__init__(shadow, bg=T["card"],
                         highlightbackground=T["border"],
                         highlightthickness=1,
                         **kw)
        self.pack(fill=tk.X, padx=(0, 2), pady=(0, 2))

        # Cabeçalho da seção (se houver título)
        if title:
            header = tk.Frame(self, bg=T["card_alt"])
            header.pack(fill=tk.X)

            if icon_fn:
                ic = icon_fn(header, bg=T["card_alt"])
                ic.pack(side=tk.LEFT, padx=(8, 4), pady=6)

            lbl = tk.Label(
                header, text=title,
                font=("Segoe UI", 9, "bold"),
                bg=T["card_alt"], fg=T["accent"],
                anchor="w",
            )
            lbl.pack(side=tk.LEFT, padx=(0, 8), pady=6)

            # Linha divisória
            sep = tk.Frame(self, bg=T["border"], height=1)
            sep.pack(fill=tk.X)

        # Área interna de conteúdo
        self.body = tk.Frame(self, bg=T["card"], padx=10, pady=8)
        self.body.pack(fill=tk.X)


# ---------------------------------------------------------------------------#
#  Widget: Botão flat com efeito hover
# ---------------------------------------------------------------------------#

class FlatButton(tk.Label):
    """Botão minimalista com hover e click feedback."""

    def __init__(self, parent, text="", icon_fn=None,
                 command=None,
                 bg=PALETTE["card_alt"],
                 fg=PALETTE["text"],
                 hover_bg=PALETTE["border_glow"],
                 hover_fg="#ffffff",
                 font=("Segoe UI", 9),
                 padx=10, pady=5,
                 **kw):
        T = PALETTE
        self._cmd = command
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._hover_fg = hover_fg

        if icon_fn and not text:
            # Botão somente ícone — usa Canvas
            self._is_icon = True
            self._canvas_icon = icon_fn(parent, bg=bg)
            self._canvas_icon.bind("<Enter>", self._on_enter)
            self._canvas_icon.bind("<Leave>", self._on_leave)
            self._canvas_icon.bind("<Button-1>", self._on_click)
            return

        self._is_icon = False
        super().__init__(
            parent, text=text, bg=bg, fg=fg,
            font=font, padx=padx, pady=pady,
            cursor="hand2", anchor="center",
            **kw,
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def pack(self, **kw):
        if getattr(self, "_is_icon", False):
            self._canvas_icon.pack(**kw)
        else:
            super().pack(**kw)

    def grid(self, **kw):
        if getattr(self, "_is_icon", False):
            self._canvas_icon.grid(**kw)
        else:
            super().grid(**kw)

    def _on_enter(self, _e):
        if not getattr(self, "_is_icon", False):
            self.config(bg=self._hover_bg, fg=self._hover_fg)

    def _on_leave(self, _e):
        if not getattr(self, "_is_icon", False):
            self.config(bg=self._bg, fg=self._fg)

    def _on_click(self, _e):
        if self._cmd:
            self._cmd()


# ---------------------------------------------------------------------------#
#  Widget: Botão circular com ícone
# ---------------------------------------------------------------------------#

class CircleButton(tk.Canvas):
    """Botão circular desenhado em canvas com ícone SVG e hover."""

    def __init__(self, parent, size=32, label="", color=PALETTE["accent"],
                 bg=PALETTE["card"], command=None, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=bg, highlightthickness=0, bd=0, **kw)
        self._size = size
        self._color = color
        self._hover_color = PALETTE["card_alt"]
        self._bg = bg
        self._label = label
        self._cmd = command
        self._draw(color)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.config(cursor="hand2")

    def _draw(self, fill_color):
        self.delete("all")
        s = self._size
        p = 2
        self.create_oval(p, p, s - p, s - p, fill=fill_color,
                         outline=PALETTE["border"], width=1)
        if self._label:
            self.create_text(s // 2, s // 2, text=self._label,
                             fill="#ffffff", font=("Segoe UI", 10, "bold"))

    def _on_enter(self, _e):
        self._draw(self._hover_color)
        self.create_oval(2, 2, self._size - 2, self._size - 2,
                         outline=self._color, width=2)

    def _on_leave(self, _e):
        self._draw(self._color)

    def _on_click(self, _e):
        if self._cmd:
            self._cmd()


# ---------------------------------------------------------------------------#
#  Widget: Badge numérico (ex: contador de histórico)
# ---------------------------------------------------------------------------#

class Badge(tk.Canvas):
    """Badge circular com número, estilo pill."""

    def __init__(self, parent, text="0", color=PALETTE["accent"],
                 bg=PALETTE["card"], **kw):
        super().__init__(parent, width=22, height=22, bg=bg,
                         highlightthickness=0, bd=0, **kw)
        self._color = color
        self._bg = bg
        self.set_text(text)

    def set_text(self, text: str):
        self.delete("all")
        self.create_oval(1, 1, 21, 21, fill=self._color, outline="")
        self.create_text(11, 11, text=str(text),
                         fill="#ffffff", font=("Segoe UI", 8, "bold"))


# ---------------------------------------------------------------------------#
#  Helper: criar linha divisória temática
# ---------------------------------------------------------------------------#

def Divider(parent, padx=8, pady=4) -> tk.Frame:
    """Linha horizontal divisória temática."""
    sep = tk.Frame(parent, bg=PALETTE["border"], height=1)
    sep.pack(fill=tk.X, padx=padx, pady=pady)
    return sep


# ---------------------------------------------------------------------------#
#  Helper: rótulo de seção inline (sem LabelFrame)
# ---------------------------------------------------------------------------#

def SectionLabel(parent, text: str, icon: str = "") -> tk.Label:
    """Rótulo de seção estilizado sem usar LabelFrame."""
    T = PALETTE
    full = f"{icon}  {text}" if icon else text
    lbl = tk.Label(
        parent, text=full,
        font=("Segoe UI", 9, "bold"),
        bg=T["card"], fg=T["accent"],
        anchor="w",
    )
    lbl.pack(fill=tk.X, padx=6, pady=(6, 2))
    return lbl
