"""
ui/canvas_view.py
-----------------
Visualizador Canvas interativo para desenhar a grade cartesiana,
figuras geométricas originais e transformadas, e vetores.
"""

import math
import tkinter as tk
from config import DEFAULT_PAN_X, DEFAULT_PAN_Y, DEFAULT_ZOOM, THEME_COLORS


class CanvasView:
    """Gerencia o Canvas Tkinter e a renderização gráfica dos elementos."""

    def __init__(self, parent_frame, shape_manager):
        self.shape_manager = shape_manager

        # Estado da Câmera (zoom e deslocamento)
        self.zoom = DEFAULT_ZOOM
        self.pan_x = DEFAULT_PAN_X
        self.pan_y = DEFAULT_PAN_Y
        self.drag_start = None

        # Opções de Exibição
        self.view_mode = "Ambos"          # "Figura", "Vetores", "Ambos"
        self.show_orig_grid = True        # Grade cartesiana de fundo
        self.show_trans_grid = False      # Grade transformada
        self.show_orig_shape = True       # Contorno da figura original
        self.show_labels = True           # Rótulos com coordenadas

        # Cores Personalizáveis da Figura
        self.shape_color = THEME_COLORS["shape_fill"]
        self.shape_outline = THEME_COLORS["shape_outline"]

        # Componente Canvas do Tkinter
        self.canvas = tk.Canvas(parent_frame, bg=THEME_COLORS["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Callback disparado quando um ponto é adicionado via duplo clique
        self.on_point_added_callback = None
        # Callback disparado quando um estado é salvo no histórico (para atualizar o indicador)
        self.on_state_saved_callback = None

        # Vinculação de eventos do mouse
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_zoom)
        self.canvas.bind("<Button-4>", lambda e: self.change_zoom(1.1))   # Linux scroll up
        self.canvas.bind("<Button-5>", lambda e: self.change_zoom(0.9))   # Linux scroll down

        # Matriz de transformação atual (lista de listas 2×2)
        self.current_matrix = [[1.0, 0.0], [0.0, 1.0]]

    # ------------------------------------------------------------------ #
    #  Conversão de coordenadas
    # ------------------------------------------------------------------ #

    def to_screen(self, x, y):
        """Converte coordenadas do mundo cartesiano para pixels da tela."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx = w / 2.0 + self.pan_x
        cy = h / 2.0 + self.pan_y
        sx = cx + x * self.zoom
        sy = cy - y * self.zoom
        return sx, sy

    def to_world(self, sx, sy):
        """Converte pixels da tela para coordenadas do mundo cartesiano.

        Caso exista uma transformação matricial ativa, inverte a matriz
        para obter o ponto original (pré-transformação).
        """
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx = w / 2.0 + self.pan_x
        cy = h / 2.0 + self.pan_y

        tx = (sx - cx) / self.zoom
        ty = (cy - sy) / self.zoom

        # Inverter a transformação matricial ativa para obter coordenadas originais
        import numpy as np
        M_arr = np.asarray(self.current_matrix).reshape(2, 2)
        det = M_arr[0, 0] * M_arr[1, 1] - M_arr[0, 1] * M_arr[1, 0]
        if abs(det) > 1e-6:
            inv_det = 1.0 / det
            orig_x = inv_det * (M_arr[1, 1] * tx - M_arr[0, 1] * ty)
            orig_y = inv_det * (-M_arr[1, 0] * tx + M_arr[0, 0] * ty)
            return round(float(orig_x), 1), round(float(orig_y), 1)
        else:
            # Matriz singular — usar coordenadas da tela diretamente
            return round(tx, 1), round(ty, 1)

    # ------------------------------------------------------------------ #
    #  Eventos do mouse
    # ------------------------------------------------------------------ #

    def on_double_click(self, event):
        """Adiciona um novo ponto/vértice na posição do duplo clique."""
        wx, wy = self.to_world(event.x, event.y)

        count = len(self.shape_manager.points) + 1
        label = f"P{count}"

        # Paleta de cores rotativa para os pontos
        palette = ["#ff79c6", "#ffb86c", "#bd93f9", "#50fa7b", "#8be9fd", "#f1fa8c"]
        color = palette[count % len(palette)]

        # Salvar estado antes de adicionar o ponto
        # Apenas as transformações matriciais são guardadas no histórico agora.
        if self.on_state_saved_callback:
            self.on_state_saved_callback()

        self.shape_manager.add_point(wx, wy, label, color)

        # Notificar o painel lateral (VectorPanel) sobre o novo ponto
        if self.on_point_added_callback:
            self.on_point_added_callback()

        self.redraw()

    def on_pan_start(self, event):
        """Registra o ponto inicial do arrasto (pan)."""
        self.drag_start = (event.x, event.y)

    def on_pan_drag(self, event):
        """Move a câmera (pan) conforme o arrasto do mouse."""
        if self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.pan_x += dx
            self.pan_y += dy
            self.drag_start = (event.x, event.y)
            self.redraw()

    def on_mouse_zoom(self, event):
        """Aplica zoom usando a roda do mouse."""
        factor = 1.1 if event.delta > 0 else 0.9
        self.change_zoom(factor)

    def change_zoom(self, factor):
        """Altera o nível de zoom por um fator multiplicativo."""
        new_zoom = self.zoom * factor
        if 8.0 <= new_zoom <= 400.0:
            self.zoom = new_zoom
            self.redraw()

    def reset_view(self):
        """Restaura o zoom e o deslocamento da câmera para os valores padrão."""
        self.pan_x = DEFAULT_PAN_X
        self.pan_y = DEFAULT_PAN_Y
        self.zoom = DEFAULT_ZOOM
        self.redraw()

    # ------------------------------------------------------------------ #
    #  Atualização da matriz
    # ------------------------------------------------------------------ #

    def update_matrix(self, M):
        """Atualiza a matriz de transformação corrente e força o redesenho.

        M deve ser uma lista de listas [[a, b], [c, d]].
        """
        self.current_matrix = M
        self.redraw()

    # ------------------------------------------------------------------ #
    #  Desenho principal
    # ------------------------------------------------------------------ #

    def redraw(self):
        """Redesenha todos os elementos: grade, eixos, figura original,
        figura transformada, vetores e rótulos.
        """
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        cx = w / 2.0 + self.pan_x
        cy = h / 2.0 + self.pan_y

        # Limites visíveis em coordenadas do mundo
        min_x = math.floor((-cx) / self.zoom) - 2
        max_x = math.ceil((w - cx) / self.zoom) + 2
        min_y = math.floor((cy - h) / self.zoom) - 2
        max_y = math.ceil(cy / self.zoom) + 2

        # 1. Desenhar Grade Cartesiana Original
        if self.show_orig_grid:
            for x in range(min_x, max_x + 1):
                sx1, sy1 = self.to_screen(x, min_y)
                sx2, sy2 = self.to_screen(x, max_y)
                color = THEME_COLORS["grid_orig"] if x != 0 else THEME_COLORS["axis"]
                width = 1 if x != 0 else 2
                dash = (2, 4) if x != 0 else None
                self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=width, dash=dash)

            for y in range(min_y, max_y + 1):
                sx1, sy1 = self.to_screen(min_x, y)
                sx2, sy2 = self.to_screen(max_x, y)
                color = THEME_COLORS["grid_orig"] if y != 0 else THEME_COLORS["axis"]
                width = 1 if y != 0 else 2
                dash = (2, 4) if y != 0 else None
                self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=width, dash=dash)

        # 2. Desenhar Grade Transformada
        M = self.current_matrix
        if self.show_trans_grid:
            r_x = range(max(-25, min_x), min(25, max_x) + 1)
            r_y = range(max(-25, min_y), min(25, max_y) + 1)

            for gx in r_x:
                # Coordenadas transformadas das linhas verticais da grade
                tx1 = M[0][0] * gx + M[0][1] * min_y
                ty1 = M[1][0] * gx + M[1][1] * min_y
                tx2 = M[0][0] * gx + M[0][1] * max_y
                ty2 = M[1][0] * gx + M[1][1] * max_y
                sx1, sy1 = self.to_screen(tx1, ty1)
                sx2, sy2 = self.to_screen(tx2, ty2)
                self.canvas.create_line(sx1, sy1, sx2, sy2, fill=THEME_COLORS["grid_trans"], width=1)

            for gy in r_y:
                # Coordenadas transformadas das linhas horizontais da grade
                tx1 = M[0][0] * min_x + M[0][1] * gy
                ty1 = M[1][0] * min_x + M[1][1] * gy
                tx2 = M[0][0] * max_x + M[0][1] * gy
                ty2 = M[1][0] * max_x + M[1][1] * gy
                sx1, sy1 = self.to_screen(tx1, ty1)
                sx2, sy2 = self.to_screen(tx2, ty2)
                self.canvas.create_line(sx1, sy1, sx2, sy2, fill=THEME_COLORS["grid_trans"], width=1)

        # 3. Desenhar Ponto de Origem (0, 0)
        sx0, sy0 = self.to_screen(0, 0)
        self.canvas.create_oval(sx0 - 4, sy0 - 4, sx0 + 4, sy0 + 4, fill=THEME_COLORS["text"], outline="")

        points = self.shape_manager.points
        if not points:
            return

        # 4. Desenhar Contorno da Figura Original (tracejado cinza)
        if self.show_orig_shape and len(points) >= 2:
            orig_screen_pts = []
            for pt in points:
                sx, sy = self.to_screen(pt.x, pt.y)
                orig_screen_pts.extend([sx, sy])

            if len(points) >= 3:
                self.canvas.create_polygon(
                    orig_screen_pts, fill="",
                    outline=THEME_COLORS["orig_shape"], width=2, dash=(4, 4),
                )
            else:
                self.canvas.create_line(
                    orig_screen_pts, fill=THEME_COLORS["orig_shape"], width=2, dash=(4, 4),
                )

        # 5. Calcular Pontos Transformados
        trans_coords = self.shape_manager.get_transformed_points(M)

        # 6. Modo "Figura" ou "Ambos": Desenhar Polígono Transformado
        if self.view_mode in ["Figura", "Ambos"] and len(trans_coords) >= 2:
            screen_pts = []
            for t_pt in trans_coords:
                sx, sy = self.to_screen(t_pt.x, t_pt.y)
                screen_pts.extend([sx, sy])

            if len(trans_coords) >= 3:
                self.canvas.create_polygon(
                    screen_pts,
                    fill=self.shape_color,
                    outline=self.shape_outline,
                    width=3,
                    stipple="gray25",
                )
            else:
                # Apenas 2 pontos: desenhar linha
                self.canvas.create_line(screen_pts, fill=self.shape_outline, width=3)

        # 7. Modo "Vetores" ou "Ambos": Desenhar Setas da Origem até cada ponto
        if self.view_mode in ["Vetores", "Ambos"]:
            for t_pt in trans_coords:
                sx, sy = self.to_screen(t_pt.x, t_pt.y)
                dist = math.hypot(sx - sx0, sy - sy0)
                if dist >= 2:
                    self.canvas.create_line(
                        sx0, sy0, sx, sy,
                        fill=t_pt.color, width=3,
                        arrow=tk.LAST, arrowshape=(10, 12, 5),
                    )

        # 8. Desenhar Pontos (bolinhas) e Rótulos com Coordenadas
        for t_pt in trans_coords:
            sx, sy = self.to_screen(t_pt.x, t_pt.y)

            # Bolinha do vértice
            self.canvas.create_oval(
                sx - 5, sy - 5, sx + 5, sy + 5,
                fill=t_pt.color, outline="#ffffff", width=1.5,
            )

            # Rótulo com coordenadas transformadas
            if self.show_labels:
                # O rótulo mostra as coordenadas transformadas em tempo real
                lbl_text = f"{t_pt.label}'({t_pt.x:.1f}, {t_pt.y:.1f})"
                self.canvas.create_text(
                    sx + 10, sy - 10,
                    text=lbl_text,
                    fill=t_pt.color,
                    font=("Segoe UI", 9, "bold"),
                    anchor="w",
                )
