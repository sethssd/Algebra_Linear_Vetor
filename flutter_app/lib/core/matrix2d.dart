/// core/matrix2d.dart
import 'dart:math';

/// Alias semântico para ponto 2D.
typedef Vec2 = ({double x, double y});

/// Conjunto de funções estáticas para álgebra linear 2×2.
class Matrix2D {
  //  Matriz identidade

  /// Retorna a matriz identidade 2×2.
  static List<List<double>> identity() => [
        [1.0, 0.0],
        [0.0, 1.0],
      ];

  //  Multiplicação A · B

  /// Multiplica duas matrizes 2×2, calculando `A · B`.
  static List<List<double>> multiply(
      List<List<double>> a, List<List<double>> b) {
    return [
      // Linha 0 do resultado: linha 0 de A combinada com cada coluna de B.
      [
        // C[0][0] = (linha 0 de A) · (coluna 0 de B)
        a[0][0] * b[0][0] + a[0][1] * b[1][0],
        // C[0][1] = (linha 0 de A) · (coluna 1 de B)
        a[0][0] * b[0][1] + a[0][1] * b[1][1],
      ],
      // Linha 1 do resultado: linha 1 de A combinada com cada coluna de B.
      [
        // C[1][0] = (linha 1 de A) · (coluna 0 de B)
        a[1][0] * b[0][0] + a[1][1] * b[1][0],
        // C[1][1] = (linha 1 de A) · (coluna 1 de B)
        a[1][0] * b[0][1] + a[1][1] * b[1][1],
      ],
    ];
  }

  //  Transformar um ponto

  /// Aplica a transformação linear `mat` a um ponto, calculando `p' = M · p`.
  static Vec2 transformPoint(List<List<double>> mat, Vec2 point) {
    // 1) Nova coordenada X: produto escalar da LINHA 0 da matriz por (x, y).
    final nx = mat[0][0] * point.x + mat[0][1] * point.y;
    // 2) Nova coordenada Y: produto escalar da LINHA 1 da matriz por (x, y).
    final ny = mat[1][0] * point.x + mat[1][1] * point.y;
    // 3) Empacota o resultado em um novo record (o ponto original não muda).
    return (x: nx, y: ny);
  }

  //  Inversa 2×2

  /// Calcula a matriz inversa `M⁻¹` de uma matriz 2×2, se ela existir.
  static List<List<double>>? inverse(List<List<double>> mat) {
    // 1) Determinante: det = a·d - b·c (fator de variação de área).
    final det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0];
    // 2) Compara com tolerância (1e-10) em vez de `== 0`, pois números de
    //    ponto flutuante acumulam erro e raramente dão exatamente zero.
    if (det.abs() < 1e-10) return null; // singular
    // 3) Calcula 1/det uma única vez para reaproveitar nos 4 elementos.
    final invDet = 1.0 / det;
    // 4) Monta a adjunta (troca a diagonal principal, inverte o sinal da
    //    diagonal secundária) e escala por 1/det.
    return [
      [mat[1][1] * invDet, -mat[0][1] * invDet],
      [-mat[1][0] * invDet, mat[0][0] * invDet],
    ];
  }

  //  Interpolação linear entre duas matrizes

  /// Interpola linearmente (LERP) elemento a elemento entre duas matrizes.
  static List<List<double>> interpolate(
      List<List<double>> start, List<List<double>> end, double t) {
    return [
      // Linha 0: mistura ponderada de cada elemento.
      [
        start[0][0] * (1 - t) + end[0][0] * t,
        start[0][1] * (1 - t) + end[0][1] * t,
      ],
      // Linha 1: mesma mistura ponderada.
      [
        start[1][0] * (1 - t) + end[1][0] * t,
        start[1][1] * (1 - t) + end[1][1] * t,
      ],
    ];
  }

  //  Verificação se é identidade

  /// Verifica se uma matriz é (aproximadamente) a identidade.
  static bool isIdentity(List<List<double>> mat, {double tol = 1e-4}) {
    // Diagonal principal deve estar perto de 1; fora da diagonal, perto de 0.
    return (mat[0][0] - 1.0).abs() < tol &&
        mat[0][1].abs() < tol &&
        mat[1][0].abs() < tol &&
        (mat[1][1] - 1.0).abs() < tol;
  }

  //  Fábricas de matrizes de transformação

  /// Cria a matriz de rotação anti-horária em torno da origem.
  static List<List<double>> rotation(double angleDeg) {
    // 1) `cos` e `sin` do Dart trabalham em RADIANOS: converte graus -> rad.
    final rad = angleDeg * pi / 180.0;
    // 2) Calcula cosseno e seno uma vez só e reutiliza na matriz.
    final c = cos(rad);
    final s = sin(rad);
    // 3) Monta R(θ) conforme a fórmula acima.
    return [
      [c, -s],
      [s, c],
    ];
  }

  /// Cria a matriz de escala (alongamento/compressão) em torno da origem.
  static List<List<double>> scaling(double sx, double sy) => [
        [sx, 0.0],
        [0.0, sy],
      ];

  /// Cria a matriz de reflexão em relação ao eixo X (espelha verticalmente).
  static List<List<double>> reflectX() => [
        [1.0, 0.0],
        [0.0, -1.0],
      ];

  /// Cria a matriz de reflexão em relação ao eixo Y (espelha horizontalmente).
  static List<List<double>> reflectY() => [
        [-1.0, 0.0],
        [0.0, 1.0],
      ];

  /// Cria a matriz de reflexão em relação à reta `y = x` (diagonal).
  static List<List<double>> reflectYX() => [
        [0.0, 1.0],
        [1.0, 0.0],
      ];

  //  Ordenação angular de pontos

  /// Ordena pontos pelo ângulo polar em torno do seu centroide.
  static List<Vec2> sortPointsAngularly(List<Vec2> points) {
    // 1) Caso base: sem pontos, não há o que ordenar (evita divisão por 0).
    if (points.isEmpty) return [];
    // 2) Centroide X: média aritmética de todas as coordenadas X.
    final cx = points.map((p) => p.x).reduce((a, b) => a + b) / points.length;
    // 3) Centroide Y: média aritmética de todas as coordenadas Y.
    final cy = points.map((p) => p.y).reduce((a, b) => a + b) / points.length;
    // 4) Copia a lista para não alterar a original recebida.
    final sorted = List<Vec2>.from(points);
    // 5) Ordena comparando o ângulo de cada ponto em relação ao centroide.
    sorted.sort((a, b) {
      // `atan2(dy, dx)` devolve o ângulo (em radianos, de -π a π) do vetor
      // que vai do centroide até o ponto, respeitando o quadrante correto.
      final aa = atan2(a.y - cy, a.x - cx);
      final ab = atan2(b.y - cy, b.x - cx);
      return aa.compareTo(ab);
    });
    return sorted;
  }
}
