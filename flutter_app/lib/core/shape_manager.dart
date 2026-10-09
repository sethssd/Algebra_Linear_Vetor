/// core/shape_manager.dart
import 'dart:math';
import 'package:flutter/material.dart';
import 'matrix2d.dart';
import '../theme.dart';

/// Um vértice da figura, com dados matemáticos e visuais.
class Point2D {
  /// Coordenada X (abscissa) no plano cartesiano.
  double x;

  /// Coordenada Y (ordenada) no plano cartesiano.
  double y;

  /// Nome exibido junto ao ponto (ex.: "P1", "P2").
  String label;

  /// Cor usada para desenhar o ponto na tela.
  Color color;

  /// Cria um ponto.
  Point2D(this.x, this.y, {this.label = '', this.color = const Color(0xFFff79c6)});

  /// Cria uma CÓPIA independente do ponto (cópia profunda).
  Point2D clone() => Point2D(x, y, label: label, color: color);
}

/// Uma "fotografia" imutável do estado completo do `ShapeManager`.
class ShapeStateSnapshot {
  /// Cópia dos vértices originais (antes de qualquer matriz).
  final List<Point2D> basePoints;

  /// Cópia da pilha de matrizes de transformação aplicadas.
  final List<List<List<double>>> matrixStack;

  /// Cópia dos nomes das transformações (paralela a `matrixStack`).
  final List<String> matrixNamesStack;

  /// Nome da figura no momento da captura.
  final String shapeName;

  /// Limite de pontos da figura personalizada (`null` = sem limite).
  final int? pointLimit;

  /// Cria um snapshot com todos os dados já copiados.
  ShapeStateSnapshot({
    required this.basePoints,
    required this.matrixStack,
    required this.matrixNamesStack,
    required this.shapeName,
    this.pointLimit,
  });
}

/// Gerenciador central da figura e das transformações lineares.
class ShapeManager extends ChangeNotifier {
  /// Vértices originais da figura (antes das transformações).
  final List<Point2D> basePoints = [];

  /// Pilha de matrizes 2×2 aplicadas, da mais antiga para a mais recente.
  final List<List<List<double>>> matrixStack = [];

  /// Nomes legíveis das transformações; `matrixNamesStack[i]` descreve
  final List<String> matrixNamesStack = [];

  /// Pilha de snapshots usada pelo sistema de undo (último = mais recente).
  final List<ShapeStateSnapshot> _history = [];

  /// Nome da figura atual.
  String shapeName = 'Quadrado Unitário';

  /// Máximo de pontos permitido (`null` = ilimitado).
  int? pointLimit;

  /// Inicializa o gerenciador carregando a figura padrão.
  ShapeManager() {
    // Não usar _saveState aqui, carregar a figura inicial
    // (o histórico deve começar vazio: não há estado anterior para desfazer).
    _loadPresetShapeInternal('Quadrado Unitário');
  }

  //  Histórico de Estado Completo

  /// Tira uma foto (snapshot) do estado atual e a empilha no histórico.
  void _saveState() {
    _history.add(ShapeStateSnapshot(
      // 1) Clona cada ponto individualmente (Point2D é mutável).
      basePoints: basePoints.map((p) => p.clone()).toList(),
      // 2) Cópia de 3 níveis: pilha -> matriz -> linha. Cada linha vira uma
      //    nova lista, então nenhuma matriz é compartilhada com o original.
      matrixStack: matrixStack.map((m) => m.map((row) => List<double>.from(row)).toList()).toList(),
      // 3) Strings são imutáveis; basta copiar a lista que as contém.
      matrixNamesStack: List<String>.from(matrixNamesStack),
      // 4) Valores simples (String e int?) são copiados por valor.
      shapeName: shapeName,
      pointLimit: pointLimit,
    ));
  }

  /// Indica se existe algum snapshot disponível para desfazer.
  bool get canUndo => _history.isNotEmpty;

  /// Quantidade de snapshots guardados no histórico.
  int get historyCount => _history.length;

  /// Desfaz a última ação restaurando o snapshot mais recente (UNDO).
  bool popHistory() {
    // 1) Sem histórico não há o que desfazer.
    if (_history.isNotEmpty) {
      // 2) Remove (pop) o snapshot mais recente da pilha.
      final state = _history.removeLast();
      // 3) Restaura cada coleção. Usa clear() + addAll() para manter as
      //    MESMAS instâncias de lista (são `final`, e outros objetos podem
      //    estar com referência a elas) apenas trocando o conteúdo.
      basePoints.clear();
      basePoints.addAll(state.basePoints);
      matrixStack.clear();
      matrixStack.addAll(state.matrixStack);
      matrixNamesStack.clear();
      matrixNamesStack.addAll(state.matrixNamesStack);
      // 4) Restaura os valores simples.
      shapeName = state.shapeName;
      pointLimit = state.pointLimit;
      // 5) Avisa a UI para redesenhar com o estado restaurado.
      notifyListeners();
      return true;
    }
    return false;
  }

  /// Descarta todas as transformações aplicadas, voltando à figura base.
  void resetHistory() {
    // 1) Salva o estado atual para permitir desfazer este reset.
    _saveState();
    // 2) Esvazia a pilha: matriz total vira a identidade (figura original).
    matrixStack.clear();
    matrixNamesStack.clear();
    // 3) Notifica a UI.
    notifyListeners();
  }

  /// Restaura a figura ao estado inicial (sem transformações).
  bool restoreInitialState() {
    // 1) Nada a fazer se a figura já está intacta e não há histórico.
    if (matrixStack.isEmpty && _history.isEmpty) return false;
    // 2) Salva o estado para que o reset também possa ser desfeito.
    _saveState();
    // 3) Limpa as transformações; basePoints permanece intacto.
    matrixStack.clear();
    matrixNamesStack.clear();
    notifyListeners();
    return true;
  }

  //  Pontos calculados e Matrizes

  /// Calcula a matriz total = matriz "em edição" × todas as já aplicadas.
  List<List<double>> getTotalMatrix(List<List<double>> currentM) {
    // 1) Começa com a identidade (elemento neutro da multiplicação).
    var mTotal = Matrix2D.identity();
    // 2) Percorre a pilha da mais antiga (M1) para a mais nova (Mn).
    for (final m in matrixStack) {
      // 3) multiply(m, mTotal) => m · mTotal. Colocar a matriz nova à
      //    ESQUERDA do acumulado garante a ordem de aplicação correta
      //    (a mais antiga é a primeira a atuar sobre o ponto).
      mTotal = Matrix2D.multiply(m, mTotal);
    }
    // 4) Aplica por último a matriz atual (também à esquerda).
    return Matrix2D.multiply(currentM, mTotal);
  }

  /// Pontos da figura com as transformações JÁ APLICADAS (pilha), sem
  List<Point2D> get points {
    // 1) Acumula a matriz total da pilha (mesmo algoritmo de getTotalMatrix,
    //    porém sem matriz extra em edição).
    var mTotal = Matrix2D.identity();
    for (final m in matrixStack) {
      mTotal = Matrix2D.multiply(m, mTotal);
    }
    // 2) Transforma cada vértice ORIGINAL com a mesma matriz total.
    return basePoints.map((pt) {
      final p = Matrix2D.transformPoint(mTotal, (x: pt.x, y: pt.y));
      // 3) Recria o Point2D preservando rótulo e cor (só as coordenadas mudam).
      return Point2D(p.x, p.y, label: pt.label, color: pt.color);
    }).toList();
  }

  /// Pontos transformados incluindo uma matriz atual (pré-visualização).
  List<Point2D> getTransformedPoints(List<List<double>> currentM) {
    // 1) Combina a pilha e a matriz atual em UMA única matriz 2×2.
    //    Multiplicar uma vez e depois aplicar a todos os pontos é mais
    //    barato do que aplicar cada matriz a cada ponto separadamente.
    final mTotal = getTotalMatrix(currentM);
    // 2) Aplica a matriz total a cada vértice ORIGINAL (nunca ao já
    //    transformado), evitando acumular erros de arredondamento.
    return basePoints.map((pt) {
      final p = Matrix2D.transformPoint(mTotal, (x: pt.x, y: pt.y));
      // 3) Preserva metadados visuais (rótulo e cor).
      return Point2D(p.x, p.y, label: pt.label, color: pt.color);
    }).toList();
  }

  /// Confirma uma transformação, empilhando-a na pilha de matrizes.
  void applyTransformation(List<List<double>> m, String name) {
    // 1) Ignora transformações "nulas" (nada mudaria visualmente).
    if (!Matrix2D.isIdentity(m)) {
      // 2) Salva o estado ANTES de modificar, para permitir undo.
      _saveState();
      // 3) Empilha matriz e nome em paralelo (mesmo índice nas duas listas).
      matrixStack.add(m);
      matrixNamesStack.add(name);
      // 4) Avisa a UI.
      notifyListeners();
    }
  }

  //  Figuras e Pontos

  /// Carrega uma figura pré-definida SEM salvar histórico nem notificar.
  void _loadPresetShapeInternal(String name) {
    // 1) Reseta o estado básico: nome, sem limite, sem pontos e sem
    //    transformações aplicadas.
    shapeName = name;
    pointLimit = null;
    basePoints.clear();
    matrixStack.clear();

    // `pts` guarda pares [x, y] em coordenadas cartesianas.
    List<List<double>> pts;

    // 2) Escolhe os vértices conforme o nome. A ordem dos pontos define
    //    como o polígono é desenhado (liga cada ponto ao próximo).
    switch (name) {
      case 'Quadrado Unitário':
        // Quadrado de lado 2, canto inferior esquerdo na origem.
        pts = [[0, 0], [2, 0], [2, 2], [0, 2]];
      case 'Triângulo':
        pts = [[0, 0], [3, 0], [1.5, 2.5]];
      case 'Casa':
        // Base quadrada (2×2) com telhado em (1, 3.2).
        pts = [[0, 0], [2, 0], [2, 2], [1, 3.2], [0, 2]];
      case 'Estrela':
        // 10 vértices, alternando pontas externas e vértices internos,
        // centrada na origem.
        pts = [
          [0, 3], [0.8, 1], [3, 0.8], [1.2, -0.6],
          [1.8, -2.8], [0, -1.5], [-1.8, -2.8], [-1.2, -0.6],
          [-3, 0.8], [-0.8, 1],
        ];
      case 'Losango':
        // Quadrado girado 45°, com vértices sobre os eixos.
        pts = [[0, 2], [2, 0], [0, -2], [-2, 0]];
      default:
        pts = [];
    }

    // 3) Paleta de cores dos vértices.
    final colors = darkColors.vertexPalette; // fallback, color depends on theme usually
    // 4) Converte cada par [x, y] em um Point2D rotulado (P1, P2, ...) com
    //    cor cíclica (o `%` reinicia a paleta se houver mais pontos que cores).
    for (var i = 0; i < pts.length; i++) {
      basePoints.add(Point2D(
        pts[i][0],
        pts[i][1],
        label: 'P${i + 1}',
        color: colors[i % colors.length],
      ));
    }
  }

  /// Carrega uma figura pré-definida, com suporte a undo e notificação da UI.
  void loadPresetShape(String name) {
    // 1) Salva o estado atual para poder voltar à figura anterior.
    _saveState();
    // 2) Substitui o conteúdo (também zera as transformações).
    _loadPresetShapeInternal(name);
    // 3) Notifica a UI.
    notifyListeners();
  }

  /// Inicia o modo de figura personalizada, vazia, com limite de vértices.
  void startCustomShape(int limit) {
    // 1) Salva o estado anterior (undo).
    _saveState();
    // 2) Configura a nova figura vazia e o limite de pontos.
    shapeName = 'Figura Personalizada';
    pointLimit = limit;
    // 3) Limpa pontos e transformações da figura anterior.
    basePoints.clear();
    matrixStack.clear();
    notifyListeners();
  }

  /// Adiciona um vértice à figura base.
  bool addPoint(double x, double y, {String? label, Color? color}) {
    // 1) Guarda: se há limite e ele já foi atingido, recusa o ponto.
    //    (`!` é seguro, pois `pointLimit != null` foi verificado antes.)
    if (pointLimit != null && basePoints.length >= pointLimit!) {
      return false; // Limit reached
    }
    // 2) Salva o estado ANTES de modificar (permite desfazer a adição).
    _saveState();
    // 3) Gera o rótulo padrão sequencial, se nenhum foi informado.
    final lbl = label ?? 'P${basePoints.length + 1}';
    // 4) Escolhe a cor, percorrendo a paleta de forma cíclica (módulo).
    final col = color ?? darkColors.vertexPalette[basePoints.length % darkColors.vertexPalette.length];
    // 5) Insere o ponto na lista base (coordenadas ORIGINAIS).
    basePoints.add(Point2D(x, y, label: lbl, color: col));
    // 6) Notifica a UI e sinaliza sucesso.
    notifyListeners();
    return true;
  }

  /// Remove o vértice da posição indicada e renumera os rótulos.
  void removePoint(int index) {
    // 1) Valida o índice para evitar RangeError.
    if (index >= 0 && index < basePoints.length) {
      // 2) Salva o estado (undo).
      _saveState();
      // 3) Remove o ponto.
      basePoints.removeAt(index);
      // 4) Refaz P1, P2, ... sem "buracos" na numeração.
      _relabelSequential();
      notifyListeners();
    }
  }

  /// Remove todos os pontos da figura (a ação pode ser desfeita).
  void clearAll() {
    _saveState();
    basePoints.clear();
    notifyListeners();
  }

  /// Reordena os pontos pelo ângulo polar em torno do centroide.
  void sortPointsAngularly() {
    // 1) Com menos de 3 pontos não há polígono: nada a ordenar.
    if (basePoints.length < 3) return;
    // 2) Salva o estado (undo).
    _saveState();
    // 3) Centroide = média das coordenadas (centro geométrico dos vértices).
    final cx = basePoints.map((p) => p.x).reduce((a, b) => a + b) / basePoints.length;
    final cy = basePoints.map((p) => p.y).reduce((a, b) => a + b) / basePoints.length;
    // 4) Ordena por ângulo crescente do vetor (centroide -> ponto).
    basePoints.sort((a, b) {
      // atan2(dy, dx) retorna o ângulo no intervalo (-π, π], respeitando
      // o quadrante de cada ponto.
      final aa = atan2(a.y - cy, a.x - cx);
      final ab = atan2(b.y - cy, b.x - cx);
      return aa.compareTo(ab);
    });
    // 5) Os rótulos devem acompanhar a nova ordem (P1, P2, ...).
    _relabelSequential();
    notifyListeners();
  }

  /// Renumera os rótulos automáticos para P1, P2, P3... segundo a posição.
  void _relabelSequential() {
    for (var i = 0; i < basePoints.length; i++) {
      // Apenas rótulos automáticos são reescritos.
      if (basePoints[i].label.startsWith('P')) {
        basePoints[i].label = 'P${i + 1}';
      }
    }
  }
}
