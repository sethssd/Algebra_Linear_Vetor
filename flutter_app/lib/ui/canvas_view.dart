/// ui/canvas_view.dart
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import '../core/matrix2d.dart';
import '../core/shape_manager.dart';
import '../theme.dart';
import 'canvas_painter.dart';

class CanvasView extends StatefulWidget {
  final ShapeManager shapeManager;
  final List<List<double>> currentMatrix;
  final String viewMode;
  final bool showOrigGrid;
  final bool showTransGrid;
  final bool showOrigShape;
  final bool showLabels;
  final Color shapeFillColor;
  final Color shapeOutlineColor;
  final VoidCallback? onPointAdded;

  const CanvasView({
    super.key,
    required this.shapeManager,
    required this.currentMatrix,
    this.viewMode = 'Ambos',
    this.showOrigGrid = true,
    this.showTransGrid = false,
    this.showOrigShape = true,
    this.showLabels = true,
    required this.shapeFillColor,
    required this.shapeOutlineColor,
    this.onPointAdded,
  });

  @override
  State<CanvasView> createState() => _CanvasViewState();
}

class _CanvasViewState extends State<CanvasView> {
  final GlobalKey _paintKey = GlobalKey();
  double _zoom = 50.0;
  Offset _pan = Offset.zero;
  Offset? _lastFocal;

  Offset _toWorld(Offset screenPoint, Size size) {
    final cx = size.width / 2 + _pan.dx;
    final cy = size.height / 2 + _pan.dy;
    final tx = (screenPoint.dx - cx) / _zoom;
    final ty = (cy - screenPoint.dy) / _zoom;

    // Inverter a matriz TOTAL para obter a coordenada exata de base
    final totalM = widget.shapeManager.getTotalMatrix(widget.currentMatrix);
    final inv = Matrix2D.inverse(totalM);
    if (inv != null) {
      final ox = inv[0][0] * tx + inv[0][1] * ty;
      final oy = inv[1][0] * tx + inv[1][1] * ty;
      return Offset(
        (ox * 10).roundToDouble() / 10,
        (oy * 10).roundToDouble() / 10,
      );
    }
    // Caso a matriz seja singular (ex: projeção), não tem inversa exata
    return Offset(
      (tx * 10).roundToDouble() / 10,
      (ty * 10).roundToDouble() / 10,
    );
  }

  void _onScaleStart(ScaleStartDetails details) {
    _lastFocal = details.localFocalPoint;
  }

  void _onScaleUpdate(ScaleUpdateDetails details) {
    setState(() {
      if (_lastFocal != null) {
        final delta = details.localFocalPoint - _lastFocal!;
        _pan += delta;
      }
      _lastFocal = details.localFocalPoint;

      if (details.scale != 1.0) {
        final newZoom = (_zoom * details.scale).clamp(8.0, 400.0);
        _zoom = newZoom;
      }
    });
  }

  void _onPointerSignal(PointerSignalEvent event) {
    if (event is PointerScrollEvent) {
      setState(() {
        final factor = event.scrollDelta.dy < 0 ? 1.1 : 0.9;
        final newZoom = (_zoom * factor).clamp(8.0, 400.0);
        _zoom = newZoom;
      });
    }
  }

  @override
  void didUpdateWidget(covariant CanvasView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.currentMatrix != oldWidget.currentMatrix || widget.shapeManager.basePoints.length != oldWidget.shapeManager.basePoints.length) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _checkAndFitBounds();
      });
    }
  }

  void _checkAndFitBounds() {
    if (!mounted) return;
    final box = _paintKey.currentContext?.findRenderObject() as RenderBox?;
    if (box == null) return;
    final size = box.size;

    final pts = widget.shapeManager.getTransformedPoints(widget.currentMatrix);
    if (pts.isEmpty) return;

    double minX = pts[0].x;
    double maxX = pts[0].x;
    double minY = pts[0].y;
    double maxY = pts[0].y;

    for (final p in pts) {
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }

    final cx = size.width / 2 + _pan.dx;
    final cy = size.height / 2 + _pan.dy;

    final sMinX = cx + minX * _zoom;
    final sMaxX = cx + maxX * _zoom;
    final sMinY = cy - maxY * _zoom; 
    final sMaxY = cy - minY * _zoom;

    // Se estiver fora da tela ou ocupando mais que a tela
    if (sMinX < 40 || sMaxX > size.width - 40 || sMinY < 40 || sMaxY > size.height - 40) {
      final centerX = (minX + maxX) / 2;
      final centerY = (minY + maxY) / 2;
      final width = (maxX - minX).abs();
      final height = (maxY - minY).abs();

      final targetWidth = width < 10.0 ? 10.0 : width * 1.5; 
      final targetHeight = height < 10.0 ? 10.0 : height * 1.5;

      final zoomX = size.width / targetWidth;
      final zoomY = size.height / targetHeight;

      double newZoom = zoomX < zoomY ? zoomX : zoomY;
      newZoom = newZoom.clamp(8.0, 400.0);

      final newPan = Offset(-centerX * newZoom, centerY * newZoom);

      setState(() {
        _zoom = newZoom;
        _pan = newPan;
      });
    }
  }

  void _onDoubleTap(TapDownDetails details) {
    final box = _paintKey.currentContext?.findRenderObject() as RenderBox?;
    if (box == null) return;
    
    final size = box.size;
    final localPos = box.globalToLocal(details.globalPosition);
    final world = _toWorld(localPos, size);

    final success = widget.shapeManager.addPoint(
      world.dx,
      world.dy,
    );
    
    if (success) {
      widget.onPointAdded?.call();
    } else {
      _showLimitDialog();
    }
  }

  void _showLimitDialog() async {
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Theme.of(context).cardColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        title: Text('Limite Atingido', style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color)),
        content: Text(
          'Você atingiu o limite de ${widget.shapeManager.pointLimit} pontos selecionado.',
          style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, 'ok'),
            child: const Text('OK'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, 'infinito'),
            child: const Text('Limite Infinito'),
          ),
        ],
      ),
    );

    if (result == 'infinito') {
      widget.shapeManager.pointLimit = null;
    }
  }

  void _resetView() {
    setState(() {
      _zoom = 50.0;
      _pan = Offset.zero;
    });
  }

  void _zoomIn() {
    setState(() {
      _zoom = (_zoom * 1.2).clamp(8.0, 400.0);
    });
  }

  void _zoomOut() {
    setState(() {
      _zoom = (_zoom * 0.8).clamp(8.0, 400.0);
    });
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;

    return Column(
      children: [
        // Barra de ferramentas limpa (sem emojis)
        Container(
          height: 40,
          decoration: BoxDecoration(
            color: colors.card,
            border: Border(bottom: BorderSide(color: colors.border, width: 1)),
          ),
          child: Row(
            children: [
              _toolbarButton(Icons.center_focus_strong, 'Centralizar', _resetView, colors),
              _toolbarDivider(colors),
              _toolbarButton(Icons.add, '', _zoomIn, colors),
              _toolbarButton(Icons.remove, '', _zoomOut, colors),
              _toolbarDivider(colors),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Text(
                    'Duplo clique para adicionar ponto  ·  Arrastar para mover  ·  Scroll para zoom',
                    style: TextStyle(color: colors.subtext, fontSize: 10),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
            ],
          ),
        ),
        // Canvas principal
        Expanded(
          child: Listener(
            onPointerSignal: _onPointerSignal,
            child: GestureDetector(
              onScaleStart: _onScaleStart,
              onScaleUpdate: _onScaleUpdate,
              onDoubleTapDown: _onDoubleTap,
              child: ClipRect(
                child: CustomPaint(
                  key: _paintKey,
                  painter: CartesianPainter(
                    shapeManager: widget.shapeManager,
                    currentMatrix: widget.currentMatrix,
                    zoom: _zoom,
                    pan: _pan,
                    viewMode: widget.viewMode,
                    showOrigGrid: widget.showOrigGrid,
                    showTransGrid: widget.showTransGrid,
                    showOrigShape: widget.showOrigShape,
                    showLabels: widget.showLabels,
                    colors: colors,
                    shapeFillColor: widget.shapeFillColor,
                    shapeOutlineColor: widget.shapeOutlineColor,
                  ),
                  size: Size.infinite,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _toolbarButton(IconData icon, String text, VoidCallback onTap, AppColors colors) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10),
        child: Center(
          child: Row(
            children: [
              Icon(icon, size: 14, color: colors.subtext),
              if (text.isNotEmpty) ...[
                const SizedBox(width: 4),
                Text(text, style: TextStyle(color: colors.subtext, fontSize: 12)),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _toolbarDivider(AppColors colors) {
    return Container(width: 1, height: 20, color: colors.border);
  }
}
