"""
ui/vector_panel.py
------------------
Painel de gerenciamento de pontos, figuras predefinidas, exibição de vetores vs pontos e personalização de cores.
"""

import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
from config import THEME_COLORS


class VectorPanel:
    """Painel lateral direito para escolher figuras, alternar modo Pontos/Vetores e criar pontos."""
    def __init__(self, parent_frame, canvas_view, shape_manager):
        self.parent_frame = parent_frame
        self.canvas_view = canvas_view
        self.shape_manager = shape_manager

        # Variáveis de Controle
        self.preset_shape_var = tk.StringVar(value="Quadrado Unitário")
        self.view_mode_var = tk.StringVar(value="Ambos")

        # Formulário de Novo Ponto
        self.pt_x_str = tk.StringVar(value="2.0")
        self.pt_y_str = tk.StringVar(value="1.5")
        self.pt_lbl_str = tk.StringVar(value="P1")
        self.pt_color = "#ff79c6"

        # Toggles de Visibilidade
        self.show_orig_grid_var = tk.BooleanVar(value=True)
        self.show_trans_grid_var = tk.BooleanVar(value=False)
        self.show_orig_shape_var = tk.BooleanVar(value=True)
        self.show_labels_var = tk.BooleanVar(value=True)

        # Scrollbar e Canvas para o Painel Direito
        right_canvas = tk.Canvas(parent_frame, bg=THEME_COLORS["panel"], highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=right_canvas.yview)
        self.scroll_content = ttk.Frame(right_canvas)

        self.scroll_content.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )
        right_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.build_widgets()

    def build_widgets(self):
        """Constrói as seções do painel de vetores e pontos."""
        # Seção 1: Figuras Pré-Definidas
        sec1 = ttk.LabelFrame(self.scroll_content, text=" 📍 Formas & Figuras ", padding=10)
        sec1.pack(fill=tk.X, padx=8, pady=6)

        shapes = ["Quadrado Unitário", "Triângulo", "Casa", "Estrela", "Losango", "Figura Personalizada"]
        cb_shape = ttk.Combobox(sec1, textvariable=self.preset_shape_var, values=shapes, state="readonly")
        cb_shape.pack(fill=tk.X, pady=4)
        cb_shape.bind("<<ComboboxSelected>>", lambda e: self.on_shape_change())

        # Seção 2: Modo de Exibição (Pontos/Figura vs Vetores)
        sec2 = ttk.LabelFrame(self.scroll_content, text=" 👁️ Modo de Exibição ", padding=10)
        sec2.pack(fill=tk.X, padx=8, pady=6)

        modes = [("🔺 Figura (Polígono)", "Figura"), ("🏹 Vetores (Setas)", "Vetores"), ("✨ Ambos (Figura + Vetores)", "Ambos")]
        for text, mode_val in modes:
            r = ttk.Radiobutton(
                sec2,
                text=text,
                value=mode_val,
                variable=self.view_mode_var,
                command=self.on_view_mode_change
            )
            r.pack(anchor="w", pady=2)

        # Seção 3: Adicionar Ponto / Vértice
        sec3 = ttk.LabelFrame(self.scroll_content, text=" ➕ Adicionar Ponto / Vetor ", padding=10)
        sec3.pack(fill=tk.X, padx=8, pady=6)

        grid_pt = ttk.Frame(sec3)
        grid_pt.pack(fill=tk.X, pady=2)

        ttk.Label(grid_pt, text="X:").grid(row=0, column=0, padx=2)
        ttk.Entry(grid_pt, textvariable=self.pt_x_str, width=5).grid(row=0, column=1, padx=2)

        ttk.Label(grid_pt, text="Y:").grid(row=0, column=2, padx=2)
        ttk.Entry(grid_pt, textvariable=self.pt_y_str, width=5).grid(row=0, column=3, padx=2)

        ttk.Label(grid_pt, text="Nome:").grid(row=0, column=4, padx=2)
        ttk.Entry(grid_pt, textvariable=self.pt_lbl_str, width=5).grid(row=0, column=5, padx=2)

        row_btn = ttk.Frame(sec3)
        row_btn.pack(fill=tk.X, pady=4)

        self.btn_color_pt = tk.Button(
            row_btn, text="🎨 Cor", bg=self.pt_color, fg="#11111b",
            font=("Segoe UI", 9, "bold"), relief="flat", command=self.pick_point_color
        )
        self.btn_color_pt.pack(side=tk.LEFT, padx=(0, 4))

        btn_add = ttk.Button(row_btn, text="Adicionar Ponto", command=self.add_point)
        btn_add.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Seção 4: Lista de Pontos da Figura
        sec4 = ttk.LabelFrame(self.scroll_content, text=" 📋 Pontos da Figura ", padding=10)
        sec4.pack(fill=tk.X, padx=8, pady=6)

        self.list_frame = ttk.Frame(sec4)
        self.list_frame.pack(fill=tk.X, pady=2)

        btn_sort = ttk.Button(sec4, text="🔄 Organizar Pontos (Evitar Nós)", command=self.sort_points)
        btn_sort.pack(fill=tk.X, pady=(4, 2))

        btn_clear = ttk.Button(sec4, text="🗑️ Limpar Todos os Pontos", command=self.clear_all_points)
        btn_clear.pack(fill=tk.X, pady=2)

        # Seção 5: Opções de Visibilidade da Grade
        sec5 = ttk.LabelFrame(self.scroll_content, text=" ⚙️ Visibilidade ", padding=10)
        sec5.pack(fill=tk.X, padx=8, pady=6)

        ttk.Checkbutton(sec5, text="Grade Cartesiana (Fundo)", variable=self.show_orig_grid_var, command=self.update_visibilities).pack(anchor="w")
        ttk.Checkbutton(sec5, text="Grade Transformada", variable=self.show_trans_grid_var, command=self.update_visibilities).pack(anchor="w")
        ttk.Checkbutton(sec5, text="Contorno da Figura Original", variable=self.show_orig_shape_var, command=self.update_visibilities).pack(anchor="w")
        ttk.Checkbutton(sec5, text="Rótulos e Coordenadas", variable=self.show_labels_var, command=self.update_visibilities).pack(anchor="w")

        self.refresh_points_list_ui()

    def on_shape_change(self):
        shape_name = self.preset_shape_var.get()
        if shape_name != "Figura Personalizada":
            self.shape_manager.load_preset_shape(shape_name)
            self.refresh_points_list_ui()
            self.canvas_view.redraw()

    def on_view_mode_change(self):
        self.canvas_view.view_mode = self.view_mode_var.get()
        self.canvas_view.redraw()

    def pick_point_color(self):
        color_code = colorchooser.askcolor(title="Escolha a cor do Ponto")
        if color_code and color_code[1]:
            self.pt_color = color_code[1]
            self.btn_color_pt.config(bg=self.pt_color)

    def add_point(self):
        try:
            x = float(self.pt_x_str.get())
            y = float(self.pt_y_str.get())
            lbl = self.pt_lbl_str.get().strip() or f"P{len(self.shape_manager.points)+1}"

            self.shape_manager.add_point(x, y, lbl, self.pt_color)
            self.preset_shape_var.set("Figura Personalizada")
            self.refresh_points_list_ui()
            self.canvas_view.redraw()

            self.pt_lbl_str.set(f"P{len(self.shape_manager.points)+1}")
        except ValueError:
            messagebox.showerror("Erro de Coordenada", "Insira valores numéricos válidos para X e Y.")

    def remove_point(self, index):
        self.shape_manager.remove_point(index)
        self.refresh_points_list_ui()
        self.canvas_view.redraw()

    def sort_points(self):
        """Reordena os pontos angularmente em relação ao centróide para evitar nós/cruzamentos."""
        self.shape_manager.sort_points_angularly()
        self.refresh_points_list_ui()
        self.canvas_view.redraw()

    def clear_all_points(self):
        self.shape_manager.clear_all()
        self.preset_shape_var.set("Figura Personalizada")
        self.refresh_points_list_ui()
        self.canvas_view.redraw()

    def update_visibilities(self):
        self.canvas_view.show_orig_grid = self.show_orig_grid_var.get()
        self.canvas_view.show_trans_grid = self.show_trans_grid_var.get()
        self.canvas_view.show_orig_shape = self.show_orig_shape_var.get()
        self.canvas_view.show_labels = self.show_labels_var.get()
        self.canvas_view.redraw()

    def refresh_points_list_ui(self):
        for child in self.list_frame.winfo_children():
            child.destroy()

        points = self.shape_manager.points
        if not points:
            tk.Label(self.list_frame, text="Nenhum ponto adicionado.", font=("Segoe UI", 8, "italic"), bg=THEME_COLORS["panel"], fg=THEME_COLORS["subtext"]).pack(anchor="w")
            return

        for idx, pt in enumerate(points):
            row = ttk.Frame(self.list_frame)
            row.pack(fill=tk.X, pady=1)

            lbl_dot = tk.Label(row, text="●", fg=pt.color, bg=THEME_COLORS["panel"], font=("Segoe UI", 11))
            lbl_dot.pack(side=tk.LEFT, padx=(0, 4))

            lbl_txt = tk.Label(row, text=f"{pt.label}: ({pt.x:.1f}, {pt.y:.1f})", font=("Segoe UI", 9), bg=THEME_COLORS["panel"], fg=THEME_COLORS["text"])
            lbl_txt.pack(side=tk.LEFT, expand=True, anchor="w")

            btn_del = tk.Button(row, text="❌", font=("Segoe UI", 7), bg=THEME_COLORS["panel"], fg="#ff5555", relief="flat", command=lambda i=idx: self.remove_point(i))
            btn_del.pack(side=tk.RIGHT, padx=2)
