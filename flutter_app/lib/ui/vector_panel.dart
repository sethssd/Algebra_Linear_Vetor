/// ui/vector_panel.dart
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import '../core/shape_manager.dart';
import '../theme.dart';

class VectorPanel extends StatefulWidget {
  final ShapeManager shapeManager;
  final List<List<double>> currentMatrix;
  final String viewMode;
  final ValueChanged<String> onViewModeChanged;
  final ValueChanged<String> onShapeChanged;
  final bool showOrigGrid;
  final bool showTransGrid;
  final bool showOrigShape;
  final bool showLabels;
  final ValueChanged<bool> onOrigGridChanged;
  final ValueChanged<bool> onTransGridChanged;
  final ValueChanged<bool> onOrigShapeChanged;
  final ValueChanged<bool> onLabelsChanged;

  const VectorPanel({
    super.key,
    required this.shapeManager,
    required this.currentMatrix,
    required this.viewMode,
    required this.onViewModeChanged,
    required this.onShapeChanged,
    required this.showOrigGrid,
    required this.showTransGrid,
    required this.showOrigShape,
    required this.showLabels,
    required this.onOrigGridChanged,
    required this.onTransGridChanged,
    required this.onOrigShapeChanged,
    required this.onLabelsChanged,
  });

  @override
  State<VectorPanel> createState() => _VectorPanelState();
}

class _VectorPanelState extends State<VectorPanel> {
  final _xCtrl = TextEditingController(text: '2.0');
  final _yCtrl = TextEditingController(text: '1.5');
  final _lblCtrl = TextEditingController(text: 'P1');
  final _matrixScrollCtrl = ScrollController();
  Color? _ptColor;
  bool _showAsMatrix = false;

  @override
  void dispose() {
    _xCtrl.dispose();
    _yCtrl.dispose();
    _lblCtrl.dispose();
    _matrixScrollCtrl.dispose();
    super.dispose();
  }

  void _addPoint() {
    final x = double.tryParse(_xCtrl.text);
    final y = double.tryParse(_yCtrl.text);
    if (x == null || y == null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: const Text('Insira valores numéricos válidos para X e Y.'),
        backgroundColor: context.colors.danger,
      ));
      return;
    }
    final lbl = _lblCtrl.text.trim().isEmpty
        ? 'P${widget.shapeManager.basePoints.length + 1}'
        : _lblCtrl.text.trim();
    
    final success = widget.shapeManager.addPoint(x, y, label: lbl, color: _ptColor);
    if (!success) {
      showPointLimitDialog();
      return;
    }
    
    _lblCtrl.text = 'P${widget.shapeManager.basePoints.length + 1}';
    widget.onShapeChanged('Figura Personalizada');
  }

  void _pickColor() async {
    final color = await showDialog<Color>(
      context: context,
      builder: (ctx) => _ColorPickerDialog(currentColor: _ptColor ?? context.colors.vertexPalette[0]),
    );
    if (color != null) {
      setState(() => _ptColor = color);
    }
  }

  void showVertexCountDialog() async {
    final result = await showDialog<int>(
      context: context,
      builder: (ctx) => const _VertexCountDialog(),
    );
    if (result != null && result > 0) {
      widget.shapeManager.startCustomShape(result);
      widget.onShapeChanged('Figura Personalizada');
    }
  }

  void showPointLimitDialog() async {
    final colors = context.colors;
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: colors.bg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        title: Text('Limite Atingido', style: TextStyle(color: colors.text)),
        content: Text(
          'Você atingiu o limite de ${widget.shapeManager.pointLimit} pontos selecionado.',
          style: TextStyle(color: colors.text),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, 'ok'),
            child: Text('OK', style: TextStyle(color: colors.subtext)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, 'infinito'),
            child: Text('Limite Infinito', style: TextStyle(color: colors.accent)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: colors.accent),
            onPressed: () => Navigator.pop(ctx, 'alterar'),
            child: const Text('Alterar Limite', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (result == 'infinito') {
      widget.shapeManager.pointLimit = null;
      // Triggers a redraw implicitly if we add points next
    } else if (result == 'alterar') {
      showVertexCountDialog();
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final transPoints = widget.shapeManager.getTransformedPoints(widget.currentMatrix);
    _ptColor ??= colors.vertexPalette[0];

    return Container(
      width: 300,
      decoration: BoxDecoration(
        color: colors.panel,
        border: Border(left: BorderSide(color: colors.border, width: 1)),
      ),
      child: ListView(
        padding: const EdgeInsets.all(8),
        children: [
          // ---- Forma da Figura ----
          _CardSection(
            icon: Icons.category_rounded,
            title: 'Forma da Figura',
            colors: colors,
            children: [_buildShapeDropdown(colors)],
          ),
          const SizedBox(height: 6),

          // ---- Modo de Exibição ----
          _CardSection(
            icon: Icons.visibility_rounded,
            title: 'Modo de Exibição',
            colors: colors,
            children: [
              _viewModeRadio('Figura (Polígono)', 'Figura', colors),
              _viewModeRadio('Vetores (Setas)', 'Vetores', colors),
              _viewModeRadio('Ambos (Figura + Vetores)', 'Ambos', colors),
            ],
          ),
          const SizedBox(height: 6),

          // ---- Adicionar Ponto ----
          _CardSection(
            icon: Icons.add_location_alt_rounded,
            title: 'Adicionar Ponto',
            colors: colors,
            children: [
              Row(
                children: [
                  _miniField('X', _xCtrl, colors),
                  const SizedBox(width: 6),
                  _miniField('Y', _yCtrl, colors),
                  const SizedBox(width: 6),
                  _miniField('Nome', _lblCtrl, colors),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  GestureDetector(
                    onTap: _pickColor,
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: _ptColor,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: colors.border),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _addPoint,
                      icon: const Icon(Icons.add, size: 16),
                      label: const Text('Adicionar Ponto'),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 6),

          // ---- Pontos da Figura ----
          _CardSection(
            icon: Icons.scatter_plot_rounded,
            title: 'Pontos da Figura',
            colors: colors,
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _MiniToggleBtn(
                  label: 'Lista',
                  selected: !_showAsMatrix,
                  colors: colors,
                  onTap: () => setState(() => _showAsMatrix = false),
                ),
                _MiniToggleBtn(
                  label: 'Matriz',
                  selected: _showAsMatrix,
                  colors: colors,
                  onTap: () => setState(() => _showAsMatrix = true),
                ),
              ],
            ),
            children: [
              if (transPoints.isEmpty)
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Text('Nenhum ponto adicionado.',
                      style: TextStyle(
                          color: colors.subtext,
                          fontSize: 11,
                          fontStyle: FontStyle.italic)),
                )
              else if (_showAsMatrix)
                _buildMatrixView(transPoints, colors)
              else
                ...transPoints.asMap().entries.map((e) {
                  final idx = e.key;
                  final pt = e.value;
                  final bgColor =
                      idx % 2 == 0 ? colors.card : colors.cardAlt;
                  return Container(
                    color: bgColor,
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                    child: Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: pt.color,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            '${pt.label}  (${pt.x.toStringAsFixed(1)}, ${pt.y.toStringAsFixed(1)})',
                            style: TextStyle(
                                color: colors.text, fontSize: 12),
                          ),
                        ),
                        InkWell(
                          onTap: () {
                            widget.shapeManager.removePoint(idx);
                          },
                          child: Padding(
                            padding: const EdgeInsets.all(4),
                            child: Icon(Icons.close, size: 14, color: colors.subtext),
                          ),
                        ),
                      ],
                    ),
                  );
                }),
              const SizedBox(height: 6),
              Row(
                children: [
                  Expanded(
                    child: _ActionBtn(
                      icon: Icons.refresh_rounded,
                      label: 'Organizar',
                      color: colors.accent2,
                      colors: colors,
                      onTap: () => widget.shapeManager.sortPointsAngularly(),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: _ActionBtn(
                      icon: Icons.clear_all_rounded,
                      label: 'Limpar',
                      color: colors.danger,
                      colors: colors,
                      onTap: () {
                        widget.shapeManager.clearAll();
                        widget.onShapeChanged('Figura Personalizada');
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 6),

          // ---- Visibilidade ----
          _CardSection(
            icon: Icons.layers_rounded,
            title: 'Visibilidade',
            colors: colors,
            children: [
              _visToggle('Grade Cartesiana (Fundo)', widget.showOrigGrid,
                  widget.onOrigGridChanged, colors),
              _visToggle('Grade Transformada', widget.showTransGrid,
                  widget.onTransGridChanged, colors),
              _visToggle('Contorno Original', widget.showOrigShape,
                  widget.onOrigShapeChanged, colors),
              _visToggle(
                  'Rótulos e Coordenadas', widget.showLabels, widget.onLabelsChanged, colors),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMatrixView(List<Point2D> pts, AppColors colors) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: colors.cardAlt,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: colors.border),
      ),
      child: Row(
        children: [
          Text('[', style: TextStyle(fontSize: 32, color: colors.accent, fontWeight: FontWeight.bold)),
          const SizedBox(width: 8),
          Expanded(
            child: Listener(
              onPointerSignal: (event) {
                if (event is PointerScrollEvent) {
                  final offset = event.scrollDelta.dy;
                  _matrixScrollCtrl.jumpTo(
                    (_matrixScrollCtrl.offset + offset).clamp(
                      0.0,
                      _matrixScrollCtrl.position.maxScrollExtent,
                    ),
                  );
                }
              },
              child: SingleChildScrollView(
                controller: _matrixScrollCtrl,
                scrollDirection: Axis.horizontal,
                physics: const BouncingScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: pts.map((p) => Container(
                        width: 45,
                        alignment: Alignment.center,
                        child: Text(p.label, style: TextStyle(color: colors.subtext, fontSize: 10, fontWeight: FontWeight.bold)),
                      )).toList(),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: pts.map((p) => Container(
                        width: 45,
                      alignment: Alignment.center,
                      child: Text(p.x.toStringAsFixed(1), style: TextStyle(color: colors.text, fontSize: 13, fontFamily: 'monospace')),
                    )).toList(),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: pts.map((p) => Container(
                      width: 45,
                      alignment: Alignment.center,
                      child: Text(p.y.toStringAsFixed(1), style: TextStyle(color: colors.text, fontSize: 13, fontFamily: 'monospace')),
                    )).toList(),
                  ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text(']', style: TextStyle(fontSize: 32, color: colors.accent, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildShapeDropdown(AppColors colors) {
    const shapes = [
      'Quadrado Unitário',
      'Triângulo',
      'Casa',
      'Estrela',
      'Losango',
      'Figura Personalizada',
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: colors.cardAlt,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colors.border),
      ),
      child: DropdownButton<String>(
        value: shapes.contains(widget.shapeManager.shapeName)
            ? widget.shapeManager.shapeName
            : 'Quadrado Unitário',
        isExpanded: true,
        dropdownColor: colors.card,
        underline: const SizedBox(),
        style: TextStyle(color: colors.text, fontSize: 13),
        items: shapes
            .map((s) => DropdownMenuItem(value: s, child: Text(s)))
            .toList(),
        onChanged: (v) {
          if (v == null) return;
          if (v == 'Figura Personalizada') {
            showVertexCountDialog();
          } else {
            widget.shapeManager.loadPresetShape(v);
            widget.onShapeChanged(v);
          }
        },
      ),
    );
  }

  Widget _viewModeRadio(String text, String value, AppColors colors) {
    return RadioListTile<String>(
      title: Text(text,
          style: TextStyle(color: colors.text, fontSize: 12)),
      value: value,
      groupValue: widget.viewMode,
      onChanged: (v) {
        if (v != null) widget.onViewModeChanged(v);
      },
      dense: true,
      contentPadding: EdgeInsets.zero,
      activeColor: colors.accent,
    );
  }

  Widget _miniField(String label, TextEditingController ctrl, AppColors colors) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: colors.subtext, fontSize: 10)),
          const SizedBox(height: 2),
          SizedBox(
            height: 32,
            child: TextField(
              controller: ctrl,
              textAlign: TextAlign.center,
              style: TextStyle(color: colors.text, fontSize: 12),
              decoration: InputDecoration(
                contentPadding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                isDense: true,
                filled: true,
                fillColor: colors.cardAlt,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(6),
                  borderSide: BorderSide(color: colors.border),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _visToggle(String label, bool value, ValueChanged<bool> onChanged, AppColors colors) {
    return SizedBox(
      height: 32,
      child: Row(
        children: [
          SizedBox(
            width: 24,
            height: 24,
            child: Checkbox(
              value: value,
              onChanged: (v) => onChanged(v ?? false),
              activeColor: colors.accent,
              side: BorderSide(color: colors.subtext),
            ),
          ),
          const SizedBox(width: 8),
          Text(label, style: TextStyle(color: colors.text, fontSize: 12)),
        ],
      ),
    );
  }
}

// ================================================================== //
//  Widgets auxiliares
// ================================================================== //

class _CardSection extends StatelessWidget {
  final IconData icon;
  final String title;
  final AppColors colors;
  final Widget? trailing;
  final List<Widget> children;

  const _CardSection({
    required this.icon,
    required this.title,
    required this.colors,
    this.trailing,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: colors.card,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: colors.border, width: 0.5),
        boxShadow: [
          BoxShadow(color: colors.shadow, blurRadius: 8, offset: const Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              border:
                  Border(bottom: BorderSide(color: colors.border, width: 0.5)),
            ),
            child: Row(
              children: [
                Icon(icon, color: colors.accent, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(title,
                      style: TextStyle(
                          color: colors.text,
                          fontSize: 12,
                          fontWeight: FontWeight.w600)),
                ),
                if (trailing != null) trailing!,
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: children,
            ),
          ),
        ],
      ),
    );
  }
}

class _MiniToggleBtn extends StatelessWidget {
  final String label;
  final bool selected;
  final AppColors colors;
  final VoidCallback onTap;

  const _MiniToggleBtn({
    required this.label,
    required this.selected,
    required this.colors,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(left: 4),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: selected ? colors.accent : colors.cardAlt,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(color: selected ? colors.accent : colors.border),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: selected ? Colors.white : colors.subtext,
            fontSize: 10,
            fontWeight: selected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}

class _ActionBtn extends StatefulWidget {
  final IconData icon;
  final String label;
  final Color color;
  final AppColors colors;
  final VoidCallback onTap;

  const _ActionBtn({
    required this.icon,
    required this.label,
    required this.color,
    required this.colors,
    required this.onTap,
  });

  @override
  State<_ActionBtn> createState() => _ActionBtnState();
}

class _ActionBtnState extends State<_ActionBtn> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          decoration: BoxDecoration(
            color: _hovered ? widget.colors.border : widget.colors.cardAlt,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(widget.icon, size: 14, color: widget.color),
              const SizedBox(width: 4),
              Text(widget.label,
                  style: TextStyle(color: widget.color, fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }
}

// ================================================================== //
//  Diálogo de quantidade de vértices
// ================================================================== //

class _VertexCountDialog extends StatefulWidget {
  const _VertexCountDialog();

  @override
  State<_VertexCountDialog> createState() => _VertexCountDialogState();
}

class _VertexCountDialogState extends State<_VertexCountDialog> {
  int _count = 4;

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Dialog(
      backgroundColor: colors.bg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Quantos vértices a sua\nfigura vai ter?',
              textAlign: TextAlign.center,
              style: TextStyle(color: colors.text, fontSize: 16),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  onPressed: _count > 1
                      ? () => setState(() => _count--)
                      : null,
                  icon: const Icon(Icons.remove_circle_outline),
                  color: colors.accent,
                ),
                Container(
                  width: 60,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: colors.card,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: colors.border),
                  ),
                  child: Text(
                    '$_count',
                    textAlign: TextAlign.center,
                    style:
                        TextStyle(color: colors.text, fontSize: 18),
                  ),
                ),
                IconButton(
                  onPressed: _count < 100
                      ? () => setState(() => _count++)
                      : null,
                  icon: const Icon(Icons.add_circle_outline),
                  color: colors.accent,
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Cancelar',
                        style: TextStyle(color: colors.subtext)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => Navigator.pop(context, _count),
                    child: const Text('Continuar'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ================================================================== //
//  Seletor de cores simples
// ================================================================== //

class _ColorPickerDialog extends StatelessWidget {
  final Color currentColor;

  const _ColorPickerDialog({required this.currentColor});

  static const _colors = [
    Color(0xFFff79c6),
    Color(0xFFffb86c),
    Color(0xFFbd93f9),
    Color(0xFF50fa7b),
    Color(0xFF8be9fd),
    Color(0xFFf1fa8c),
    Color(0xFFff5555),
    Color(0xFFff6e6e),
    Color(0xFF44475a),
    Color(0xFF6272a4),
    Color(0xFFf8f8f2),
    Color(0xFF00f2fe),
  ];

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Dialog(
      backgroundColor: colors.bg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Escolha uma cor',
                style: TextStyle(color: colors.text, fontSize: 14)),
            const SizedBox(height: 16),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: _colors
                  .map((c) => GestureDetector(
                        onTap: () => Navigator.pop(context, c),
                        child: Container(
                          width: 36,
                          height: 36,
                          decoration: BoxDecoration(
                            color: c,
                            borderRadius: BorderRadius.circular(8),
                            border: c == currentColor
                                ? Border.all(color: Colors.white, width: 2)
                                : null,
                          ),
                        ),
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}
