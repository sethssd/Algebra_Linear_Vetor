"""
core/matrix.py
--------------
Operações de matriz 2x2 e geração de transformações lineares 2D.
"""

import math


class Matrix2D:
    """Classe utilitária para transformações matriciais 2D."""

    @staticmethod
    def identity():
        return [[1.0, 0.0], [0.0, 1.0]]

    @staticmethod
    def rotation(angle_degrees):
        rad = math.radians(angle_degrees)
        c, s = math.cos(rad), math.sin(rad)
        return [[c, -s], [s, c]]

    @staticmethod
    def scaling(sx, sy):
        return [[float(sx), 0.0], [0.0, float(sy)]]

    @staticmethod
    def shear_x(kx):
        return [[1.0, float(kx)], [0.0, 1.0]]

    @staticmethod
    def shear_y(ky):
        return [[1.0, 0.0], [float(ky), 1.0]]

    @staticmethod
    def reflect_x():
        return [[1.0, 0.0], [0.0, -1.0]]

    @staticmethod
    def reflect_y():
        return [[-1.0, 0.0], [0.0, 1.0]]

    @staticmethod
    def reflect_yx():
        return [[0.0, 1.0], [1.0, 0.0]]

    @staticmethod
    def project_x():
        return [[1.0, 0.0], [0.0, 0.0]]

    @staticmethod
    def project_y():
        return [[0.0, 0.0], [0.0, 1.0]]

    @staticmethod
    def transform_point(M, x, y):
        """Multiplica matriz M 2x2 pelo ponto (x, y)."""
        nx = M[0][0] * x + M[0][1] * y
        ny = M[1][0] * x + M[1][1] * y
        return nx, ny

    @staticmethod
    def interpolate(M_target, t):
        """Interpolador temporal M(t) = (1-t)*I + t*M_target (t entre 0.0 e 1.0)."""
        t = max(0.0, min(1.0, float(t)))
        M_start = Matrix2D.identity()
        return [
            [(1.0 - t) * M_start[0][0] + t * M_target[0][0], (1.0 - t) * M_start[0][1] + t * M_target[0][1]],
            [(1.0 - t) * M_start[1][0] + t * M_target[1][0], (1.0 - t) * M_start[1][1] + t * M_target[1][1]]
        ]
