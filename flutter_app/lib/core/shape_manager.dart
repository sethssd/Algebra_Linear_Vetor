/// core/shape_manager.dart
import 'dart:math';
import 'package:flutter/material.dart';
import 'matrix2d.dart';
import '../theme.dart';

class Point2D {
  double x;
  double y;
  String label;
  Color color;

  Point2D(this.x, this.y, {this.label = '', this.color = const Color(0xFFff79c6)});

  Point2D clone() => Point2D(x, y, label: label, color: color);
}

class ShapeStateSnapshot {
  final List<Point2D> basePoints;
  final List<List<List<double>>> matrixStack;
  final List<String> matrixNamesStack;
  final String shapeName;
  final int? pointLimit;

  ShapeStateSnapshot({
    required this.basePoints,
    required this.matrixStack,
    required this.matrixNamesStack,
    required this.shapeName,
    this.pointLimit,
  });
}

class ShapeManager extends ChangeNotifier {
  final List<Point2D> basePoints = [];
  final List<List<List<double>>> matrixStack = [];
  final List<String> matrixNamesStack = [];
  final List<ShapeStateSnapshot> _history = [];
  String shapeName = 'Quadrado Unitário';
  int? pointLimit;

  ShapeManager() {
    // Não usar _saveState aqui, carregar a figura inicial
    _loadPresetShapeInternal('Quadrado Unitário');
  }

  // ------------------------------------------------------------------ //
  //  Histórico de Estado Completo
  // ------------------------------------------------------------------ //

  void _saveState() {
    _history.add(ShapeStateSnapshot(
      basePoints: basePoints.map((p) => p.clone()).toList(),
      matrixStack: matrixStack.map((m) => m.map((row) => List<double>.from(row)).toList()).toList(),
      matrixNamesStack: List<String>.from(matrixNamesStack),
      shapeName: shapeName,
      pointLimit: pointLimit,
    ));
  }

  bool get canUndo => _history.isNotEmpty;

  int get historyCount => _history.length;

  bool popHistory() {
    if (_history.isNotEmpty) {
      final state = _history.removeLast();
      basePoints.clear();
      basePoints.addAll(state.basePoints);
      matrixStack.clear();
      matrixStack.addAll(state.matrixStack);
      matrixNamesStack.clear();
      matrixNamesStack.addAll(state.matrixNamesStack);
      shapeName = state.shapeName;
      pointLimit = state.pointLimit;
      notifyListeners();
      return true;
    }
    return false;
  }

  void resetHistory() {
    _saveState();
    matrixStack.clear();
    matrixNamesStack.clear();
    notifyListeners();
  }

  bool restoreInitialState() {
    if (matrixStack.isEmpty && _history.isEmpty) return false;
    _saveState();
    matrixStack.clear();
    matrixNamesStack.clear();
    notifyListeners();
    return true;
  }

  // ------------------------------------------------------------------ //
  //  Pontos calculados e Matrizes
  // ------------------------------------------------------------------ //

  List<List<double>> getTotalMatrix(List<List<double>> currentM) {
    var mTotal = Matrix2D.identity();
    for (final m in matrixStack) {
      mTotal = Matrix2D.multiply(m, mTotal);
    }
    return Matrix2D.multiply(currentM, mTotal);
  }

  List<Point2D> get points {
    var mTotal = Matrix2D.identity();
    for (final m in matrixStack) {
      mTotal = Matrix2D.multiply(m, mTotal);
    }
    return basePoints.map((pt) {
      final p = Matrix2D.transformPoint(mTotal, (x: pt.x, y: pt.y));
      return Point2D(p.x, p.y, label: pt.label, color: pt.color);
    }).toList();
  }

  List<Point2D> getTransformedPoints(List<List<double>> currentM) {
    final mTotal = getTotalMatrix(currentM);
    return basePoints.map((pt) {
      final p = Matrix2D.transformPoint(mTotal, (x: pt.x, y: pt.y));
      return Point2D(p.x, p.y, label: pt.label, color: pt.color);
    }).toList();
  }

  void applyTransformation(List<List<double>> m, String name) {
    if (!Matrix2D.isIdentity(m)) {
      _saveState();
      matrixStack.add(m);
      matrixNamesStack.add(name);
      notifyListeners();
    }
  }

  // ------------------------------------------------------------------ //
  //  Figuras e Pontos
  // ------------------------------------------------------------------ //

  void _loadPresetShapeInternal(String name) {
    shapeName = name;
    pointLimit = null;
    basePoints.clear();
    matrixStack.clear();

    List<List<double>> pts;

    switch (name) {
      case 'Quadrado Unitário':
        pts = [[0, 0], [2, 0], [2, 2], [0, 2]];
      case 'Triângulo':
        pts = [[0, 0], [3, 0], [1.5, 2.5]];
      case 'Casa':
        pts = [[0, 0], [2, 0], [2, 2], [1, 3.2], [0, 2]];
      case 'Estrela':
        pts = [
          [0, 3], [0.8, 1], [3, 0.8], [1.2, -0.6],
          [1.8, -2.8], [0, -1.5], [-1.8, -2.8], [-1.2, -0.6],
          [-3, 0.8], [-0.8, 1],
        ];
      case 'Losango':
        pts = [[0, 2], [2, 0], [0, -2], [-2, 0]];
      default:
        pts = [];
    }

    final colors = darkColors.vertexPalette; // fallback, color depends on theme usually
    for (var i = 0; i < pts.length; i++) {
      basePoints.add(Point2D(
        pts[i][0],
        pts[i][1],
        label: 'P${i + 1}',
        color: colors[i % colors.length],
      ));
    }
  }

  void loadPresetShape(String name) {
    _saveState();
    _loadPresetShapeInternal(name);
    notifyListeners();
  }

  void startCustomShape(int limit) {
    _saveState();
    shapeName = 'Figura Personalizada';
    pointLimit = limit;
    basePoints.clear();
    matrixStack.clear();
    notifyListeners();
  }

  bool addPoint(double x, double y, {String? label, Color? color}) {
    if (pointLimit != null && basePoints.length >= pointLimit!) {
      return false; // Limit reached
    }
    _saveState();
    final lbl = label ?? 'P${basePoints.length + 1}';
    final col = color ?? darkColors.vertexPalette[basePoints.length % darkColors.vertexPalette.length];
    basePoints.add(Point2D(x, y, label: lbl, color: col));
    notifyListeners();
    return true;
  }

  void removePoint(int index) {
    if (index >= 0 && index < basePoints.length) {
      _saveState();
      basePoints.removeAt(index);
      _relabelSequential();
      notifyListeners();
    }
  }

  void clearAll() {
    _saveState();
    basePoints.clear();
    notifyListeners();
  }

  void sortPointsAngularly() {
    if (basePoints.length < 3) return;
    _saveState();
    final cx = basePoints.map((p) => p.x).reduce((a, b) => a + b) / basePoints.length;
    final cy = basePoints.map((p) => p.y).reduce((a, b) => a + b) / basePoints.length;
    basePoints.sort((a, b) {
      final aa = atan2(a.y - cy, a.x - cx);
      final ab = atan2(b.y - cy, b.x - cx);
      return aa.compareTo(ab);
    });
    _relabelSequential();
    notifyListeners();
  }

  void _relabelSequential() {
    for (var i = 0; i < basePoints.length; i++) {
      if (basePoints[i].label.startsWith('P')) {
        basePoints[i].label = 'P${i + 1}';
      }
    }
  }
}
