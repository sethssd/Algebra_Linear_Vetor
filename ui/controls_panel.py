"""
ui/controls_panel.py
--------------------
Painel de controles lateral esquerdo do Transformador Linear 2D.
Gerencia presets de transformação, entrada de matriz personalizada,
slider de interpolação e animação de morphing.
"""

import time
import tkinter as tk
from tkinter import colorchooser, ttk

from config import get_theme, CURRENT_THEME
from core.matrix import Matrix2D


# Auxiliar para obter cores do tema ativo
def cor_tema(chave: str) -> str:
    """Retorna a cor correspondente à chave no tema atualmente ativo."""
    return get_theme()[chave]


class ControlsPanel:
    """Gerencia o painel lateral de controles de transformações."""

    def __init__(self, parent_frame, canvas_view):
        self.canvas_view = canvas_view

        # Matriz-alvo para interpolação (lista de listas 2×2)
        self.target_matrix = Matrix2D.identity()
        self.morph_t = 1.0           # Progresso da interpolação (0.0 a 1.0)
        self.is_animating = False    # Controle da animação
        self.anim_job = None         # Referência ao callback agendado
        self.last_anim_time = None   # Para cálculo de delta-time

        # Variáveis de controle dos widgets
        self.preset_var = tk.StringVar(value="Identidade")
        self.angle_str = tk.StringVar(value="45.0")
        self.scale_x_str = tk.StringVar(value="1.5")
        self.scale_y_str = tk.StringVar(value="1.5")
        self.shear_x_str = tk.StringVar(value="0.5")
        self.shear_y_str = tk.StringVar(value="0.5")

        # Entradas da matriz manual 2×2
        self.m_a_str = tk.StringVar(value="1.0")
        self.m_b_str = tk.StringVar(value="0.0")
        self.m_c_str = tk.StringVar(value="0.0")
        self.m_d_str = tk.StringVar(value="1.0")

        # Slider de morphing (0 a 100)
        self.morph_var = tk.DoubleVar(value=100.0)

        # Canvas com scrollbar para o painel esquerdo
        left_canvas = tk.Canvas(parent_frame, bg=cor_tema("panel"), highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=left_canvas.yview)
        self.scroll_content = ttk.Frame(left_canvas)
        canvas_win = left_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.bind(
            "<Configure>",
            lambda e: (
                left_canvas.itemconfig(canvas_win, width=e.width),
                left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            )
        )
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Construir interface e aplicar preset inicial
        self._build_widgets()
        self.on_preset_change()

    # ------------------------------------------------------------------ #
    #  Construção da interface
    # ------------------------------------------------------------------ #

    def _build_widgets(self):
        """Constrói todas as seções de widgets dentro do painel com scroll."""

        # Seção 1 — Presets de Transformação
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
            "Matriz Personalizada 2x2",
        ]
        cb = ttk.Combobox(sec1, textvariable=self.preset_var, values=presets, state="readonly")
        cb.pack(fill=tk.X, pady=4)
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_preset_change())

        # Frame para controles dinâmicos (sliders de ângulo, escala, etc.)
        self.param_frame = ttk.Frame(sec1)
        self.param_frame.pack(fill=tk.X, pady=4)

        # Seção 2 — Exibição da Matriz Resultante
        sec2 = ttk.LabelFrame(self.scroll_content, text=" 2. Matriz de Transformação [M] ", padding=10)
        sec2.pack(fill=tk.X, padx=8, pady=6)

        grid_m = ttk.Frame(sec2)
        grid_m.pack(pady=4)

        # Colchetes decorativos e campos de entrada da matriz
        tk.Label(grid_m, text="[", font=("Segoe UI", 24),
                 bg=cor_tema("panel"), fg=cor_tema("accent")).grid(row=0, column=0, rowspan=2, padx=2)
        ttk.Entry(grid_m, textvariable=self.m_a_str, width=6, justify="center").grid(row=0, column=1, padx=3, pady=3)
        ttk.Entry(grid_m, textvariable=self.m_b_str, width=6, justify="center").grid(row=0, column=2, padx=3, pady=3)
        ttk.Entry(grid_m, textvariable=self.m_c_str, width=6, justify="center").grid(row=1, column=1, padx=3, pady=3)
        ttk.Entry(grid_m, textvariable=self.m_d_str, width=6, justify="center").grid(row=1, column=2, padx=3, pady=3)
        tk.Label(grid_m, text="]", font=("Segoe UI", 24),
                 bg=cor_tema("panel"), fg=cor_tema("accent")).grid(row=0, column=3, rowspan=2, padx=2)

        btn_apply = ttk.Button(sec2, text="Aplicar Matriz Manual", command=self.on_apply_custom_matrix)
        btn_apply.pack(fill=tk.X, pady=4)

        # Seção 3 — Cor da Figura
        sec3 = ttk.LabelFrame(self.scroll_content, text=" 3. Aparência e Cor ", padding=10)
        sec3.pack(fill=tk.X, padx=8, pady=6)

        btn_color = ttk.Button(sec3, text="🎨 Alterar Cor da Figura / Polígono", command=self.choose_shape_color)
        btn_color.pack(fill=tk.X, pady=4)

        # Seção 4 — Animação de Morphing
        sec4 = ttk.LabelFrame(self.scroll_content, text=" 4. Animação de Transformação ", padding=10)
        sec4.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(sec4, text="Progresso da Transformação (t):",
                 bg=cor_tema("panel"), fg=cor_tema("text")).pack(anchor="w")
        slider_m = ttk.Scale(sec4, from_=0.0, to=100.0, variable=self.morph_var, command=self.on_morph_slider)
        slider_m.pack(fill=tk.X, pady=4)

        btn_box = ttk.Frame(sec4)
        btn_box.pack(fill=tk.X, pady=4)
        self.btn_play = ttk.Button(btn_box, text="▶ Animar", command=self.toggle_animation)
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        btn_reset_t = ttk.Button(btn_box, text="⏮ Reset (t=0)", command=self.reset_morph)
        btn_reset_t.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

    # ------------------------------------------------------------------ #
    #  Controles dinâmicos (sliders por tipo de transformação)
    # ------------------------------------------------------------------ #

    def _update_dynamic_controls(self):
        """Cria sliders/entries conforme o preset selecionado."""
        for child in self.param_frame.winfo_children():
            child.destroy()

        preset = self.preset_var.get()

        if preset == "Rotação":
            self._create_slider_and_entry(
                parent=self.param_frame,
                label_text="Ângulo de Rotação (°):",
                slider_min=-360.0, slider_max=360.0,
                str_var=self.angle_str,
                on_change=self._on_rotation_changed,
            )
        elif preset == "Escala":
            self._create_slider_and_entry(
                parent=self.param_frame,
                label_text="Escala X (S_x):",
                slider_min=-5.0, slider_max=5.0,
                str_var=self.scale_x_str,
                on_change=self._on_scale_changed,
            )
            self._create_slider_and_entry(
                parent=self.param_frame,
                label_text="Escala Y (S_y):",
                slider_min=-5.0, slider_max=5.0,
                str_var=self.scale_y_str,
                on_change=self._on_scale_changed,
            )
        elif preset == "Cisalhamento X (Shear X)":
            self._create_slider_and_entry(
                parent=self.param_frame,
                label_text="Fator k_x:",
                slider_min=-5.0, slider_max=5.0,
                str_var=self.shear_x_str,
                on_change=self._on_shear_x_changed,
            )
        elif preset == "Cisalhamento Y (Shear Y)":
            self._create_slider_and_entry(
                parent=self.param_frame,
                label_text="Fator k_y:",
                slider_min=-5.0, slider_max=5.0,
                str_var=self.shear_y_str,
                on_change=self._on_shear_y_changed,
            )

    def _create_slider_and_entry(self, parent, label_text, slider_min, slider_max, str_var, on_change):
        """Cria um par sincronizado de slider + campo de entrada."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=4)

        lbl = ttk.Label(frame, text=label_text)
        lbl.pack(anchor="w")

        controls_row = ttk.Frame(frame)
        controls_row.pack(fill=tk.X, pady=2)

        try:
            initial_val = float(str_var.get())
        except ValueError:
            initial_val = 0.0

        double_var = tk.DoubleVar(value=initial_val)

        slider = ttk.Scale(
            controls_row,
            from_=slider_min, to=slider_max,
            variable=double_var,
            command=lambda val: self._on_slider_move(val, str_var, on_change),
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        entry = ttk.Entry(controls_row, textvariable=str_var, width=7, justify="center")
        entry.pack(side=tk.RIGHT)

        # Sincronizar alterações no campo de texto com o slider
        str_var.trace_add("write", lambda *args: self._on_entry_type(str_var, double_var, on_change))

    def _on_slider_move(self, val_str, str_var, callback):
        """Chamado quando o slider é movido — atualiza o campo de texto."""
        try:
            val = float(val_str)
            str_var.set(f"{val:.2f}")
            callback()
        except ValueError:
            pass

    def _on_entry_type(self, str_var, double_var, callback):
        """Chamado quando o campo de texto é editado — atualiza o slider."""
        try:
            val = float(str_var.get())
            double_var.set(val)
            callback()
        except ValueError:
            pass

    # ------------------------------------------------------------------ #
    #  Callbacks de cada tipo de transformação
    # ------------------------------------------------------------------ #

    def _on_rotation_changed(self):
        """Recalcula a matriz de rotação com base no ângulo informado."""
        try:
            ang = float(self.angle_str.get())
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.rotation(ang))
            self._update_matrix_display()
        except ValueError:
            pass

    def _on_scale_changed(self):
        """Recalcula a matriz de escala com base em S_x e S_y."""
        try:
            sx = float(self.scale_x_str.get())
            sy = float(self.scale_y_str.get())
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.scaling(sx, sy))
            self._update_matrix_display()
        except ValueError:
            pass

    def _on_shear_x_changed(self):
        """Recalcula a matriz de cisalhamento X."""
        try:
            kx = float(self.shear_x_str.get())
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.shear_x(kx))
            self._update_matrix_display()
        except ValueError:
            pass

    def _on_shear_y_changed(self):
        """Recalcula a matriz de cisalhamento Y."""
        try:
            ky = float(self.shear_y_str.get())
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.shear_y(ky))
            self._update_matrix_display()
        except ValueError:
            pass

    # ------------------------------------------------------------------ #
    #  Seleção de preset
    # ------------------------------------------------------------------ #

    def on_preset_change(self):
        """Chamado quando o preset do combobox é alterado."""
        preset = self.preset_var.get()
        self._update_dynamic_controls()

        if preset == "Identidade":
            self.target_matrix = Matrix2D.identity()
        elif preset == "Rotação":
            self._on_rotation_changed()
            return
        elif preset == "Escala":
            self._on_scale_changed()
            return
        elif preset == "Cisalhamento X (Shear X)":
            self._on_shear_x_changed()
            return
        elif preset == "Cisalhamento Y (Shear Y)":
            self._on_shear_y_changed()
            return
        elif preset == "Reflexão no Eixo X":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.reflect_x())
        elif preset == "Reflexão no Eixo Y":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.reflect_y())
        elif preset == "Reflexão na Reta Y = X":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.reflect_yx())
        elif preset == "Projeção no Eixo X":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.project_x())
        elif preset == "Projeção no Eixo Y":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.project_y())
        else:
            # Matriz Personalizada 2x2
            self.on_apply_custom_matrix()
            return

        self._update_matrix_display()

    # ------------------------------------------------------------------ #
    #  Matriz personalizada
    # ------------------------------------------------------------------ #

    def on_apply_custom_matrix(self):
        """Aplica a matriz digitada manualmente nos campos de entrada."""
        try:
            a = float(self.m_a_str.get())
            b = float(self.m_b_str.get())
            c = float(self.m_c_str.get())
            d = float(self.m_d_str.get())
            self.preset_var.set("Matriz Personalizada 2x2")
            self.target_matrix = [[a, b], [c, d]]
            self._apply_current_matrix_to_canvas()
        except ValueError:
            pass

    # ------------------------------------------------------------------ #
    #  Atualização da exibição da matriz e envio ao canvas
    # ------------------------------------------------------------------ #

    def _update_matrix_display(self):
        """Atualiza os campos de texto da matriz e aplica ao canvas."""
        M = self.target_matrix
        self.m_a_str.set(f"{M[0][0]:.2f}")
        self.m_b_str.set(f"{M[0][1]:.2f}")
        self.m_c_str.set(f"{M[1][0]:.2f}")
        self.m_d_str.set(f"{M[1][1]:.2f}")
        self._apply_current_matrix_to_canvas()

    def _apply_current_matrix_to_canvas(self):
        """Interpola entre a identidade e a matriz-alvo e envia ao canvas.

        O resultado é sempre uma lista de listas [[a, b], [c, d]],
        garantindo compatibilidade com o acesso M[i][j] no CanvasView.
        """
        identity = Matrix2D.identity()
        # Interpolar usando NumPy e converter de volta para lista de listas
        M_interp = Matrix2D.interpolate_matrices(identity, self.target_matrix, self.morph_t)
        self.canvas_view.update_matrix(M_interp)

    # ------------------------------------------------------------------ #
    #  Cor da figura
    # ------------------------------------------------------------------ #

    def choose_shape_color(self):
        """Abre o seletor de cores para alterar a cor do polígono."""
        color_code = colorchooser.askcolor(title="Escolha a Cor da Figura / Polígono")
        if color_code and color_code[1]:
            self.canvas_view.shape_color = color_code[1]
            self.canvas_view.shape_outline = color_code[1]
            self.canvas_view.redraw()

    # ------------------------------------------------------------------ #
    #  Animação de Morphing (interpolação animada)
    # ------------------------------------------------------------------ #

    def on_morph_slider(self, val):
        """Chamado quando o slider de morphing é movido manualmente."""
        self.morph_t = float(val) / 100.0
        self._apply_current_matrix_to_canvas()

    def reset_morph(self):
        """Reseta o slider de morphing para t=0 (identidade)."""
        self.morph_var.set(0.0)
        self.morph_t = 0.0
        self._apply_current_matrix_to_canvas()

    def toggle_animation(self):
        """Alterna entre iniciar e pausar a animação de morphing."""
        if self.is_animating:
            self.is_animating = False
            self.btn_play.config(text="▶ Animar")
            self.last_anim_time = None
        else:
            self.is_animating = True
            self.btn_play.config(text="⏸ Pausar")
            if self.morph_var.get() >= 100.0:
                self.morph_var.set(0.0)
            self.last_anim_time = time.perf_counter()
            self._step_animation()

    def _step_animation(self):
        """Avança um quadro da animação usando delta-time real."""
        if not self.is_animating:
            return

        # Calcular delta-time desde o último quadro
        now = time.perf_counter()
        dt = now - self.last_anim_time if self.last_anim_time else 0.016
        self.last_anim_time = now

        # Velocidade: ~50 unidades por segundo (100% em ~2 segundos)
        speed = 50.0
        current_val = self.morph_var.get()
        next_val = current_val + speed * dt

        if next_val >= 100.0:
            next_val = 100.0
            self.is_animating = False
            self.btn_play.config(text="▶ Animar")
            self.last_anim_time = None

        self.morph_var.set(next_val)
        self.morph_t = next_val / 100.0
        self._apply_current_matrix_to_canvas()

        if self.is_animating:
            # Agendar próximo quadro (~60 FPS)
            self.anim_job = self.scroll_content.after(16, self._step_animation)
