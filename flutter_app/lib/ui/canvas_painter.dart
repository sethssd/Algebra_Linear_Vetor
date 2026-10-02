/// ui/canvas_painter.dart
import 'dart:math';
import 'package:flutter/material.dart';
import '../core/shape_manager.dart';
import '../theme.dart';

class CartesianPainter extends CustomPainter {
  final ShapeManager shapeManager;
  final List<List<double>> currentMatrix;
  final double zoom;
  final Offset pan;
  final String viewMode;
  final bool showOrigGrid;
  final bool showTransGrid;
  final bool showOrigShape;
  final bool showLabels;
  final AppColors colors;
  final Color shapeFillColor;
  final Color shapeOutlineColor;

  CartesianPainter({
    required this.shapeManager,
    required this.currentMatrix,
    required this.zoom,
    required this.pan,
    this.viewMode = 'Ambos',
    this.showOrigGrid = true,
    this.showTransGrid = false,
    this.showOrigShape = true,
    this.showLabels = true,
    required this.colors,
    required this.shapeFillColor,
    required this.shapeOutlineColor,
  });

  Offset _toScreen(double x, double y, Size size) {
    final cx = size.width / 2 + pan.dx;
    final cy = size.height / 2 + pan.dy;
    return Offset(cx + x * zoom, cy - y * zoom);
  }

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2 + pan.dx;
    final cy = size.height / 2 + pan.dy;

    final minX = ((-cx) / zoom).floor() - 2;
    final maxX = ((size.width - cx) / zoom).ceil() + 2;
    final minY = ((cy - size.height) / zoom).floor() - 2;
    final maxY = (cy / zoom).ceil() + 2;

    if (showOrigGrid) {
      final gridPaint = Paint()
        ..color = colors.gridOrig
        ..strokeWidth = 1;

      final axisPaint = Paint()
        ..color = colors.axis
        ..strokeWidth = 2;

      for (var x = minX; x <= maxX; x++) {
        final p1 = _toScreen(x.toDouble(), minY.toDouble(), size);
        final p2 = _toScreen(x.toDouble(), maxY.toDouble(), size);
        canvas.drawLine(p1, p2, x == 0 ? axisPaint : gridPaint);
      }
      for (var y = minY; y <= maxY; y++) {
        final p1 = _toScreen(minX.toDouble(), y.toDouble(), size);
        final p2 = _toScreen(maxX.toDouble(), y.toDouble(), size);
        canvas.drawLine(p1, p2, y == 0 ? axisPaint : gridPaint);
      }
    }

    if (showTransGrid) {
      final transPaint = Paint()
        ..color = colors.gridTrans
        ..strokeWidth = 1;

      final rMinX = max(-25, minX);
      final rMaxX = min(25, maxX);
      final rMinY = max(-25, minY);
      final rMaxY = min(25, maxY);

      final m = currentMatrix;
      for (var gx = rMinX; gx <= rMaxX; gx++) {
        final tx1 = m[0][0] * gx + m[0][1] * minY;
        final ty1 = m[1][0] * gx + m[1][1] * minY;
        final tx2 = m[0][0] * gx + m[0][1] * maxY;
        final ty2 = m[1][0] * gx + m[1][1] * maxY;
        canvas.drawLine(
            _toScreen(tx1, ty1, size), _toScreen(tx2, ty2, size), transPaint);
      }
      for (var gy = rMinY; gy <= rMaxY; gy++) {
        final tx1 = m[0][0] * minX + m[0][1] * gy;
        final ty1 = m[1][0] * minX + m[1][1] * gy;
        final tx2 = m[0][0] * maxX + m[0][1] * gy;
        final ty2 = m[1][0] * maxX + m[1][1] * gy;
        canvas.drawLine(
            _toScreen(tx1, ty1, size), _toScreen(tx2, ty2, size), transPaint);
      }
    }

    final origin = _toScreen(0, 0, size);
    canvas.drawCircle(origin, 4, Paint()..color = colors.text);

    final pts = shapeManager.points;
    if (pts.isEmpty) return;

    if (showOrigShape && pts.length >= 2) {
      final origPaint = Paint()
        ..color = colors.origShape
        ..strokeWidth = 2
        ..style = PaintingStyle.stroke;

      final path = Path();
      for (var i = 0; i < pts.length; i++) {
        final s = _toScreen(pts[i].x, pts[i].y, size);
        if (i == 0) {
          path.moveTo(s.dx, s.dy);
        } else {
          path.lineTo(s.dx, s.dy);
        }
      }
      if (pts.length >= 3) path.close();
      canvas.drawPath(path, origPaint);
    }

    final transCoords = shapeManager.getTransformedPoints(currentMatrix);

    if ((viewMode == 'Figura' || viewMode == 'Ambos') && transCoords.length >= 2) {
      final fillPaint = Paint()
        ..color = shapeFillColor
        ..style = PaintingStyle.fill;
      final outPaint = Paint()
        ..color = shapeOutlineColor
        ..strokeWidth = 3
        ..style = PaintingStyle.stroke;

      final path = Path();
      for (var i = 0; i < transCoords.length; i++) {
        final s = _toScreen(transCoords[i].x, transCoords[i].y, size);
        if (i == 0) {
          path.moveTo(s.dx, s.dy);
        } else {
          path.lineTo(s.dx, s.dy);
        }
      }
      if (transCoords.length >= 3) path.close();
      canvas.drawPath(path, fillPaint);
      canvas.drawPath(path, outPaint);
    }

    if (viewMode == 'Vetores' || viewMode == 'Ambos') {
      for (final tPt in transCoords) {
        final s = _toScreen(tPt.x, tPt.y, size);
        final dist = (s - origin).distance;
        if (dist >= 2) {
          _drawArrow(canvas, origin, s, tPt.color);
        }
      }
    }

    for (final tPt in transCoords) {
      final s = _toScreen(tPt.x, tPt.y, size);

      canvas.drawCircle(s, 6, Paint()..color = tPt.color);
      canvas.drawCircle(
          s,
          6,
          Paint()
            ..color = Colors.white
            ..style = PaintingStyle.stroke
            ..strokeWidth = 1.5);

      if (showLabels) {
        final tp = TextPainter(
          text: TextSpan(
            text: "${tPt.label}'(${tPt.x.toStringAsFixed(1)}, ${tPt.y.toStringAsFixed(1)})",
            style: TextStyle(
              color: tPt.color,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
          textDirection: TextDirection.ltr,
        );
        tp.layout();
        tp.paint(canvas, Offset(s.dx + 10, s.dy - 16));
      }
    }
  }

  void _drawArrow(Canvas canvas, Offset from, Offset to, Color color) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(from, to, paint);

    final dir = (to - from);
    final len = dir.distance;
    if (len < 1) return;
    final unit = dir / len;
    final perp = Offset(-unit.dy, unit.dx);
    const arrowLen = 12.0;
    const arrowWidth = 5.0;

    final tip = to;
    final left = to - unit * arrowLen + perp * arrowWidth;
    final right = to - unit * arrowLen - perp * arrowWidth;

    final arrowPath = Path()
      ..moveTo(tip.dx, tip.dy)
      ..lineTo(left.dx, left.dy)
      ..lineTo(right.dx, right.dy)
      ..close();
    canvas.drawPath(arrowPath, Paint()..color = color);
  }

  @override
  bool shouldRepaint(CartesianPainter oldDelegate) => true;
}
