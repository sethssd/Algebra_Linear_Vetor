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
from ui.theme import (
    PALETTE as T,
    CardFrame,
    icon_rotate, icon_scale, icon_shear, icon_reflect,
    icon_undo, icon_reset, icon_color, icon_matrix,
    Divider,
)


# Auxiliar para obter cores do tema ativo
def cor_tema(chave: str) -> str:
    """Retorna a cor correspondente à chave no tema atualmente ativo."""
    return get_theme()[chave]


class ControlsPanel:
    """Gerencia o painel lateral de controles de transformações."""

    def __init__(self, parent_frame, canvas_view):
        self.canvas_view = canvas_view
        self.on_transformation_committed_callback = None

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

        # Entradas da matriz manual 2×2
        self.m_a_str = tk.StringVar(value="1.0")
        self.m_b_str = tk.StringVar(value="0.0")
        self.m_c_str = tk.StringVar(value="0.0")
        self.m_d_str = tk.StringVar(value="1.0")

        # Slider de morphing (0 a 100)
        self.morph_var = tk.DoubleVar(value=100.0)

        # Canvas com scrollbar para o painel esquerdo
        left_canvas = tk.Canvas(parent_frame, bg=T["panel"], highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=left_canvas.yview)
        self.scroll_content = tk.Frame(left_canvas, bg=T["panel"])
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

        # Suporte para rolagem da roda do mouse no painel
        left_canvas.bind("<Enter>", lambda e: left_canvas.bind_all("<MouseWheel>",
            lambda ev: left_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
        left_canvas.bind("<Leave>", lambda e: left_canvas.unbind_all("<MouseWheel>"))

        # Construir interface e aplicar preset inicial
        self._build_widgets()
        self.on_preset_change()

    # ------------------------------------------------------------------ #
    #  Construção da interface
    # ------------------------------------------------------------------ #

    def _build_widgets(self):
        """Constrói todas as seções de widgets dentro do painel com scroll."""
        pad_top = 8

        # ---- Seção 1: Presets de Transformação -------------------------
        card1 = CardFrame(self.scroll_content, title="Transformação", icon_fn=icon_rotate)
        card1.pack(fill=tk.X, padx=6, pady=(pad_top, 4))

        presets = [
            "Identidade",
            "Rotação",
            "Escala",
            "Reflexão no Eixo X",
            "Reflexão no Eixo Y",
            "Reflexão na Reta Y = X",
        ]
        cb = ttk.Combobox(card1.body, textvariable=self.preset_var,
                          values=presets, state="readonly")
        cb.pack(fill=tk.X, pady=(0, 6))
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_preset_change())

        # Frame para controles dinâmicos (sliders)
        self.param_frame = tk.Frame(card1.body, bg=T["card"])
        self.param_frame.pack(fill=tk.X)

        # ---- Seção 2: Histórico & Desfazer --------------------------------
        card2 = CardFrame(self.scroll_content, title="Histórico & Desfazer", icon_fn=icon_undo)
        card2.pack(fill=tk.X, padx=6, pady=4)

        # Linha de botões
        row_btns = tk.Frame(card2.body, bg=T["card"])
        row_btns.pack(fill=tk.X, pady=(0, 6))

        self.btn_undo = tk.Label(
            row_btns, text="  ↩  Desfazer  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["card_alt"], fg=T["warn"],
            padx=6, pady=5, relief="flat",
        )
        self.btn_undo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.btn_undo.bind("<Button-1>", lambda e: self.undo_transformation())
        self.btn_undo.bind("<Enter>", lambda e: self.btn_undo.config(bg=T["border"]))
        self.btn_undo.bind("<Leave>", lambda e: self.btn_undo.config(bg=T["card_alt"]))

        self.btn_reset_initial = tk.Label(
            row_btns, text="  ⏮  Restaurar  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["card_alt"], fg=T["danger"],
            padx=6, pady=5, relief="flat",
        )
        self.btn_reset_initial.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        self.btn_reset_initial.bind("<Button-1>", lambda e: self.reset_to_initial())
        self.btn_reset_initial.bind("<Enter>", lambda e: self.btn_reset_initial.config(bg=T["border"]))
        self.btn_reset_initial.bind("<Leave>", lambda e: self.btn_reset_initial.config(bg=T["card_alt"]))

        # Status do histórico
        self.lbl_history_status = tk.Label(
            card2.body,
            text="—  Sem alterações",
            font=("Segoe UI", 8),
            bg=T["card"], fg=T["subtext"],
            anchor="w",
        )
        self.lbl_history_status.pack(fill=tk.X)

        # ---- Seção 3: Matriz de Transformação ----------------------------
        card3 = CardFrame(self.scroll_content, title="Matriz  [M]", icon_fn=icon_matrix)
        card3.pack(fill=tk.X, padx=6, pady=4)

        grid_m = tk.Frame(card3.body, bg=T["card"])
        grid_m.pack(pady=4)

        # Colchetes decorativos e entradas
        tk.Label(grid_m, text="[", font=("Segoe UI", 26, "bold"),
                 bg=T["card"], fg=T["accent"]).grid(row=0, column=0, rowspan=2, padx=(0, 4))

        for row, var in enumerate([self.m_a_str, self.m_b_str]):
            ttk.Entry(grid_m, textvariable=var, width=7,
                      justify="center", state="readonly").grid(row=0, column=row + 1, padx=3, pady=3)
        for row, var in enumerate([self.m_c_str, self.m_d_str]):
            ttk.Entry(grid_m, textvariable=var, width=7,
                      justify="center", state="readonly").grid(row=1, column=row + 1, padx=3, pady=3)

        tk.Label(grid_m, text="]", font=("Segoe UI", 26, "bold"),
                 bg=T["card"], fg=T["accent"]).grid(row=0, column=3, rowspan=2, padx=(4, 0))

        # ---- Seção 4: Cor e Aparência ------------------------------------
        card4 = CardFrame(self.scroll_content, title="Aparência", icon_fn=icon_color)
        card4.pack(fill=tk.X, padx=6, pady=4)

        btn_color = tk.Label(
            card4.body, text="  🎨  Alterar Cor da Figura  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["card_alt"], fg=T["text"],
            padx=8, pady=5, relief="flat",
        )
        btn_color.pack(fill=tk.X, pady=(0, 8))
        btn_color.bind("<Button-1>", lambda e: self.choose_shape_color())
        btn_color.bind("<Enter>", lambda e: btn_color.config(bg=T["border"]))
        btn_color.bind("<Leave>", lambda e: btn_color.config(bg=T["card_alt"]))

        Divider(card4.body, padx=0, pady=2)

        tk.Label(card4.body, text="Progresso da Transformação (t):",
                 font=("Segoe UI", 8), bg=T["card"], fg=T["subtext"]).pack(anchor="w", pady=(4, 0))
        slider_m = ttk.Scale(card4.body, from_=0.0, to=100.0,
                             variable=self.morph_var, command=self.on_morph_slider)
        slider_m.pack(fill=tk.X, pady=4)

        btn_anim_row = tk.Frame(card4.body, bg=T["card"])
        btn_anim_row.pack(fill=tk.X, pady=(0, 2))

        self.btn_play = tk.Label(
            btn_anim_row, text="  ▶  Animar  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["success"], fg="#ffffff",
            padx=8, pady=5, relief="flat",
        )
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.btn_play.bind("<Button-1>", lambda e: self.toggle_animation())
        self.btn_play.bind("<Enter>", lambda e: self.btn_play.config(bg=T["border_glow"]) if "Animar" in self.btn_play["text"] else None)
        self.btn_play.bind("<Leave>", lambda e: self.btn_play.config(bg=T["success"]) if "Animar" in self.btn_play["text"] else None)

        btn_reset_t = tk.Label(
            btn_anim_row, text="  ⏮  t = 0  ",
            font=("Segoe UI", 9), cursor="hand2",
            bg=T["card_alt"], fg=T["subtext"],
            padx=8, pady=5, relief="flat",
        )
        btn_reset_t.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        btn_reset_t.bind("<Button-1>", lambda e: self.reset_morph())
        btn_reset_t.bind("<Enter>", lambda e: btn_reset_t.config(bg=T["border"]))
        btn_reset_t.bind("<Leave>", lambda e: btn_reset_t.config(bg=T["card_alt"]))

        # Espaçamento final
        tk.Frame(self.scroll_content, bg=T["panel"], height=12).pack()

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

    # ------------------------------------------------------------------ #
    #  Seleção de preset
    # ------------------------------------------------------------------ #

    def on_preset_change(self):
        """Chamado quando o preset do combobox é alterado.
        Se houver uma transformação ativa (não-identidade) acumulada na pré-visualização,
        ela é gravada automaticamente nos vetores e no histórico antes de carregar o novo preset.
        """
        identity = Matrix2D.identity()
        M_current = Matrix2D.interpolate_matrices(identity, self.target_matrix, self.morph_t)

        # Se havia uma matriz não-identidade aplicada no preset anterior, acumula automaticamente!
        if not Matrix2D.is_identity(M_current):
            self.canvas_view.shape_manager.apply_transformation(M_current)
            if self.on_transformation_committed_callback:
                self.on_transformation_committed_callback()

            # Resetar parâmetros dinâmicos dos sliders para a nova transformação
            self.angle_str.set("0.0")
            self.scale_x_str.set("1.0")
            self.scale_y_str.set("1.0")
            self.morph_var.set(100.0)
            self.morph_t = 1.0

        preset = self.preset_var.get()
        self._update_dynamic_controls()

        if preset == "Identidade":
            self.target_matrix = Matrix2D.identity()
        elif preset == "Rotação":
            self._on_rotation_changed()
            self._update_undo_button_state()
            return
        elif preset == "Escala":
            self._on_scale_changed()
            self._update_undo_button_state()
            return
        elif preset == "Reflexão no Eixo X":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.reflect_x())
        elif preset == "Reflexão no Eixo Y":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.reflect_y())
        elif preset == "Reflexão na Reta Y = X":
            self.target_matrix = Matrix2D.from_numpy(Matrix2D.reflect_yx())

        self._update_matrix_display()
        self._update_undo_button_state()

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    #  Histórico & Desfazer
    # ------------------------------------------------------------------ #

    def undo_transformation(self):
        """Desfaz UMA alteração por vez (Ctrl+Z) — qualquer tipo de ação.

        Passo 1: se houver pré-visualização ativa no slider/preset, apenas cancela
                 a pré-visualização e retorna (não toca no histórico).
        Passo 2: se não houver pré-visualização ativa, desfaz o último item do
                 histórico (pontos + cores), sem afetar outros itens.
        """
        identity = Matrix2D.identity()
        M_current = Matrix2D.interpolate_matrices(identity, self.target_matrix, self.morph_t)

        # Passo 1 — Cancelar pré-visualização ativa (slider movido, mas ainda não confirmado)
        if not Matrix2D.is_identity(M_current):
            self.preset_var.set("Identidade")
            self.angle_str.set("0.0")
            self.scale_x_str.set("1.0")
            self.scale_y_str.set("1.0")
            self.target_matrix = Matrix2D.identity()
            self.morph_var.set(100.0)
            self.morph_t = 1.0
            self._update_dynamic_controls()
            self._update_matrix_display()
            self._update_undo_button_state()
            return  # Só cancelou o preview — para aqui

        # Passo 2 — Desfazer UM item do histórico (matrizes)
        if self.canvas_view.shape_manager.pop_history():
            if self.on_transformation_committed_callback:
                self.on_transformation_committed_callback()

        self._update_matrix_display()
        self._update_undo_button_state()

    def reset_to_initial(self):
        """Restaura o estado completo inicial do ciclo (sem matrizes)."""
        if self.canvas_view.shape_manager.restore_initial_state():
            self.preset_var.set("Identidade")
            self.angle_str.set("0.0")
            self.scale_x_str.set("1.0")
            self.scale_y_str.set("1.0")
            self.target_matrix = Matrix2D.identity()
            self.morph_var.set(100.0)
            self.morph_t = 1.0
            self._update_dynamic_controls()
            self._update_matrix_display()
            if self.on_transformation_committed_callback:
                self.on_transformation_committed_callback()

        self._update_undo_button_state()

    def _update_undo_button_state(self):
        """Atualiza visual dos botões de desfazer e rótulo explicativo."""
        can_undo = self.canvas_view.shape_manager.can_undo()
        count = len(self.canvas_view.shape_manager.matrix_stack)
        identity = Matrix2D.identity()
        M_current = Matrix2D.interpolate_matrices(identity, self.target_matrix, self.morph_t)
        has_active_preview = not Matrix2D.is_identity(M_current)
        has_anything = can_undo or has_active_preview

        if hasattr(self, 'btn_undo'):
            self.btn_undo.config(
                fg=T["warn"] if has_anything else T["subtext"],
                cursor="hand2" if has_anything else "arrow",
            )

        if hasattr(self, 'btn_reset_initial'):
            self.btn_reset_initial.config(
                fg=T["danger"] if can_undo else T["subtext"],
                cursor="hand2" if can_undo else "arrow",
            )

        if hasattr(self, 'lbl_history_status'):
            if count > 0:
                self.lbl_history_status.config(
                    text=f"●  {count} alteração{'es' if count > 1 else ''} no histórico",
                    fg=T["accent"],
                )
            elif has_active_preview:
                self.lbl_history_status.config(
                    text="●  pré-visualizando...",
                    fg=T["warn"],
                )
            else:
                self.lbl_history_status.config(
                    text="—  sem alterações",
                    fg=T["subtext"],
                )

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
            # Salva estado antes de alterar a cor
            # (A cor agora é separada das matrizes, portanto não é salva na pilha de matrizes)
            self.canvas_view.shape_color = color_code[1]
            self.canvas_view.shape_outline = color_code[1]
            self.canvas_view.redraw()
            self._update_undo_button_state()

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
            self.btn_play.config(text="  ▶  Animar  ", bg=T["success"], fg="#ffffff")
            self.last_anim_time = None
        else:
            self.is_animating = True
            self.btn_play.config(text="  ⏸  Pausar  ", bg=T["warn"], fg="#ffffff")
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
