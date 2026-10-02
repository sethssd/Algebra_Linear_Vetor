"""
core/matrix.py
--------------
Classe utilitária para transformações lineares 2D utilizando NumPy
para desempenho e clareza.
"""

import numpy as np
import math
from typing import List, Tuple

# Alias de tipo para legibilidade
Vector = Tuple[float, float]
Matrix = np.ndarray  # Matriz NumPy 2×2


class Matrix2D:
    """Auxiliar estático para operações matriciais 2D comuns.

    Todos os métodos aceitam ou retornam tuplas/listas Python para manter
    a API pública compatível com o restante do projeto, aproveitando o
    NumPy internamente.
    """

    # ------------------------------------------------------------------ #
    #  Conversores entre lista Python e ndarray NumPy
    # ------------------------------------------------------------------ #

    @staticmethod
    def to_numpy(values) -> Matrix:
        """Converte uma lista (plana ou aninhada) para uma matriz NumPy 2×2.

        Aceita:
          - Lista plana com 4 números em ordem de linha: [a, b, c, d]
          - Lista de listas: [[a, b], [c, d]]
          - ndarray do NumPy (retornado sem cópia se já for 2×2)
        """
        arr = np.asarray(values, dtype=float)
        if arr.shape == (2, 2):
            return arr
        return arr.reshape(2, 2)

    @staticmethod
    def from_numpy(mat: Matrix) -> List[List[float]]:
        """Converte uma matriz NumPy 2×2 para lista de listas Python.
        Retorna no formato [[a, b], [c, d]].
        """
        return mat.tolist()

    # ------------------------------------------------------------------ #
    #  Operações matriciais básicas
    # ------------------------------------------------------------------ #

    @staticmethod
    def multiply(a: Matrix, b: Matrix) -> Matrix:
        """Multiplicação matricial (a · b) usando ``numpy.dot``."""
        return np.dot(a, b)

    @staticmethod
    def transform_point(mat, point: Vector) -> Vector:
        """Aplica uma matriz de transformação 2×2 a um ponto (x, y).

        A matriz é tratada como linear (sem componente de translação).
        Aceita tanto ndarray quanto lista/lista-de-listas.
        """
        # Garantir que a matriz seja um ndarray 2×2
        m = np.asarray(mat, dtype=float)
        if m.shape != (2, 2):
            m = m.reshape(2, 2)
        vec = np.array([point[0], point[1]], dtype=float)
        result = m @ vec
        return float(result[0]), float(result[1])

    @staticmethod
    def inverse(mat: Matrix) -> Matrix:
        """Retorna a inversa de uma matriz 2×2.
        Lança ``np.linalg.LinAlgError`` se a matriz for singular.
        """
        return np.linalg.inv(mat)

    @staticmethod
    def interpolate(start: Matrix, end: Matrix, t: float) -> Matrix:
        """Interpolação linear entre duas matrizes.
        ``t`` deve estar no intervalo fechado ``[0, 1]``.
        """
        return (1 - t) * start + t * end

    # ------------------------------------------------------------------ #
    #  Fábricas de matrizes de transformação
    # ------------------------------------------------------------------ #

    @staticmethod
    def rotation(angle_deg: float) -> Matrix:
        """Cria uma matriz de rotação para *angle_deg* graus."""
        rad = math.radians(angle_deg)
        c, s = math.cos(rad), math.sin(rad)
        return np.array([[c, -s], [s, c]])

    @staticmethod
    def scaling(sx: float, sy: float) -> Matrix:
        """Cria uma matriz de escala."""
        return np.array([[sx, 0.0], [0.0, sy]])

    @staticmethod
    def shear(sx: float, sy: float) -> Matrix:
        """Cria uma matriz de cisalhamento.
        ``sx`` cisalha X por Y, ``sy`` cisalha Y por X.
        """
        return np.array([[1.0, sx], [sy, 1.0]])

    @staticmethod
    def reflection(x_axis: bool = False, y_axis: bool = False) -> Matrix:
        """Matriz de reflexão em relação ao eixo X, eixo Y ou ambos.
        Se ambas as flags forem ``False``, a matriz identidade é retornada.
        """
        mx = -1.0 if x_axis else 1.0
        my = -1.0 if y_axis else 1.0
        return np.array([[mx, 0.0], [0.0, my]])

    # ------------------------------------------------------------------ #
    #  Auxiliares de compatibilidade (usados no código da interface)
    # ------------------------------------------------------------------ #

    @staticmethod
    def identity() -> List[List[float]]:
        """Retorna a matriz identidade 2×2 como lista de listas Python."""
        return [[1.0, 0.0], [0.0, 1.0]]

    @staticmethod
    def is_identity(mat, tol: float = 1e-4) -> bool:
        """Verifica se a matriz 2×2 fornecida é numericamente equivalente à Identidade."""
        try:
            arr = np.asarray(mat, dtype=float).reshape(2, 2)
            return bool(np.allclose(arr, np.eye(2), atol=tol))
        except Exception:
            return False

    @staticmethod
    def shear_x(kx: float) -> Matrix:
        """Cisalhamento ao longo de X (kₓ)."""
        return Matrix2D.shear(kx, 0.0)

    @staticmethod
    def shear_y(ky: float) -> Matrix:
        """Cisalhamento ao longo de Y (kᵧ)."""
        return Matrix2D.shear(0.0, ky)

    @staticmethod
    def reflect_x() -> Matrix:
        """Reflexão em relação ao eixo X."""
        return Matrix2D.reflection(x_axis=True)

    @staticmethod
    def reflect_y() -> Matrix:
        """Reflexão em relação ao eixo Y."""
        return Matrix2D.reflection(y_axis=True)

    @staticmethod
    def reflect_yx() -> Matrix:
        """Reflexão em relação à reta y = x (troca de eixos)."""
        return np.array([[0.0, 1.0], [1.0, 0.0]])

    @staticmethod
    def project_x() -> Matrix:
        """Projeção sobre o eixo X."""
        return np.array([[1.0, 0.0], [0.0, 0.0]])

    @staticmethod
    def project_y() -> Matrix:
        """Projeção sobre o eixo Y."""
        return np.array([[0.0, 0.0], [0.0, 1.0]])

    # ------------------------------------------------------------------ #
    #  Wrappers legados — preservam assinatura antiga da API
    # ------------------------------------------------------------------ #

    @staticmethod
    def multiply_matrices(m1, m2) -> List[List[float]]:
        """Wrapper legado que aceita listas e retorna lista de listas.
        Internamente utiliza NumPy para o cálculo.
        """
        return Matrix2D.from_numpy(
            Matrix2D.multiply(Matrix2D.to_numpy(m1), Matrix2D.to_numpy(m2))
        )

    @staticmethod
    def invert_matrix(values) -> List[List[float]]:
        """Wrapper legado que retorna a inversa como lista de listas.
        ``values`` deve conter exatamente quatro números.
        """
        return Matrix2D.from_numpy(Matrix2D.inverse(Matrix2D.to_numpy(values)))

    @staticmethod
    def interpolate_matrices(start_vals, end_vals, t: float) -> List[List[float]]:
        """Wrapper legado para interpolação retornando lista de listas.
        ``t`` em ``[0, 1]``.
        """
        start = Matrix2D.to_numpy(start_vals)
        end = Matrix2D.to_numpy(end_vals)
        return Matrix2D.from_numpy(Matrix2D.interpolate(start, end, t))

    # ------------------------------------------------------------------ #
    #  Utilitário geométrico
    # ------------------------------------------------------------------ #

    @staticmethod
    def sort_points_angularly(points: List[Vector]) -> List[Vector]:
        """Retorna os pontos ordenados em sentido anti-horário ao redor
        do centróide, utilizando ``atan2`` para robustez.
        """
        if not points:
            return []
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)

        def angle(p: Vector) -> float:
            return math.atan2(p[1] - cy, p[0] - cx)

        return sorted(points, key=angle)
