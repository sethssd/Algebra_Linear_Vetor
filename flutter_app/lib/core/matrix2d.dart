/// core/matrix2d.dart
/// Classe utilitária para transformações lineares 2D.
/// Portado de core/matrix.py — sem dependência de NumPy, usa List<List<double>>.
///
/// ## Convenções adotadas por toda a engine
///
/// 1. **Representação de matriz:** uma matriz 2×2 é uma lista de duas linhas,
///    onde cada linha é uma lista de dois `double`. Ou seja, `m[linha][coluna]`:
///
/// ```text
///        col0    col1
///   [ m[0][0]  m[0][1] ]   <- linha 0
///   [ m[1][0]  m[1][1] ]   <- linha 1
/// ```
///
/// 2. **Representação de ponto:** um ponto é um *vetor coluna* `[x, y]ᵀ`.
///    A transformação é aplicada pela ESQUERDA do vetor: `p' = M · p`.
///
/// 3. **Composição:** se aplicamos primeiro `A` e depois `B`, a matriz
///    equivalente é `B · A` (a transformação mais recente fica à esquerda).
///    Isso acontece porque `B · (A · p) = (B · A) · p` (associatividade).
///
/// 4. **Matrizes 2×2 só representam transformações LINEARES:** rotação,
///    escala, reflexão e cisalhamento em torno da ORIGEM. Translações não
///    são lineares e, por isso, não existem nesta classe.
import 'dart:math';

/// Alias semântico para ponto 2D.
///
/// Usa um *record* nomeado do Dart 3: `(x: 1.0, y: 2.0)`.
/// É imutável e leve, ideal para cálculos matemáticos temporários
/// (diferente de `Point2D`, que carrega rótulo e cor para a UI).
typedef Vec2 = ({double x, double y});

/// Conjunto de funções estáticas para álgebra linear 2×2.
///
/// Todas as funções são *puras*: não modificam seus argumentos e sempre
/// devolvem novas listas/valores. Isso é o que torna seguro armazenar
/// matrizes em pilhas e snapshots (ver `ShapeManager`).
class Matrix2D {
  // ------------------------------------------------------------------ //
  //  Matriz identidade
  // ------------------------------------------------------------------ //

  /// Retorna a matriz identidade 2×2.
  ///
  /// A identidade é o elemento neutro da multiplicação de matrizes:
  /// `I · A = A · I = A`, e `I · p = p` (não move nenhum ponto).
  /// É usada como valor inicial ao acumular uma sequência de transformações.
  ///
  /// ```text
  ///   I = [ 1  0 ]
  ///       [ 0  1 ]
  /// ```
  ///
  /// @return Uma NOVA matriz identidade a cada chamada (evita que dois
  /// trechos do código compartilhem e alterem sem querer a mesma lista).
  static List<List<double>> identity() => [
        [1.0, 0.0],
        [0.0, 1.0],
      ];

  // ------------------------------------------------------------------ //
  //  Multiplicação A · B
  // ------------------------------------------------------------------ //

  /// Multiplica duas matrizes 2×2, calculando `A · B`.
  ///
  /// Regra **Linha × Coluna**: o elemento `C[i][j]` é o produto escalar
  /// (dot product) da linha `i` de A pela coluna `j` de B:
  ///
  /// ```text
  ///   [ a00 a01 ]   [ b00 b01 ]   [ a00·b00 + a01·b10   a00·b01 + a01·b11 ]
  ///   [ a10 a11 ] · [ b10 b11 ] = [ a10·b00 + a11·b10   a10·b01 + a11·b11 ]
  /// ```
  ///
  /// ATENÇÃO: a multiplicação de matrizes NÃO é comutativa (`A·B ≠ B·A`).
  /// A ordem define qual transformação é aplicada primeiro: em `A · B · p`,
  /// o vetor `p` sofre `B` primeiro e depois `A`.
  ///
  /// @param a Matriz da esquerda (transformação aplicada DEPOIS).
  /// @param b Matriz da direita (transformação aplicada ANTES).
  /// @return Nova matriz 2×2 equivalente a aplicar `b` e em seguida `a`.
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

  // ------------------------------------------------------------------ //
  //  Transformar um ponto
  // ------------------------------------------------------------------ //

  /// Aplica a transformação linear `mat` a um ponto, calculando `p' = M · p`.
  ///
  /// É o caso particular da multiplicação de matrizes onde a segunda
  /// matriz é um vetor coluna 2×1:
  ///
  /// ```text
  ///   [ m00 m01 ]   [ x ]   [ m00·x + m01·y ]   [ x' ]
  ///   [ m10 m11 ] · [ y ] = [ m10·x + m11·y ] = [ y' ]
  /// ```
  ///
  /// Geometricamente, as COLUNAS da matriz dizem para onde vão os vetores
  /// da base: coluna 0 = destino de (1,0); coluna 1 = destino de (0,1).
  ///
  /// @param mat Matriz 2×2 da transformação.
  /// @param point Ponto original (record com `x` e `y`).
  /// @return Novo ponto com as coordenadas transformadas.
  static Vec2 transformPoint(List<List<double>> mat, Vec2 point) {
    // 1) Nova coordenada X: produto escalar da LINHA 0 da matriz por (x, y).
    final nx = mat[0][0] * point.x + mat[0][1] * point.y;
    // 2) Nova coordenada Y: produto escalar da LINHA 1 da matriz por (x, y).
    final ny = mat[1][0] * point.x + mat[1][1] * point.y;
    // 3) Empacota o resultado em um novo record (o ponto original não muda).
    return (x: nx, y: ny);
  }

  // ------------------------------------------------------------------ //
  //  Inversa 2×2
  // ------------------------------------------------------------------ //

  /// Calcula a matriz inversa `M⁻¹` de uma matriz 2×2, se ela existir.
  ///
  /// A inversa "desfaz" a transformação: `M⁻¹ · M = I`. Para 2×2 existe
  /// uma fórmula fechada baseada no determinante `det = ad - bc`:
  ///
  /// ```text
  ///   M = [ a  b ]      M⁻¹ = (1/det) · [  d  -b ]
  ///       [ c  d ]                      [ -c   a ]
  /// ```
  ///
  /// Se `det = 0` a matriz é *singular*: ela colapsa o plano em uma reta
  /// ou em um ponto (perde informação), portanto não há como desfazê-la.
  ///
  /// @param mat Matriz 2×2 a ser invertida.
  /// @return A matriz inversa, ou `null` se a matriz for singular.
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

  // ------------------------------------------------------------------ //
  //  Interpolação linear entre duas matrizes
  // ------------------------------------------------------------------ //

  /// Interpola linearmente (LERP) elemento a elemento entre duas matrizes.
  ///
  /// Fórmula aplicada a cada elemento: `R = start·(1 - t) + end·t`.
  ///
  /// ```text
  ///   t = 0.0  ->  resultado = start
  ///   t = 0.5  ->  média entre start e end
  ///   t = 1.0  ->  resultado = end
  /// ```
  ///
  /// Útil para ANIMAR uma transformação: variando `t` de 0 a 1 a figura
  /// "desliza" da posição inicial até a final.
  ///
  /// Observação: o LERP direto de matrizes de rotação NÃO mantém uma
  /// rotação perfeita no meio do caminho (a figura pode encolher
  /// levemente), pois a interpolação ocorre nos elementos e não no ângulo.
  ///
  /// @param start Matriz inicial (em t = 0).
  /// @param end Matriz final (em t = 1).
  /// @param t Fator de progresso, normalmente entre 0.0 e 1.0.
  /// @return Nova matriz 2×2 interpolada.
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

  // ------------------------------------------------------------------ //
  //  Verificação se é identidade
  // ------------------------------------------------------------------ //

  /// Verifica se uma matriz é (aproximadamente) a identidade.
  ///
  /// Compara com a matriz alvo:
  ///
  /// ```text
  ///   [ 1  0 ]
  ///   [ 0  1 ]
  /// ```
  ///
  /// Usa tolerância porque, em ponto flutuante, valores como `0.99999999`
  /// devem ser tratados como `1.0`. Serve para ignorar transformações que
  /// não fazem nada (ex.: rotação de 0° ou escala 1×1).
  ///
  /// @param mat Matriz 2×2 a ser testada.
  /// @param tol Tolerância máxima aceita por elemento (padrão `1e-4`).
  /// @return `true` se todos os elementos estiverem dentro da tolerância.
  static bool isIdentity(List<List<double>> mat, {double tol = 1e-4}) {
    // Diagonal principal deve estar perto de 1; fora da diagonal, perto de 0.
    return (mat[0][0] - 1.0).abs() < tol &&
        mat[0][1].abs() < tol &&
        mat[1][0].abs() < tol &&
        (mat[1][1] - 1.0).abs() < tol;
  }

  // ------------------------------------------------------------------ //
  //  Fábricas de matrizes de transformação
  // ------------------------------------------------------------------ //

  /// Cria a matriz de rotação anti-horária em torno da origem.
  ///
  /// ```text
  ///   R(θ) = [ cosθ  -sinθ ]
  ///          [ sinθ   cosθ ]
  /// ```
  ///
  /// Dedução: a coluna 0 é o destino de (1,0) = (cosθ, sinθ) e a coluna 1
  /// é o destino de (0,1) = (-sinθ, cosθ). Rotações preservam distâncias e
  /// ângulos (matriz ortogonal, det = 1).
  ///
  /// Nota: com o eixo Y apontando para cima, θ positivo gira no sentido
  /// anti-horário. Em telas (Y para baixo) o sentido visual se inverte.
  ///
  /// @param angleDeg Ângulo de rotação em GRAUS.
  /// @return Matriz de rotação 2×2.
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
  ///
  /// ```text
  ///   S(sx, sy) = [ sx  0  ]
  ///               [ 0   sy ]
  /// ```
  ///
  /// Multiplica X por `sx` e Y por `sy`. Valores > 1 ampliam, entre 0 e 1
  /// reduzem, e negativos também refletem. O determinante é `sx·sy`
  /// (fator de variação da área da figura).
  ///
  /// @param sx Fator de escala no eixo X.
  /// @param sy Fator de escala no eixo Y.
  /// @return Matriz de escala 2×2 (diagonal).
  static List<List<double>> scaling(double sx, double sy) => [
        [sx, 0.0],
        [0.0, sy],
      ];

  /// Cria a matriz de reflexão em relação ao eixo X (espelha verticalmente).
  ///
  /// ```text
  ///   Fx = [ 1   0 ]      (x, y) -> (x, -y)
  ///        [ 0  -1 ]
  /// ```
  ///
  /// Mantém X e inverte o sinal de Y. Determinante = -1 (inverte a
  /// orientação: horário vira anti-horário).
  ///
  /// @return Matriz de reflexão 2×2 sobre o eixo X.
  static List<List<double>> reflectX() => [
        [1.0, 0.0],
        [0.0, -1.0],
      ];

  /// Cria a matriz de reflexão em relação ao eixo Y (espelha horizontalmente).
  ///
  /// ```text
  ///   Fy = [ -1  0 ]      (x, y) -> (-x, y)
  ///        [  0  1 ]
  /// ```
  ///
  /// Inverte o sinal de X e mantém Y. Determinante = -1.
  ///
  /// @return Matriz de reflexão 2×2 sobre o eixo Y.
  static List<List<double>> reflectY() => [
        [-1.0, 0.0],
        [0.0, 1.0],
      ];

  /// Cria a matriz de reflexão em relação à reta `y = x` (diagonal).
  ///
  /// ```text
  ///   Fyx = [ 0  1 ]      (x, y) -> (y, x)
  ///         [ 1  0 ]
  /// ```
  ///
  /// Troca as coordenadas X e Y entre si (equivale a transpor o ponto).
  /// Determinante = -1.
  ///
  /// @return Matriz de reflexão 2×2 sobre a reta y = x.
  static List<List<double>> reflectYX() => [
        [0.0, 1.0],
        [1.0, 0.0],
      ];

  // ------------------------------------------------------------------ //
  //  Ordenação angular de pontos
  // ------------------------------------------------------------------ //

  /// Ordena pontos pelo ângulo polar em torno do seu centroide.
  ///
  /// Serve para que, ao ligar os pontos NA ORDEM da lista, o polígono
  /// resultante contorne a figura sem se cruzar (válido para polígonos
  /// convexos ou "estrelados" em relação ao centro).
  ///
  /// @param points Lista de pontos em qualquer ordem (não é modificada).
  /// @return Nova lista ordenada por ângulo crescente (de -π a π), ou lista
  /// vazia se a entrada for vazia.
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
