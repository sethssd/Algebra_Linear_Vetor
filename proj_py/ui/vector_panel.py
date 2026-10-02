"""
ui/vector_panel.py
------------------
Painel lateral direito para gerenciamento de pontos, figuras predefinidas,
alternância entre modo Pontos/Vetores, visibilidade e lista de pontos com
barra de rolagem (scrollbar) ajustada aos limites do painel.
"""

import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
from config import THEME_COLORS
from ui.theme import PALETTE as T, CardFrame, icon_points, icon_scale, Divider
from ui.dialogs import VertexCountDialog
import math

class VectorPanel:
    """Painel lateral direito para escolher figuras, alternar modo
    Pontos/Vetores e criar/remover pontos com suporte a barra de rolagem.
    """

    def __init__(self, parent_frame, canvas_view, shape_manager):
        self.parent_frame = parent_frame
        self.canvas_view = canvas_view
        self.shape_manager = shape_manager

        # Variáveis de controle
        self.preset_shape_var = tk.StringVar(value="Quadrado Unitário")
        self.view_mode_var = tk.StringVar(value="Ambos")

        # Formulário de novo ponto
        self.pt_x_str = tk.StringVar(value="2.0")
        self.pt_y_str = tk.StringVar(value="1.5")
        self.pt_lbl_str = tk.StringVar(value="P1")
        self.pt_color = "#ff79c6"

        # Toggles de visibilidade
        self.show_orig_grid_var = tk.BooleanVar(value=True)
        self.show_trans_grid_var = tk.BooleanVar(value=False)
        self.show_orig_shape_var = tk.BooleanVar(value=True)
        self.show_labels_var = tk.BooleanVar(value=True)

        # Canvas com scrollbar para o painel direito completo
        self.right_canvas = tk.Canvas(parent_frame, bg=THEME_COLORS["panel"], highlightthickness=0)
        self.right_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.right_canvas.yview)
        self.scroll_content = ttk.Frame(self.right_canvas)

        # Janela interna do canvas com ajuste de largura delimitado
        self.canvas_window = self.right_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.right_canvas.configure(yscrollcommand=self.right_scrollbar.set)

        self.right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Ajustar largura do conteúdo para não ultrapassar a borda do painel
        self.right_canvas.bind("<Configure>", self._on_right_canvas_configure)

        # Suporte para rolagem da roda do mouse no painel principal
        self._bind_mousewheel(self.right_canvas, self._on_right_canvas_scroll)

        # Construir widgets
        self._build_widgets()

    def _on_right_canvas_configure(self, event):
        """Ajusta a largura do conteúdo interno ao canvas e atualiza a área de rolagem."""
        self.right_canvas.itemconfig(self.canvas_window, width=event.width)
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))

    def _bind_mousewheel(self, widget, callback):
        """Vincula a roda do mouse ao passar o cursor sobre o widget."""
        widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", callback))
        widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))
        # Suporte para sistemas Linux (Button-4 / Button-5)
        widget.bind("<Enter>", lambda e: (
            widget.bind_all("<Button-4>", lambda ev: callback(ev, delta=120)),
            widget.bind_all("<Button-5>", lambda ev: callback(ev, delta=-120))
        ), add="+")

    def _on_right_canvas_scroll(self, event, delta=None):
        """Callback de rolagem da roda do mouse no painel lateral."""
        d = delta if delta is not None else event.delta
        self.right_canvas.yview_scroll(int(-1 * (d / 120)), "units")

    def _on_list_canvas_scroll(self, event, delta=None):
        """Callback de rolagem da roda do mouse especificamente na lista de pontos."""
        d = delta if delta is not None else event.delta
        self.list_canvas.yview_scroll(int(-1 * (d / 120)), "units")

    # ------------------------------------------------------------------ #
    #  Construção da interface
    # ------------------------------------------------------------------ #

    def _build_widgets(self):
        """Constrói as seções do painel de vetores e pontos."""
        PAD = 4

        # ---- Seção 1: Figuras Predefinidas --------------------------------
        card1 = CardFrame(self.scroll_content, title="Forma da Figura", icon_fn=icon_scale)
        card1.pack(fill=tk.X, padx=6, pady=(8, PAD))

        shapes = ["Quadrado Unitário", "Triângulo", "Casa", "Estrela", "Losango", "Figura Personalizada"]
        cb_shape = ttk.Combobox(card1.body, textvariable=self.preset_shape_var,
                                values=shapes, state="readonly")
        cb_shape.pack(fill=tk.X, pady=(0, 4))
        cb_shape.bind("<<ComboboxSelected>>", lambda e: self.on_shape_change())

        # ---- Seção 2: Modo de Exibição -----------------------------------
        card2 = CardFrame(self.scroll_content, title="Modo de Exibição", icon_fn=icon_points)
        card2.pack(fill=tk.X, padx=6, pady=PAD)

        modes = [
            ("Figura (Polígono)", "Figura"),
            ("Vetores (Setas)", "Vetores"),
            ("Ambos (Figura + Vetores)", "Ambos"),
        ]
        for text, mode_val in modes:
            r = ttk.Radiobutton(
                card2.body, text=text, value=mode_val,
                variable=self.view_mode_var, command=self.on_view_mode_change,
                style="Card.TRadiobutton" if False else "TRadiobutton",
            )
            r.pack(anchor="w", pady=1)

        # ---- Seção 3: Adicionar Ponto -----------------------------------
        card3 = CardFrame(self.scroll_content, title="Adicionar Ponto", icon_fn=icon_points)
        card3.pack(fill=tk.X, padx=6, pady=PAD)

        # Linha de coordenadas
        coords_row = tk.Frame(card3.body, bg=T["card"])
        coords_row.pack(fill=tk.X, pady=(0, 4))

        for col, (label, var, w) in enumerate([
            ("X", self.pt_x_str, 5),
            ("Y", self.pt_y_str, 5),
            ("Nome", self.pt_lbl_str, 5),
        ]):
            tk.Label(coords_row, text=label, font=("Segoe UI", 8),
                     bg=T["card"], fg=T["subtext"]).grid(row=0, column=col * 2, padx=(0, 2), sticky="e")
            ttk.Entry(coords_row, textvariable=var, width=w,
                      justify="center").grid(row=0, column=col * 2 + 1, padx=(0, 6))

        btn_row = tk.Frame(card3.body, bg=T["card"])
        btn_row.pack(fill=tk.X)

        # Botão de cor (círculo colorido)
        self.btn_color_pt = tk.Label(
            btn_row, text="  ●  ",
            font=("Segoe UI", 11, "bold"),
            bg=self.pt_color, fg="#111",
            padx=4, pady=3, cursor="hand2", relief="flat",
        )
        self.btn_color_pt.pack(side=tk.LEFT, padx=(0, 4))
        self.btn_color_pt.bind("<Button-1>", lambda e: self.pick_point_color())

        btn_add = tk.Label(
            btn_row, text="  + Adicionar Ponto  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["accent"], fg="#ffffff",
            padx=8, pady=4, relief="flat",
        )
        btn_add.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        btn_add.bind("<Button-1>", lambda e: self.add_point())
        btn_add.bind("<Enter>", lambda e: btn_add.config(bg=T["border_glow"]))
        btn_add.bind("<Leave>", lambda e: btn_add.config(bg=T["accent"]))

        # ---- Seção 4: Lista de Pontos ------------------------------------
        card4 = CardFrame(self.scroll_content, title="Pontos da Figura", icon_fn=icon_points)
        card4.pack(fill=tk.X, padx=6, pady=PAD)

        # Container scrolável
        list_container = tk.Frame(card4.body, bg=T["card"])
        list_container.pack(fill=tk.X, pady=(0, 4))

        self.list_canvas = tk.Canvas(list_container, bg=T["card_alt"],
                                     highlightthickness=0, height=150)
        self.list_scrollbar = ttk.Scrollbar(list_container, orient="vertical",
                                            command=self.list_canvas.yview)
        self.list_frame = tk.Frame(self.list_canvas, bg=T["card_alt"])

        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)

        self.list_canvas.bind(
            "<Configure>",
            lambda e: (
                self.list_canvas.itemconfig(self.list_window, width=e.width),
                self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
            )
        )
        self.list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._bind_mousewheel(self.list_canvas, self._on_list_canvas_scroll)

        Divider(card4.body, padx=0, pady=2)

        action_row = tk.Frame(card4.body, bg=T["card"])
        action_row.pack(fill=tk.X, pady=2)

        btn_sort = tk.Label(
            action_row, text="  ↻  Organizar  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["card_alt"], fg=T["accent2"],
            padx=8, pady=4, relief="flat",
        )
        btn_sort.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        btn_sort.bind("<Button-1>", lambda e: self.sort_points())
        btn_sort.bind("<Enter>", lambda e: btn_sort.config(bg=T["border"]))
        btn_sort.bind("<Leave>", lambda e: btn_sort.config(bg=T["card_alt"]))

        btn_clear = tk.Label(
            action_row, text="  ✕  Limpar  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["card_alt"], fg=T["danger"],
            padx=8, pady=4, relief="flat",
        )
        btn_clear.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        btn_clear.bind("<Button-1>", lambda e: self.clear_all_points())
        btn_clear.bind("<Enter>", lambda e: btn_clear.config(bg=T["border"]))
        btn_clear.bind("<Leave>", lambda e: btn_clear.config(bg=T["card_alt"]))

        # ---- Seção 5: Visibilidade ---------------------------------------
        card5_bg = T["card"]
        card5 = CardFrame(self.scroll_content, title="Visibilidade")
        card5.pack(fill=tk.X, padx=6, pady=PAD)

        checks = [
            ("Grade Cartesiana (Fundo)", self.show_orig_grid_var),
            ("Grade Transformada", self.show_trans_grid_var),
            ("Contorno Original", self.show_orig_shape_var),
            ("Rótulos e Coordenadas", self.show_labels_var),
        ]
        for text, var in checks:
            ttk.Checkbutton(card5.body, text=text, variable=var,
                            command=self.update_visibilities).pack(anchor="w", pady=1)

        # Espaçamento final
        tk.Frame(self.scroll_content, bg=T["panel"], height=12).pack()

        # Exibir lista de pontos inicial
        self.refresh_points_list_ui()

    # ------------------------------------------------------------------ #
    #  Callbacks de seleção
    # ------------------------------------------------------------------ #

    def on_shape_change(self):
        """Carrega a figura predefinida selecionada no combobox."""
        shape_name = self.preset_shape_var.get()
        if shape_name == "Figura Personalizada":
            dialog = VertexCountDialog(self.parent_frame.winfo_toplevel())
            self.parent_frame.wait_window(dialog)
            if dialog.result is not None:
                self._save_state()
                self.shape_manager.shape_name = "Figura Personalizada"
                self.shape_manager.clear_all()
                self.shape_manager.reset_history()
                
                # Gera `n` pontos em um polígono regular padrão
                n = dialog.result
                radius = 2.0
                palette = ["#ff79c6", "#ffb86c", "#bd93f9", "#50fa7b", "#8be9fd", "#f1fa8c"]
                for i in range(n):
                    angle = 2 * math.pi * i / n - math.pi / 2  # Começa do topo
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)
                    color = palette[i % len(palette)]
                    self.shape_manager.add_point(round(x, 2), round(y, 2), f"P{i+1}", color)
                
                self.refresh_points_list_ui()
                self.canvas_view.redraw()
            else:
                # Se o usuário cancelou, volta o dropdown para a figura anterior
                self.preset_shape_var.set(self.shape_manager.shape_name)

        else:
            # Salva estado antes de trocar a figura
            self._save_state()
            self.shape_manager.load_preset_shape(shape_name)
            self.refresh_points_list_ui()
            self.canvas_view.redraw()

    def on_view_mode_change(self):
        """Altera o modo de exibição (Figura / Vetores / Ambos)."""
        self.canvas_view.view_mode = self.view_mode_var.get()
        self.canvas_view.redraw()

    # ------------------------------------------------------------------ #
    #  Estado completo para desfazer
    # ------------------------------------------------------------------ #

    def _save_state(self):
        """Salva um snapshot completo do estado atual (pontos + cores) no histórico."""
        # Ações de pontos manuais não geram mais histórico matricial
        # Notifica o painel de controles para atualizar o indicador de histórico
        if hasattr(self.canvas_view, 'on_state_saved_callback') and self.canvas_view.on_state_saved_callback:
            self.canvas_view.on_state_saved_callback()

    # ------------------------------------------------------------------ #
    #  Manipulação de pontos
    # ------------------------------------------------------------------ #

    def pick_point_color(self):
        """Abre o seletor de cores para definir a cor do próximo ponto."""
        color_code = colorchooser.askcolor(title="Escolha a cor do Ponto")
        if color_code and color_code[1]:
            self.pt_color = color_code[1]
            self.btn_color_pt.config(bg=self.pt_color)

    def add_point(self):
        """Adiciona um ponto com as coordenadas e rótulo informados."""
        try:
            x = float(self.pt_x_str.get())
            y = float(self.pt_y_str.get())
            lbl = self.pt_lbl_str.get().strip() or f"P{len(self.shape_manager.points) + 1}"

            self._save_state()
            self.shape_manager.add_point(x, y, lbl, self.pt_color)
            self.preset_shape_var.set("Figura Personalizada")
            self.refresh_points_list_ui()
            self.canvas_view.redraw()

            # Atualizar rótulo sugerido para o próximo ponto
            self.pt_lbl_str.set(f"P{len(self.shape_manager.points) + 1}")
        except ValueError:
            messagebox.showerror("Erro de Coordenada", "Insira valores numéricos válidos para X e Y.")

    def remove_point(self, index):
        """Remove o ponto no índice fornecido e atualiza a interface."""
        self._save_state()
        self.shape_manager.remove_point(index)
        self.refresh_points_list_ui()
        self.canvas_view.redraw()

    def sort_points(self):
        """Reordena os pontos angularmente em relação ao centróide para evitar nós/cruzamentos."""
        self._save_state()
        self.shape_manager.sort_points_angularly()
        self.refresh_points_list_ui()
        self.canvas_view.redraw()

    def clear_all_points(self):
        """Remove todos os pontos e atualiza a interface."""
        self._save_state()
        self.shape_manager.clear_all()
        self.preset_shape_var.set("Figura Personalizada")
        self.refresh_points_list_ui()
        self.canvas_view.redraw()

    # ------------------------------------------------------------------ #
    #  Visibilidade
    # ------------------------------------------------------------------ #

    def update_visibilities(self):
        """Aplica as opções de visibilidade ao canvas e redesenha."""
        self.canvas_view.show_orig_grid = self.show_orig_grid_var.get()
        self.canvas_view.show_trans_grid = self.show_trans_grid_var.get()
        self.canvas_view.show_orig_shape = self.show_orig_shape_var.get()
        self.canvas_view.show_labels = self.show_labels_var.get()
        self.canvas_view.redraw()

    # ------------------------------------------------------------------ #
    #  Lista de pontos na interface com barra de rolagem (scrollbar)
    # ------------------------------------------------------------------ #

    def refresh_points_list_ui(self):
        """Reconstrói a lista visual de pontos no painel e atualiza as regiões de rolagem."""
        for child in self.list_frame.winfo_children():
            child.destroy()

        M = self.canvas_view.current_matrix
        points = self.shape_manager.get_transformed_points(M)
        if not points:
            tk.Label(
                self.list_frame, text="Nenhum ponto adicionado.",
                font=("Segoe UI", 8, "italic"),
                bg=T["card_alt"], fg=T["subtext"],
                padx=8, pady=6,
            ).pack(anchor="w")
        else:
            for idx, pt in enumerate(points):
                bg_row = T["card"] if idx % 2 == 0 else T["card_alt"]
                row = tk.Frame(self.list_frame, bg=bg_row)
                row.pack(fill=tk.X)

                # Indicador colorido do ponto
                lbl_dot = tk.Label(row, text="●", fg=pt.color,
                                   bg=bg_row, font=("Segoe UI", 10))
                lbl_dot.pack(side=tk.LEFT, padx=(6, 4), pady=4)

                # Texto com rótulo e coordenadas
                lbl_txt = tk.Label(
                    row, text=f"{pt.label}  ({pt.x:.1f}, {pt.y:.1f})",
                    font=("Segoe UI", 9), bg=bg_row, fg=T["text"],
                )
                lbl_txt.pack(side=tk.LEFT, expand=True, anchor="w")

                # Botão remover minimalista
                btn_del = tk.Label(
                    row, text=" ✕ ", font=("Segoe UI", 8),
                    bg=bg_row, fg=T["subtext"], cursor="hand2",
                )
                btn_del.pack(side=tk.RIGHT, padx=4)
                btn_del.bind("<Button-1>", lambda e, i=idx: self.remove_point(i))
                btn_del.bind("<Enter>", lambda e, b=btn_del: b.config(fg=T["danger"]))
                btn_del.bind("<Leave>", lambda e, b=btn_del: b.config(fg=T["subtext"]))

        # Forçar atualização das regiões de rolagem
        self.list_frame.update_idletasks()
        self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))

