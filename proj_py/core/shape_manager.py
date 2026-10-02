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

    def clone(self):
        """Retorna uma cópia independente deste ponto."""
        return Point2D(self.x, self.y, self.label, self.color)

    def to_tuple(self):
        """Retorna as coordenadas como tupla (x, y)."""
        return (self.x, self.y)


class ShapeManager:
    """Gerencia a lista de pontos que formam a figura geométrica."""

    def __init__(self):
        self.base_points = []
        self.matrix_stack = []
        self.shape_name = "Quadrado Unitário"
        self.load_preset_shape("Quadrado Unitário")

    @property
    def points(self):
        """Retorna os pontos calculados em tempo real com base na pilha de matrizes."""
        M_total = Matrix2D.identity()
        for M in self.matrix_stack:
            M_total = Matrix2D.multiply(M, M_total)  # Acumulação da transformação

        res = []
        for pt in self.base_points:
            nx, ny = Matrix2D.transform_point(M_total, (pt.x, pt.y))
            res.append(Point2D(nx, ny, pt.label, pt.color))
        return res

    # ------------------------------------------------------------------ #
    #  Histórico de Matrizes (Desfazer)
    # ------------------------------------------------------------------ #

    def push_history(self, shape_color=None, shape_outline=None):
        """Removido para dar lugar ao armazenamento de matrizes apenas."""
        pass

    def apply_transformation(self, M):
        """Adiciona a matriz na pilha em vez de modificar fisicamente os pontos."""
        # Se for a identidade, não precisa salvar
        if not Matrix2D.is_identity(M):
            self.matrix_stack.append(M)

    def pop_history(self):
        """Remove a última matriz da pilha (Desfazer a última transformação)."""
        if self.matrix_stack:
            self.matrix_stack.pop()
            return True # Indica que algo foi desfeito
        return False

    def reset_history(self):
        """Limpa o histórico de matrizes acumuladas."""
        self.matrix_stack.clear()

    def restore_initial_state(self):
        """Restaura o estado inicial da figura (limpa o histórico de matrizes)."""
        self.matrix_stack.clear()
        return True

    def can_undo(self):
        """Retorna True se houver transformações na pilha."""
        return len(self.matrix_stack) > 0

    # ------------------------------------------------------------------ #
    #  Figuras predefinidas
    # ------------------------------------------------------------------ #

    def load_preset_shape(self, shape_name):
        """Carrega uma figura predefinida pelo nome, substituindo os pontos atuais."""
        self.shape_name = shape_name
        self.base_points.clear()
        self.reset_history()

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
            self.base_points.append(Point2D(x, y, lbl, col))

    # ------------------------------------------------------------------ #
    #  Manipulação de pontos
    # ------------------------------------------------------------------ #

    def add_point(self, x, y, label="", color="#00f2fe"):
        """Adiciona um novo ponto aos base_points."""
        if not label:
            label = f"P{len(self.base_points) + 1}"
        self.base_points.append(Point2D(x, y, label, color))

    def remove_point(self, index):
        """Remove o ponto no índice fornecido e atualiza os rótulos sequenciais."""
        if 0 <= index < len(self.base_points):
            self.base_points.pop(index)
            for idx, pt in enumerate(self.base_points):
                if pt.label.startswith("P") and pt.label[1:].isdigit():
                    pt.label = f"P{idx + 1}"

    def clear_all(self):
        """Remove todos os pontos."""
        self.base_points.clear()

    # ------------------------------------------------------------------ #
    #  Transformação Ocular (apenas leitura manual)
    # ------------------------------------------------------------------ #

    def get_transformed_points(self, M):
        """Aplica uma matriz M temporária aos pontos ATUAIS (já transformados pela pilha)."""
        # Obter os pontos com o histórico de matrizes já aplicado
        current_pts = self.points 
        transformed = []
        for pt in current_pts:
            nx, ny = Matrix2D.transform_point(M, (pt.x, pt.y))
            transformed.append(Point2D(nx, ny, pt.label, pt.color))
        return transformed

    # ------------------------------------------------------------------ #
    #  Ordenação angular dos pontos
    # ------------------------------------------------------------------ #

    def sort_points_angularly(self):
        """Reordena os base_points angularmente em torno do centróide."""
        if len(self.base_points) < 3:
            return
        cx = sum(p.x for p in self.base_points) / len(self.base_points)
        cy = sum(p.y for p in self.base_points) / len(self.base_points)
        self.base_points.sort(key=lambda p: math.atan2(p.y - cy, p.x - cx))

        for idx, pt in enumerate(self.base_points):
            pt.label = f"P{idx + 1}"
