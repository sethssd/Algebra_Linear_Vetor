"""
main.py
-------
Ponto de entrada da aplicação Transformador Linear 2D.
Configura a janela principal, tema visual e organiza os módulos
em painéis (controles, canvas e vetores).
"""

import tkinter as tk
from ui.theme import apply_global_styles, PALETTE as T, CircleButton
from core.shape_manager import ShapeManager
from ui.canvas_view import CanvasView
from ui.controls_panel import ControlsPanel
from ui.vector_panel import VectorPanel


class App:
    """Classe principal da aplicação — monta a janela e conecta os módulos."""

    def __init__(self, root):
        self.root = root
        self.root.title("Transformador Linear 2D — Álgebra Linear")
        self.root.geometry("1400x860")
        self.root.minsize(1080, 720)
        self.root.configure(bg=T["bg"])

        # Aplicar estilos ttk globais
        apply_global_styles(self.root)

        # Gerenciador de Formas
        self.shape_manager = ShapeManager()

        # Construção da Estrutura Visual
        self._create_header()
        self._create_main_body()

    # ------------------------------------------------------------------ #
    #  Cabeçalho
    # ------------------------------------------------------------------ #

    def _create_header(self):
        """Cria o cabeçalho superior com título e subtítulo."""
        header = tk.Frame(self.root, bg=T["panel"], height=54)
        header.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(6, 0))
        header.pack_propagate(False)

        # Accent bar lateral
        accent_bar = tk.Frame(header, bg=T["accent"], width=4)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        # Título
        title_lbl = tk.Label(
            header, text="Transformador Linear 2D",
            font=("Segoe UI", 15, "bold"),
            bg=T["panel"], fg=T["text"],
        )
        title_lbl.pack(side=tk.LEFT, pady=10)

        # Badge "2D"
        badge = tk.Label(
            header, text="2D",
            font=("Segoe UI", 8, "bold"),
            bg=T["accent"], fg="#ffffff",
            padx=5, pady=1,
        )
        badge.pack(side=tk.LEFT, padx=6, pady=18)

        # Subtítulo
        sub_lbl = tk.Label(
            header,
            text="Visualização interativa de transformações matriciais",
            font=("Segoe UI", 9),
            bg=T["panel"], fg=T["subtext"],
        )
        sub_lbl.pack(side=tk.LEFT, padx=8, pady=10)

        # Separador inferior do header
        sep = tk.Frame(self.root, bg=T["border"], height=1)
        sep.pack(side=tk.TOP, fill=tk.X, padx=6)

    # ------------------------------------------------------------------ #
    #  Corpo principal (painéis esquerdo, central e direito)
    # ------------------------------------------------------------------ #

    def _create_main_body(self):
        """Cria os três painéis: controles (esquerda), canvas (centro) e vetores (direita)."""
        container = tk.Frame(self.root, bg=T["bg"])
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        # 1. Painel de Controles (Esquerda)
        left_frame = tk.Frame(
            container, bg=T["panel"], width=340,
            highlightbackground=T["border"], highlightthickness=1,
        )
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)

        # 2. Área Central (Canvas)
        center_frame = tk.Frame(
            container, bg=T["panel"],
            highlightbackground=T["border"], highlightthickness=1,
        )
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Barra de ferramentas do Canvas
        toolbar = tk.Frame(center_frame, bg=T["card"], height=38)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)

        btn_center = tk.Label(
            toolbar, text="⊕  Centralizar", font=("Segoe UI", 9),
            bg=T["card"], fg=T["subtext"],
            padx=10, pady=8, cursor="hand2",
        )
        btn_center.pack(side=tk.LEFT)
        btn_center.bind("<Enter>", lambda e: btn_center.config(fg=T["text"]))
        btn_center.bind("<Leave>", lambda e: btn_center.config(fg=T["subtext"]))
        btn_center.bind("<Button-1>", lambda e: self.canvas_view.reset_view())

        sep_v = tk.Frame(toolbar, bg=T["border"], width=1)
        sep_v.pack(side=tk.LEFT, fill=tk.Y, pady=8)

        btn_zin = tk.Label(
            toolbar, text="  ＋  ", font=("Segoe UI", 10, "bold"),
            bg=T["card"], fg=T["subtext"],
            padx=8, pady=8, cursor="hand2",
        )
        btn_zin.pack(side=tk.LEFT)
        btn_zin.bind("<Enter>", lambda e: btn_zin.config(fg=T["accent"]))
        btn_zin.bind("<Leave>", lambda e: btn_zin.config(fg=T["subtext"]))
        btn_zin.bind("<Button-1>", lambda e: self.canvas_view.change_zoom(1.2))

        btn_zout = tk.Label(
            toolbar, text="  －  ", font=("Segoe UI", 10, "bold"),
            bg=T["card"], fg=T["subtext"],
            padx=8, pady=8, cursor="hand2",
        )
        btn_zout.pack(side=tk.LEFT)
        btn_zout.bind("<Enter>", lambda e: btn_zout.config(fg=T["accent"]))
        btn_zout.bind("<Leave>", lambda e: btn_zout.config(fg=T["subtext"]))
        btn_zout.bind("<Button-1>", lambda e: self.canvas_view.change_zoom(0.8))

        sep_v2 = tk.Frame(toolbar, bg=T["border"], width=1)
        sep_v2.pack(side=tk.LEFT, fill=tk.Y, pady=8)

        lbl_tip = tk.Label(
            toolbar,
            text="  Duplo clique para adicionar ponto  ·  Arrastar para mover  ·  Scroll para zoom",
            font=("Segoe UI", 8),
            bg=T["card"], fg=T["subtext"],
        )
        lbl_tip.pack(side=tk.LEFT, padx=6)

        sep_toolbar = tk.Frame(center_frame, bg=T["border"], height=1)
        sep_toolbar.pack(side=tk.TOP, fill=tk.X)

        # Componente Visualizador Canvas
        self.canvas_view = CanvasView(center_frame, self.shape_manager)

        # Conectar o Painel de Controles (Esquerda) ao CanvasView
        self.controls_panel = ControlsPanel(left_frame, self.canvas_view)

        # 3. Painel de Vetores e Pontos (Direita)
        right_frame = tk.Frame(
            container, bg=T["panel"], width=320,
            highlightbackground=T["border"], highlightthickness=1,
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        self.vector_panel = VectorPanel(right_frame, self.canvas_view, self.shape_manager)

        # Callback de duplo clique no Canvas para atualizar lista de pontos
        def on_double_click_point_added():
            self.vector_panel.preset_shape_var.set("Figura Personalizada")
            self.vector_panel.refresh_points_list_ui()

        self.canvas_view.on_point_added_callback = on_double_click_point_added

        # Callback de fixação de transformação para atualizar lista de pontos
        def on_transformation_committed():
            self.vector_panel.preset_shape_var.set("Figura Personalizada")
            self.vector_panel.refresh_points_list_ui()

        self.controls_panel.on_transformation_committed_callback = on_transformation_committed

        # Atalho de teclado Ctrl+Z
        self.root.bind("<Control-z>", lambda e: self.controls_panel.undo_transformation())

        # Callback de estado salvo (duplo clique no canvas)
        self.canvas_view.on_state_saved_callback = self.controls_panel._update_undo_button_state


def main():
    """Inicializa a janela principal e executa o loop de eventos."""
    root = tk.Tk()

    # Centralizar na tela
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww, wh = 1400, 860
    x = max(0, (sw - ww) // 2)
    y = max(0, (sh - wh) // 2)
    root.geometry(f"{ww}x{wh}+{x}+{y}")

    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
