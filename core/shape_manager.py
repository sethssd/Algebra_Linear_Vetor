"""
core/shape_manager.py
---------------------
Gerenciamento de pontos, vetores e formas geométricas (polígonos).
"""

from core.matrix import Matrix2D


class Point2D:
    """Representa um ponto ou vetor 2D."""
    def __init__(self, x, y, label="", color="#ff79c6"):
        self.x = float(x)
        self.y = float(y)
        self.label = label
        self.color = color

    def to_tuple(self):
        return (self.x, self.y)


class ShapeManager:
    """Gerencia a lista de pontos que formam a figura geométrica."""
    def __init__(self):
        self.points = []
        self.shape_name = "Quadrado Unitário"
        self.load_preset_shape("Quadrado Unitário")

    def load_preset_shape(self, shape_name):
        """Carrega vértices pré-definidos para formar uma figura geométrica."""
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
                (-3.0, 0.8), (-0.8, 1.0)
            ]
        elif shape_name == "Losango":
            pts = [(0.0, 2.0), (2.0, 0.0), (0.0, -2.0), (-2.0, 0.0)]
        else:
            pts = []  # Personalizada vazia

        colors = ["#ff79c6", "#ffb86c", "#bd93f9", "#50fa7b", "#8be9fd", "#f1fa8c"]
        for idx, (x, y) in enumerate(pts):
            lbl = f"P{idx+1}"
            col = colors[idx % len(colors)]
            self.points.append(Point2D(x, y, lbl, col))

    def add_point(self, x, y, label="", color="#00f2fe"):
        """Adiciona um novo ponto/vértice à figura."""
        if not label:
            label = f"P{len(self.points)+1}"
        self.points.append(Point2D(x, y, label, color))

    def remove_point(self, index):
        """Remove um ponto pelo índice."""
        if 0 <= index < len(self.points):
            self.points.pop(index)

    def clear_all(self):
        """Limpa todos os pontos da figura."""
        self.points.clear()

    def get_transformed_points(self, M):
        """Retorna uma lista de tuplas (nx, ny) com as coordenadas transformadas por M."""
        transformed = []
        for pt in self.points:
            nx, ny = Matrix2D.transform_point(M, pt.x, pt.y)
            transformed.append((nx, ny))
        return transformed

    def sort_points_angularly(self):
        """Reordena os pontos pelo ângulo polar (atan2) em relação ao centróide para formar um polígono limpo sem nós."""
        if len(self.points) < 3:
            return

        import math

        # Calcular Centróide (cx, cy)
        cx = sum(p.x for p in self.points) / len(self.points)
        cy = sum(p.y for p in self.points) / len(self.points)

        # Ordenar os pontos em ordem crescente de ângulo em relação ao centróide
        self.points.sort(key=lambda p: math.atan2(p.y - cy, p.x - cx))
