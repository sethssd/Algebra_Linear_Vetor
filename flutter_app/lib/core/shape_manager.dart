/// core/shape_manager.dart
///
/// Camada de ESTADO da engine: guarda os vértices da figura, a pilha de
/// transformações aplicadas e o histórico para desfazer (undo).
/// Toda a matemática pesada é delegada a `Matrix2D`; aqui fica o
/// gerenciamento de dados e a notificação da UI.
import 'dart:math';
import 'package:flutter/material.dart';
import 'matrix2d.dart';
import '../theme.dart';

/// Um vértice da figura, com dados matemáticos e visuais.
///
/// Diferente do `Vec2` (apenas coordenadas), o `Point2D` é MUTÁVEL e
/// carrega rótulo e cor para que o canvas possa desenhá-lo.
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
  ///
  /// @param x Coordenada X.
  /// @param y Coordenada Y.
  /// @param label Rótulo opcional (padrão: string vazia).
  /// @param color Cor opcional (padrão: rosa `0xFFff79c6`).
  Point2D(this.x, this.y, {this.label = '', this.color = const Color(0xFFff79c6)});

  /// Cria uma CÓPIA independente do ponto (cópia profunda).
  ///
  /// Essencial para os snapshots do undo: como `Point2D` é mutável, guardar
  /// apenas a referência faria o histórico "mudar junto" com o estado atual.
  ///
  /// @return Novo `Point2D` com os mesmos valores.
  Point2D clone() => Point2D(x, y, label: label, color: color);
}

/// Uma "fotografia" imutável do estado completo do `ShapeManager`.
///
/// Padrão *Memento*: cada vez que uma ação destrutiva acontece, uma cópia do
/// estado anterior é empilhada. Desfazer = restaurar a última foto.
/// Todos os campos são cópias profundas, isoladas do estado vivo.
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
  ///
  /// @param basePoints Vértices originais clonados.
  /// @param matrixStack Pilha de matrizes clonada.
  /// @param matrixNamesStack Nomes das transformações.
  /// @param shapeName Nome da figura.
  /// @param pointLimit Limite de pontos (opcional).
  ShapeStateSnapshot({
    required this.basePoints,
    required this.matrixStack,
    required this.matrixNamesStack,
    required this.shapeName,
    this.pointLimit,
  });
}

/// Gerenciador central da figura e das transformações lineares.
///
/// ## Modelo de dados (ideia-chave)
///
/// * `basePoints` guarda os vértices ORIGINAIS e nunca é alterado por
///   transformações. As coordenadas exibidas são SEMPRE recalculadas a
///   partir dele, o que evita acúmulo de erro de ponto flutuante.
/// * `matrixStack` guarda cada transformação aplicada, na ordem
///   cronológica (índice 0 = a primeira).
/// * A matriz total é `M_n · ... · M_2 · M_1` e o ponto final é
///   `p_final = M_total · p_base`.
///
/// Estende `ChangeNotifier`: ao chamar `notifyListeners()`, a UI Flutter
/// que escuta este objeto é reconstruída automaticamente.
class ShapeManager extends ChangeNotifier {
  /// Vértices originais da figura (antes das transformações).
  final List<Point2D> basePoints = [];

  /// Pilha de matrizes 2×2 aplicadas, da mais antiga para a mais recente.
  final List<List<List<double>>> matrixStack = [];

  /// Nomes legíveis das transformações; `matrixNamesStack[i]` descreve
  /// `matrixStack[i]`. Mantidas sempre com o mesmo tamanho.
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

  // ------------------------------------------------------------------ //
  //  Histórico de Estado Completo
  // ------------------------------------------------------------------ //

  /// Tira uma foto (snapshot) do estado atual e a empilha no histórico.
  ///
  /// Deve ser chamado ANTES de qualquer mudança que o usuário possa querer
  /// desfazer. Cada coleção é copiada em PROFUNDIDADE; sem isso, o snapshot
  /// compartilharia referências e seria alterado junto com o estado vivo.
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
  ///
  /// @return `true` se algo foi restaurado; `false` se o histórico está vazio.
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
  ///
  /// O estado anterior é salvo antes de limpar, então a ação continua
  /// podendo ser desfeita.
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
  ///
  /// @return `false` se não havia nada a restaurar (nenhuma transformação e
  /// nenhum histórico); `true` se o reset foi realizado.
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

  // ------------------------------------------------------------------ //
  //  Pontos calculados e Matrizes
  // ------------------------------------------------------------------ //

  /// Calcula a matriz total = matriz "em edição" × todas as já aplicadas.
  ///
  /// Matematicamente, para a pilha `[M1, M2, ..., Mn]` e a matriz atual `C`:
  ///
  /// ```text
  ///   M_total = C · Mn · ... · M2 · M1
  /// ```
  ///
  /// A transformação MAIS RECENTE fica sempre à ESQUERDA, pois os pontos
  /// são vetores coluna (`p' = M · p`): o que é aplicado por último é
  /// multiplicado por último pela esquerda.
  ///
  /// @param currentM Matriz atual (ex.: pré-visualização ainda não aplicada
  /// pelo usuário). Passe a identidade para ignorá-la.
  /// @return Matriz 2×2 única equivalente a toda a cadeia de transformações.
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
  /// qualquer matriz em pré-visualização.
  ///
  /// Cada ponto é calculado como `p' = M_total · p_base`.
  ///
  /// @return Nova lista de `Point2D` transformados (`basePoints` não muda).
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
  ///
  /// Usado para mostrar em tempo real o efeito de uma transformação (ex.:
  /// um slider de rotação) ANTES de ela ser confirmada na pilha.
  ///
  /// @param currentM Matriz em edição, aplicada por último.
  /// @return Nova lista de `Point2D` com `p' = (C · M_total) · p_base`.
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
  ///
  /// Matrizes equivalentes à identidade são ignoradas, pois não alteram a
  /// figura e só poluiriam o histórico.
  ///
  /// @param m Matriz 2×2 da transformação.
  /// @param name Nome legível exibido na UI (ex.: "Rotação 45°").
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

  // ------------------------------------------------------------------ //
  //  Figuras e Pontos
  // ------------------------------------------------------------------ //

  /// Carrega uma figura pré-definida SEM salvar histórico nem notificar.
  ///
  /// Versão "interna" usada pelo construtor (quando não há UI escutando) e
  /// por `loadPresetShape` (que cuida do snapshot e da notificação).
  ///
  /// @param name Nome da figura (ex.: 'Triângulo', 'Casa', 'Estrela').
  /// Nomes desconhecidos resultam em uma figura vazia.
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
  ///
  /// @param name Nome da figura pré-definida.
  void loadPresetShape(String name) {
    // 1) Salva o estado atual para poder voltar à figura anterior.
    _saveState();
    // 2) Substitui o conteúdo (também zera as transformações).
    _loadPresetShapeInternal(name);
    // 3) Notifica a UI.
    notifyListeners();
  }

  /// Inicia o modo de figura personalizada, vazia, com limite de vértices.
  ///
  /// @param limit Quantidade máxima de pontos que o usuário poderá adicionar.
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
  ///
  /// @param x Coordenada X do novo ponto (no espaço da figura ORIGINAL).
  /// @param y Coordenada Y do novo ponto.
  /// @param label Rótulo opcional (padrão: `P<n>`).
  /// @param color Cor opcional (padrão: próxima cor da paleta).
  /// @return `true` se o ponto foi adicionado; `false` se o limite foi atingido.
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
  ///
  /// @param index Posição (base 0) do ponto em `basePoints`. Índices
  /// inválidos são ignorados em silêncio.
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
  ///
  /// Versão in-place (altera `basePoints`) do algoritmo de
  /// `Matrix2D.sortPointsAngularly`. Ajuda a formar um polígono sem
  /// arestas cruzadas quando os pontos foram clicados fora de ordem.
  /// Exige pelo menos 3 pontos (o mínimo para formar um polígono).
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
  ///
  /// Só renomeia rótulos que começam com 'P' (os automáticos), preservando
  /// nomes personalizados pelo usuário.
  void _relabelSequential() {
    for (var i = 0; i < basePoints.length; i++) {
      // Apenas rótulos automáticos são reescritos.
      if (basePoints[i].label.startsWith('P')) {
        basePoints[i].label = 'P${i + 1}';
      }
    }
  }
}
