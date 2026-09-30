"""
ui/controls_panel.py
--------------------
Painel de controle com Sliders + Caixas de Texto numéricas sincronizadas para valores exatos,
presets de transformação, seletor de cor e animação.
"""

import tkinter as tk
from tkinter import colorchooser, ttk
from config import THEME_COLORS
from core.matrix import Matrix2D


class ControlsPanel:
    """Gerencia a barra lateral de controles de transformação."""
    def __init__(self, parent_frame, canvas_view):
        self.canvas_view = canvas_view
        self.target_matrix = Matrix2D.identity()
        self.morph_t = 1.0
        self.is_animating = False
        self.anim_job = None

        # Variáveis de Controle
        self.preset_var = tk.StringVar(value="Identidade")

        # Rotação
        self.angle_str = tk.StringVar(value="45.0")
        self.angle_val = 45.0

        # Escala
        self.scale_x_str = tk.StringVar(value="1.5")
        self.scale_y_str = tk.StringVar(value="1.5")
        self.scale_x_val = 1.5
        self.scale_y_val = 1.5

        # Cisalhamento
        self.shear_x_str = tk.StringVar(value="0.5")
        self.shear_y_str = tk.StringVar(value="0.5")
        self.shear_x_val = 0.5
        self.shear_y_val = 0.5

        # Matriz Manual 2x2
        self.m_a_str = tk.StringVar(value="1.0")
        self.m_b_str = tk.StringVar(value="0.0")
        self.m_c_str = tk.StringVar(value="0.0")
        self.m_d_str = tk.StringVar(value="1.0")

        # Animação Morphing
        self.morph_var = tk.DoubleVar(value=100.0)

        # Scrollable Frame no Painel Esquerdo
        left_canvas = tk.Canvas(parent_frame, bg=THEME_COLORS["panel"], highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=left_canvas.yview)
        self.scroll_content = ttk.Frame(left_canvas)

        self.scroll_content.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        left_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.build_widgets()
        self.on_preset_change()

    def build_widgets(self):
        """Constrói as seções de controles."""
        # Seção 1: Preset
        sec1 = ttk.LabelFrame(self.scroll_content, text=" 1. Presets de Transformação ", padding=10)
        sec1.pack(fill=tk.X, padx=8, pady=6)

        presets = [
            "Identidade",
            "Rotação",
            "Escala",
            "Cisalhamento X (Shear X)",
            "Cisalhamento Y (Shear Y)",
            "Reflexão no Eixo X",
            "Reflexão no Eixo Y",
            "Reflexão na Reta Y = X",
            "Projeção no Eixo X",
            "Projeção no Eixo Y",
            "Matriz Personalizada 2x2"
        ]

        cb = ttk.Combobox(sec1, textvariable=self.preset_var, values=presets, state="readonly")
        cb.pack(fill=tk.X, pady=4)
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_preset_change())

        # Frame dinâmico para Sliders + Entradas exatas
        self.param_frame = ttk.Frame(sec1)
        self.param_frame.pack(fill=tk.X, pady=4)

        # Seção 2: Matriz 2x2 Resultante
        sec2 = ttk.LabelFrame(self.scroll_content, text=" 2. Matriz de Transformação [M] ", padding=10)
        sec2.pack(fill=tk.X, padx=8, pady=6)

        grid_m = ttk.Frame(sec2)
        grid_m.pack(pady=4)

        tk.Label(grid_m, text="[", font=("Segoe UI", 24), bg=THEME_COLORS["panel"], fg=THEME_COLORS["accent"]).grid(row=0, column=0, rowspan=2, padx=2)
        
        ttk.Entry(grid_m, textvariable=self.m_a_str, width=6, justify="center").grid(row=0, column=1, padx=3, pady=3)
        ttk.Entry(grid_m, textvariable=self.m_b_str, width=6, justify="center").grid(row=0, column=2, padx=3, pady=3)
        ttk.Entry(grid_m, textvariable=self.m_c_str, width=6, justify="center").grid(row=1, column=1, padx=3, pady=3)
        ttk.Entry(grid_m, textvariable=self.m_d_str, width=6, justify="center").grid(row=1, column=2, padx=3, pady=3)

        tk.Label(grid_m, text="]", font=("Segoe UI", 24), bg=THEME_COLORS["panel"], fg=THEME_COLORS["accent"]).grid(row=0, column=3, rowspan=2, padx=2)

        btn_apply = ttk.Button(sec2, text="Aplicar Matriz Manual", command=self.on_apply_custom_matrix)
        btn_apply.pack(fill=tk.X, pady=4)

        # Seção 3: Botão para Troca de Cor da Figura
        sec3 = ttk.LabelFrame(self.scroll_content, text=" 3. Aparência e Cor ", padding=10)
        sec3.pack(fill=tk.X, padx=8, pady=6)

        btn_color = ttk.Button(sec3, text="🎨 Alterar Cor da Figura / Polígono", command=self.choose_shape_color)
        btn_color.pack(fill=tk.X, pady=4)

        # Seção 4: Animação Morphing
        sec4 = ttk.LabelFrame(self.scroll_content, text=" 4. Animação de Transformação ", padding=10)
        sec4.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(sec4, text="Progresso da Transformação (t):", bg=THEME_COLORS["panel"], fg=THEME_COLORS["text"]).pack(anchor="w")
        slider_m = ttk.Scale(sec4, from_=0.0, to=100.0, variable=self.morph_var, command=self.on_morph_slider)
        slider_m.pack(fill=tk.X, pady=4)

        btn_box = ttk.Frame(sec4)
        btn_box.pack(fill=tk.X, pady=4)

        self.btn_play = ttk.Button(btn_box, text="▶ Animar", command=self.toggle_animation)
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        btn_reset_t = ttk.Button(btn_box, text="⏮ Reset (t=0)", command=self.reset_morph)
        btn_reset_t.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

    def update_dynamic_controls(self):
        """Monta os controles dinâmicos (Slider + Caixa de Texto para Valor Exato)."""
        for child in self.param_frame.winfo_children():
            child.destroy()

        preset = self.preset_var.get()

        if preset == "Rotação":
            self.create_slider_and_entry(
                parent=self.param_frame,
                label_text="Ângulo de Rotação (°):",
                slider_min=-360.0,
                slider_max=360.0,
                str_var=self.angle_str,
                on_change_callback=self.on_rotation_changed
            )

        elif preset == "Escala":
            self.create_slider_and_entry(
                parent=self.param_frame,
                label_text="Escala X (S_x):",
                slider_min=-5.0,
                slider_max=5.0,
                str_var=self.scale_x_str,
                on_change_callback=self.on_scale_changed
            )
            self.create_slider_and_entry(
                parent=self.param_frame,
                label_text="Escala Y (S_y):",
                slider_min=-5.0,
                slider_max=5.0,
                str_var=self.scale_y_str,
                on_change_callback=self.on_scale_changed
            )

        elif preset == "Cisalhamento X (Shear X)":
            self.create_slider_and_entry(
                parent=self.param_frame,
                label_text="Fator k_x:",
                slider_min=-5.0,
                slider_max=5.0,
                str_var=self.shear_x_str,
                on_change_callback=self.on_shear_x_changed
            )

        elif preset == "Cisalhamento Y (Shear Y)":
            self.create_slider_and_entry(
                parent=self.param_frame,
                label_text="Fator k_y:",
                slider_min=-5.0,
                slider_max=5.0,
                str_var=self.shear_y_str,
                on_change_callback=self.on_shear_y_changed
            )

    def create_slider_and_entry(self, parent, label_text, slider_min, slider_max, str_var, on_change_callback):
        """Cria um conjunto com rótulo, slider e caixa de entrada numérica sincronizados."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=4)

        lbl = ttk.Label(frame, text=label_text)
        lbl.pack(anchor="w")

        controls_row = ttk.Frame(frame)
        controls_row.pack(fill=tk.X, pady=2)

        # Variável numérico do Slider
        try:
            initial_val = float(str_var.get())
        except ValueError:
            initial_val = 0.0

        double_var = tk.DoubleVar(value=initial_val)

        slider = ttk.Scale(
            controls_row,
            from_=slider_min,
            to=slider_max,
            variable=double_var,
            command=lambda val: self._on_slider_move(val, str_var, on_change_callback)
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        # Entrada de Texto Numérica para o Usuário Digitar Qualquer Valor Exato
        entry = ttk.Entry(controls_row, textvariable=str_var, width=7, justify="center")
        entry.pack(side=tk.RIGHT)

        # Evento quando o usuário digita na caixa de texto
        str_var.trace_add("write", lambda *args: self._on_entry_type(str_var, double_var, on_change_callback))

    def _on_slider_move(self, val_str, str_var, callback):
        """Quando o slider se move, atualiza a caixa de texto."""
        try:
            val = float(val_str)
            # Atualiza o texto sem disparar um loop infinito
            str_var.set(f"{val:.2f}")
            callback()
        except ValueError:
            pass

    def _on_entry_type(self, str_var, double_var, callback):
        """Quando o usuário digita um valor exato na caixa de texto."""
        try:
            val = float(str_var.get())
            double_var.set(val)
            callback()
        except ValueError:
            pass

    # Callbacks de alteração dos parâmetros
    def on_rotation_changed(self):
        try:
            ang = float(self.angle_str.get())
            self.target_matrix = Matrix2D.rotation(ang)
            self.update_matrix_display()
        except ValueError:
            pass

    def on_scale_changed(self):
        try:
            sx = float(self.scale_x_str.get())
            sy = float(self.scale_y_str.get())
            self.target_matrix = Matrix2D.scaling(sx, sy)
            self.update_matrix_display()
        except ValueError:
            pass

    def on_shear_x_changed(self):
        try:
            kx = float(self.shear_x_str.get())
            self.target_matrix = Matrix2D.shear_x(kx)
            self.update_matrix_display()
        except ValueError:
            pass

    def on_shear_y_changed(self):
        try:
            ky = float(self.shear_y_str.get())
            self.target_matrix = Matrix2D.shear_y(ky)
            self.update_matrix_display()
        except ValueError:
            pass

    def on_preset_change(self):
        preset = self.preset_var.get()
        self.update_dynamic_controls()

        if preset == "Identidade":
            self.target_matrix = Matrix2D.identity()
        elif preset == "Rotação":
            self.on_rotation_changed()
            return
        elif preset == "Escala":
            self.on_scale_changed()
            return
        elif preset == "Cisalhamento X (Shear X)":
            self.on_shear_x_changed()
            return
        elif preset == "Cisalhamento Y (Shear Y)":
            self.on_shear_y_changed()
            return
        elif preset == "Reflexão no Eixo X":
            self.target_matrix = Matrix2D.reflect_x()
        elif preset == "Reflexão no Eixo Y":
            self.target_matrix = Matrix2D.reflect_y()
        elif preset == "Reflexão na Reta Y = X":
            self.target_matrix = Matrix2D.reflect_yx()
        elif preset == "Projeção no Eixo X":
            self.target_matrix = Matrix2D.project_x()
        elif preset == "Projeção no Eixo Y":
            self.target_matrix = Matrix2D.project_y()
        else:
            self.on_apply_custom_matrix()
            return

        self.update_matrix_display()

    def on_apply_custom_matrix(self):
        try:
            a = float(self.m_a_str.get())
            b = float(self.m_b_str.get())
            c = float(self.m_c_str.get())
            d = float(self.m_d_str.get())
            self.preset_var.set("Matriz Personalizada 2x2")
            self.target_matrix = [[a, b], [c, d]]
            self.apply_current_matrix_to_canvas()
        except ValueError:
            pass

    def update_matrix_display(self):
        M = self.target_matrix
        self.m_a_str.set(f"{M[0][0]:.2f}")
        self.m_b_str.set(f"{M[0][1]:.2f}")
        self.m_c_str.set(f"{M[1][0]:.2f}")
        self.m_d_str.set(f"{M[1][1]:.2f}")
        self.apply_current_matrix_to_canvas()

    def apply_current_matrix_to_canvas(self):
        M_interp = Matrix2D.interpolate(self.target_matrix, self.morph_t)
        self.canvas_view.update_matrix(M_interp)

    def choose_shape_color(self):
        """Abre a caixa de diálogo para escolha de cor da figura."""
        color_code = colorchooser.askcolor(title="Escolha a Cor da Figura / Polígono")
        if color_code and color_code[1]:
            self.canvas_view.shape_color = color_code[1]
            self.canvas_view.shape_outline = color_code[1]
            self.canvas_view.redraw()

    # Morphing e Animação
    def on_morph_slider(self, val):
        self.morph_t = float(val) / 100.0
        self.apply_current_matrix_to_canvas()

    def reset_morph(self):
        self.morph_var.set(0.0)
        self.morph_t = 0.0
        self.apply_current_matrix_to_canvas()

    def toggle_animation(self):
        if self.is_animating:
            self.is_animating = False
            self.btn_play.config(text="▶ Animar")
        else:
            self.is_animating = True
            self.btn_play.config(text="⏸ Pausar")
            if self.morph_var.get() >= 100.0:
                self.morph_var.set(0.0)
            self.step_animation()

    def step_animation(self):
        if not self.is_animating:
            return

        current_val = self.morph_var.get()
        next_val = current_val + 2.5

        if next_val >= 100.0:
            next_val = 100.0
            self.is_animating = False
            self.btn_play.config(text="▶ Animar")

        self.morph_var.set(next_val)
        self.morph_t = next_val / 100.0
        self.apply_current_matrix_to_canvas()

        if self.is_animating:
            self.anim_job = self.scroll_content.after(20, self.step_animation)
