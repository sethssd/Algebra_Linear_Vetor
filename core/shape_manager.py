"""
core/shape_manager.py
---------------------
Gerenciador de formas geométricas para o Transformador Linear 2D.
Mantém a lista de pontos e aplica transformações matriciais via Matrix2D.
"""

import math
from core.matrix import Matrix2D


class Point2D:
    """Representa um ponto ou vetor 2D com rótulo e cor."""

    def __init__(self, x, y, label="", color="#ff79c6"):
        self.x = float(x)
        self.y = float(y)
        self.label = label
        self.color = color

    def to_tuple(self):
        """Retorna as coordenadas como tupla (x, y)."""
        return (self.x, self.y)


class ShapeManager:
    """Gerencia a lista de pontos que formam a figura geométrica."""

    def __init__(self):
        self.points = []
        self.shape_name = "Quadrado Unitário"
        self.load_preset_shape("Quadrado Unitário")

    # ------------------------------------------------------------------ #
    #  Figuras predefinidas
    # ------------------------------------------------------------------ #

    def load_preset_shape(self, shape_name):
        """Carrega uma figura predefinida pelo nome, substituindo os pontos atuais."""
        self.shape_name = shape_name
        self.points.clear()

        if shape_name == "Quadrado Unitário":
            pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
        elif shape_name == "Triângulo":
            pts = [(0.0, 0.0), (3.0, 0.0), (1.5, 2.5)]
        elif shape_name == "Casa":
            pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (1.0, 3.2), (0.0, 2.0)]
        elif shape_name == "Estrela":
            pts = [
                (0.0, 3.0), (0.8, 1.0), (3.0, 0.8), (1.2, -0.6),
                (1.8, -2.8), (0.0, -1.5), (-1.8, -2.8), (-1.2, -0.6),
                (-3.0, 0.8), (-0.8, 1.0),
            ]
        elif shape_name == "Losango":
            pts = [(0.0, 2.0), (2.0, 0.0), (0.0, -2.0), (-2.0, 0.0)]
        else:
            pts = []

        # Paleta de cores para os vértices
        colors = ["#ff79c6", "#ffb86c", "#bd93f9", "#50fa7b", "#8be9fd", "#f1fa8c"]
        for idx, (x, y) in enumerate(pts):
            lbl = f"P{idx + 1}"
            col = colors[idx % len(colors)]
            self.points.append(Point2D(x, y, lbl, col))

    # ------------------------------------------------------------------ #
    #  Manipulação de pontos
    # ------------------------------------------------------------------ #

    def add_point(self, x, y, label="", color="#00f2fe"):
        """Adiciona um novo ponto à lista. Se label estiver vazio, gera automaticamente."""
        if not label:
            label = f"P{len(self.points) + 1}"
        self.points.append(Point2D(x, y, label, color))

    def remove_point(self, index):
        """Remove o ponto no índice fornecido e atualiza os rótulos sequenciais."""
        if 0 <= index < len(self.points):
            self.points.pop(index)
            # Reorganizar os rótulos sequenciais P1, P2, P3...
            for idx, pt in enumerate(self.points):
                if pt.label.startswith("P") and pt.label[1:].isdigit():
                    pt.label = f"P{idx + 1}"

    def clear_all(self):
        """Remove todos os pontos da lista."""
        self.points.clear()

    # ------------------------------------------------------------------ #
    #  Transformação
    # ------------------------------------------------------------------ #

    def get_transformed_points(self, M):
        """Retorna uma lista de tuplas (nx, ny) transformadas pela matriz M.

        M pode ser uma lista de listas, lista plana ou ndarray NumPy 2×2.
        A conversão é feita internamente para garantir compatibilidade.
        """
        transformed = []
        for pt in self.points:
            nx, ny = Matrix2D.transform_point(M, (pt.x, pt.y))
            transformed.append((nx, ny))
        return transformed

    # ------------------------------------------------------------------ #
    #  Ordenação angular dos pontos
    # ------------------------------------------------------------------ #

    def sort_points_angularly(self):
        """Reordena os pontos angularmente em torno do centróide
        para evitar cruzamentos (nós) no polígono e renomeia os rótulos
        em ordem sequencial (P1, P2, P3...) para manter a exibição ordenada na aba.
        """
        if len(self.points) < 3:
            return
        cx = sum(p.x for p in self.points) / len(self.points)
        cy = sum(p.y for p in self.points) / len(self.points)
        self.points.sort(key=lambda p: math.atan2(p.y - cy, p.x - cx))

        # Reatribuir rótulos sequenciais P1, P2, P3... na ordem ordenada
        for idx, pt in enumerate(self.points):
            pt.label = f"P{idx + 1}"
