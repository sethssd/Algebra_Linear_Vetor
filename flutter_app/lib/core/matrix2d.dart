/// core/matrix2d.dart
/// Classe utilitária para transformações lineares 2D.
/// Portado de core/matrix.py — sem dependência de NumPy, usa List<List<double>>.
import 'dart:math';

/// Alias semântico para ponto 2D.
typedef Vec2 = ({double x, double y});

class Matrix2D {
  // ------------------------------------------------------------------ //
  //  Matriz identidade
  // ------------------------------------------------------------------ //

  static List<List<double>> identity() => [
        [1.0, 0.0],
        [0.0, 1.0],
      ];

  // ------------------------------------------------------------------ //
  //  Multiplicação A · B
  // ------------------------------------------------------------------ //

  static List<List<double>> multiply(
      List<List<double>> a, List<List<double>> b) {
    return [
      [
        a[0][0] * b[0][0] + a[0][1] * b[1][0],
        a[0][0] * b[0][1] + a[0][1] * b[1][1],
      ],
      [
        a[1][0] * b[0][0] + a[1][1] * b[1][0],
        a[1][0] * b[0][1] + a[1][1] * b[1][1],
      ],
    ];
  }

  // ------------------------------------------------------------------ //
  //  Transformar um ponto
  // ------------------------------------------------------------------ //

  static Vec2 transformPoint(List<List<double>> mat, Vec2 point) {
    final nx = mat[0][0] * point.x + mat[0][1] * point.y;
    final ny = mat[1][0] * point.x + mat[1][1] * point.y;
    return (x: nx, y: ny);
  }

  // ------------------------------------------------------------------ //
  //  Inversa 2×2
  // ------------------------------------------------------------------ //

  static List<List<double>>? inverse(List<List<double>> mat) {
    final det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0];
    if (det.abs() < 1e-10) return null; // singular
    final invDet = 1.0 / det;
    return [
      [mat[1][1] * invDet, -mat[0][1] * invDet],
      [-mat[1][0] * invDet, mat[0][0] * invDet],
    ];
  }

  // ------------------------------------------------------------------ //
  //  Interpolação linear entre duas matrizes
  // ------------------------------------------------------------------ //

  static List<List<double>> interpolate(
      List<List<double>> start, List<List<double>> end, double t) {
    return [
      [
        start[0][0] * (1 - t) + end[0][0] * t,
        start[0][1] * (1 - t) + end[0][1] * t,
      ],
      [
        start[1][0] * (1 - t) + end[1][0] * t,
        start[1][1] * (1 - t) + end[1][1] * t,
      ],
    ];
  }

  // ------------------------------------------------------------------ //
  //  Verificação se é identidade
  // ------------------------------------------------------------------ //

  static bool isIdentity(List<List<double>> mat, {double tol = 1e-4}) {
    return (mat[0][0] - 1.0).abs() < tol &&
        mat[0][1].abs() < tol &&
        mat[1][0].abs() < tol &&
        (mat[1][1] - 1.0).abs() < tol;
  }

  // ------------------------------------------------------------------ //
  //  Fábricas de matrizes de transformação
  // ------------------------------------------------------------------ //

  static List<List<double>> rotation(double angleDeg) {
    final rad = angleDeg * pi / 180.0;
    final c = cos(rad);
    final s = sin(rad);
    return [
      [c, -s],
      [s, c],
    ];
  }

  static List<List<double>> scaling(double sx, double sy) => [
        [sx, 0.0],
        [0.0, sy],
      ];

  static List<List<double>> reflectX() => [
        [1.0, 0.0],
        [0.0, -1.0],
      ];

  static List<List<double>> reflectY() => [
        [-1.0, 0.0],
        [0.0, 1.0],
      ];

  static List<List<double>> reflectYX() => [
        [0.0, 1.0],
        [1.0, 0.0],
      ];

  // ------------------------------------------------------------------ //
  //  Ordenação angular de pontos
  // ------------------------------------------------------------------ //

  static List<Vec2> sortPointsAngularly(List<Vec2> points) {
    if (points.isEmpty) return [];
    final cx = points.map((p) => p.x).reduce((a, b) => a + b) / points.length;
    final cy = points.map((p) => p.y).reduce((a, b) => a + b) / points.length;
    final sorted = List<Vec2>.from(points);
    sorted.sort((a, b) {
      final aa = atan2(a.y - cy, a.x - cx);
      final ab = atan2(b.y - cy, b.x - cx);
      return aa.compareTo(ab);
    });
    return sorted;
  }
}
