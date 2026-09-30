"""
main.py
-------
Ponto de entrada da aplicação Transformador Linear 2D.
Organizado em módulos e componentes separados.
"""

import tkinter as tk
from config import THEME_COLORS
from core.shape_manager import ShapeManager
from ui.canvas_view import CanvasView
from ui.controls_panel import ControlsPanel
from ui.vector_panel import VectorPanel


def setup_theme_styles(root):
    """Configura o tema visual ttk para combinar com o fundo escuro."""
    style = tk.ttk.Style()
    style.theme_use("default")

    style.configure(".", background=THEME_COLORS["panel"], foreground=THEME_COLORS["text"], font=("Segoe UI", 10))
    style.configure("TFrame", background=THEME_COLORS["panel"])
    style.configure("TLabel", background=THEME_COLORS["panel"], foreground=THEME_COLORS["text"])
    style.configure("TCheckbutton", background=THEME_COLORS["panel"], foreground=THEME_COLORS["text"])
    style.map("TCheckbutton", background=[("active", THEME_COLORS["panel"])])
    style.configure("TRadiobutton", background=THEME_COLORS["panel"], foreground=THEME_COLORS["text"])
    style.map("TRadiobutton", background=[("active", THEME_COLORS["panel"])])
    style.configure("TCombobox", fieldbackground=THEME_COLORS["card"], background=THEME_COLORS["panel"], foreground=THEME_COLORS["text"])
    style.configure("TLabelframe", background=THEME_COLORS["panel"], foreground=THEME_COLORS["accent"])
    style.configure("TLabelframe.Label", background=THEME_COLORS["panel"], foreground=THEME_COLORS["accent"], font=("Segoe UI", 10, "bold"))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Transformações Lineares 2D - Álgebra Linear")
        self.root.geometry("1360x840")
        self.root.minsize(1080, 720)
        self.root.configure(bg=THEME_COLORS["bg"])

        setup_theme_styles(self.root)

        # Gerenciador de Formas
        self.shape_manager = ShapeManager()

        # Construção da Estrutura Visual
        self.create_header()
        self.create_main_body()

    def create_header(self):
        header = tk.Frame(self.root, bg=THEME_COLORS["panel"], height=52, highlightbackground=THEME_COLORS["card_border"], highlightthickness=1)
        header.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))

        title_lbl = tk.Label(header, text="📐 Transformador Linear 2D", font=("Segoe UI", 16, "bold"), bg=THEME_COLORS["panel"], fg=THEME_COLORS["accent"])
        title_lbl.pack(side=tk.LEFT, padx=15, pady=8)

        sub_lbl = tk.Label(header, text="Interface Gráfica com Controles Exatos, Figuras Geométricas e Vetores", font=("Segoe UI", 10, "italic"), bg=THEME_COLORS["panel"], fg=THEME_COLORS["subtext"])
        sub_lbl.pack(side=tk.LEFT, padx=5, pady=8)

    def create_main_body(self):
        container = tk.Frame(self.root, bg=THEME_COLORS["bg"])
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 1. Painel de Controles (Esquerda)
        left_frame = tk.Frame(container, bg=THEME_COLORS["panel"], width=340, highlightbackground=THEME_COLORS["card_border"], highlightthickness=1)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)

        # 2. Área Central (Canvas)
        center_frame = tk.Frame(container, bg=THEME_COLORS["panel"], highlightbackground=THEME_COLORS["card_border"], highlightthickness=1)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Barra de ferramentas superior do Canvas
        toolbar = tk.Frame(center_frame, bg=THEME_COLORS["card"], height=35)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_center = tk.Button(toolbar, text="🎯 Centralizar Origem", font=("Segoe UI", 9), bg=THEME_COLORS["panel"], fg=THEME_COLORS["text"], relief="flat", command=lambda: self.canvas_view.reset_view())
        btn_center.pack(side=tk.LEFT, padx=8, pady=4)

        btn_zin = tk.Button(toolbar, text="🔍 Zoom +", font=("Segoe UI", 9), bg=THEME_COLORS["panel"], fg=THEME_COLORS["text"], relief="flat", command=lambda: self.canvas_view.change_zoom(1.2))
        btn_zin.pack(side=tk.LEFT, padx=2, pady=4)

        btn_zout = tk.Button(toolbar, text="🔍 Zoom -", font=("Segoe UI", 9), bg=THEME_COLORS["panel"], fg=THEME_COLORS["text"], relief="flat", command=lambda: self.canvas_view.change_zoom(0.8))
        btn_zout.pack(side=tk.LEFT, padx=2, pady=4)

        lbl_tip = tk.Label(toolbar, text="💡 Duplo clique no gráfico para adicionar ponto | Arraste para mover | Scroll para Zoom", font=("Segoe UI", 8, "italic"), bg=THEME_COLORS["card"], fg=THEME_COLORS["subtext"])
        lbl_tip.pack(side=tk.RIGHT, padx=10)

        # Componente Visualizador Canvas
        self.canvas_view = CanvasView(center_frame, self.shape_manager)

        # Conectar os Painéis Laterais ao CanvasView
        self.controls_panel = ControlsPanel(left_frame, self.canvas_view)

        # 3. Painel de Vetores e Pontos (Direita)
        right_frame = tk.Frame(container, bg=THEME_COLORS["panel"], width=320, highlightbackground=THEME_COLORS["card_border"], highlightthickness=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        self.vector_panel = VectorPanel(right_frame, self.canvas_view, self.shape_manager)

        # Conectar callback de duplo clique do Canvas para atualizar a lista de pontos na barra lateral
        def on_double_click_point_added():
            self.vector_panel.preset_shape_var.set("Figura Personalizada")
            self.vector_panel.refresh_points_list_ui()

        self.canvas_view.on_point_added_callback = on_double_click_point_added


def main():
    root = tk.Tk()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww, wh = 1360, 840
    x = max(0, (sw - ww) // 2)
    y = max(0, (sh - wh) // 2)
    root.geometry(f"{ww}x{wh}+{x}+{y}")

    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
