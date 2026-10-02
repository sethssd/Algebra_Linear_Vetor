/// ui/controls_panel.dart
import 'package:flutter/material.dart';
import '../core/matrix2d.dart';
import '../core/shape_manager.dart';
import '../theme.dart';

class ControlsPanel extends StatefulWidget {
  final ShapeManager shapeManager;
  final List<List<double>> currentMatrix;
  final double morphT;
  final String preset;
  final ValueChanged<String> onPresetChanged;
  final ValueChanged<List<List<double>>> onMatrixChanged;
  final ValueChanged<double> onMorphChanged;
  final VoidCallback onUndo;
  final VoidCallback onReset;
  final VoidCallback onColorPick;
  final VoidCallback onAnimate;
  final bool isAnimating;

  const ControlsPanel({
    super.key,
    required this.shapeManager,
    required this.currentMatrix,
    required this.morphT,
    required this.preset,
    required this.onPresetChanged,
    required this.onMatrixChanged,
    required this.onMorphChanged,
    required this.onUndo,
    required this.onReset,
    required this.onColorPick,
    required this.onAnimate,
    required this.isAnimating,
  });

  @override
  State<ControlsPanel> createState() => _ControlsPanelState();
}

class _ControlsPanelState extends State<ControlsPanel> {
  double _angle = 0.0;
  double _scaleX = 1.0;
  double _scaleY = 1.0;
  bool _linkScale = false;

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final m = widget.currentMatrix;
    final count = widget.shapeManager.historyCount;
    final canUndo = widget.shapeManager.canUndo;

    return Container(
      width: 320,
      decoration: BoxDecoration(
        color: colors.panel,
        border: Border(right: BorderSide(color: colors.border, width: 1)),
      ),
      child: ListView(
        padding: const EdgeInsets.all(8),
        children: [
          // ---- Seção 1: Transformação ----
          _CardSection(
            icon: Icons.rotate_right_rounded,
            title: 'Transformação',
            colors: colors,
            children: [
              _buildPresetDropdown(colors),
              const SizedBox(height: 8),
              ..._buildDynamicControls(colors),
            ],
          ),

          const SizedBox(height: 6),

          // ---- Seção 2: Histórico ----
          _CardSection(
            icon: Icons.history_rounded,
            title: 'Histórico & Desfazer',
            colors: colors,
            children: [
              Row(
                children: [
                  Expanded(
                    child: _ActionButton(
                      icon: Icons.undo_rounded,
                      label: 'Desfazer',
                      color: colors.warn,
                      colors: colors,
                      onTap: widget.onUndo,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: _ActionButton(
                      icon: Icons.restore_rounded,
                      label: 'Restaurar',
                      color: canUndo ? colors.danger : colors.subtext,
                      colors: colors,
                      onTap: widget.onReset,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                count > 0
                    ? '●  $count alteraç${count > 1 ? 'ões' : 'ão'} no histórico'
                    : '—  Sem alterações',
                style: TextStyle(
                  color: count > 0 ? colors.accent : colors.subtext,
                  fontSize: 11,
                ),
              ),
            ],
          ),

          const SizedBox(height: 6),

          // ---- Seção 3: Matriz [M] ----
          _CardSection(
            icon: Icons.grid_on_rounded,
            title: 'Matriz  [M]',
            colors: colors,
            children: [
              _buildMatrixDisplay(m, colors),
            ],
          ),

          const SizedBox(height: 6),

          // ---- Seção 4: Aparência ----
          _CardSection(
            icon: Icons.palette_rounded,
            title: 'Aparência',
            colors: colors,
            children: [
              _ActionButton(
                icon: Icons.color_lens_rounded,
                label: 'Alterar Cor da Figura',
                color: colors.text,
                colors: colors,
                onTap: widget.onColorPick,
              ),
              const SizedBox(height: 10),
              Text('Progresso da Transformação (t):',
                  style: TextStyle(color: colors.subtext, fontSize: 11)),
              const SizedBox(height: 4),
              SliderTheme(
                data: SliderTheme.of(context),
                child: Slider(
                  value: widget.morphT,
                  onChanged: (v) => widget.onMorphChanged(v),
                ),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Expanded(
                    child: _ActionButton(
                      icon: widget.isAnimating ? Icons.pause_rounded : Icons.play_arrow_rounded,
                      label: widget.isAnimating ? 'Pausar' : 'Animar',
                      color: widget.isAnimating ? colors.warn : colors.success,
                      colors: colors,
                      onTap: widget.onAnimate,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: _ActionButton(
                      icon: Icons.first_page_rounded,
                      label: 'Zerar (t=0)',
                      color: colors.subtext,
                      colors: colors,
                      onTap: () => widget.onMorphChanged(0.0),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPresetDropdown(AppColors colors) {
    const presets = [
      'Identidade',
      'Rotação',
      'Escala',
      'Reflexão no Eixo X',
      'Reflexão no Eixo Y',
      'Reflexão na Reta Y = X',
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: colors.cardAlt,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colors.border),
      ),
      child: DropdownButton<String>(
        value: widget.preset,
        isExpanded: true,
        dropdownColor: colors.card,
        underline: const SizedBox(),
        style: TextStyle(color: colors.text, fontSize: 13),
        items: presets
            .map((p) => DropdownMenuItem(value: p, child: Text(p)))
            .toList(),
        onChanged: (v) {
          if (v != null) {
            widget.onPresetChanged(v);
            if (v == 'Rotação') {
              _angle = 0.0;
            } else if (v == 'Escala') {
              _scaleX = 1.0;
              _scaleY = 1.0;
            }
          }
        },
      ),
    );
  }

  List<Widget> _buildDynamicControls(AppColors colors) {
    switch (widget.preset) {
      case 'Rotação':
        return [
          _SliderRow(
            label: 'Ângulo de Rotação (°)',
            value: _angle,
            defaultMin: -360,
            defaultMax: 360,
            colors: colors,
            onChanged: (v) {
              setState(() => _angle = v);
              widget.onMatrixChanged(Matrix2D.rotation(v));
            },
          ),
        ];
      case 'Escala':
        return [
          Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    _SliderRow(
                      label: 'Escala X (Sₓ)',
                      value: _scaleX,
                      defaultMin: -5,
                      defaultMax: 5,
                      colors: colors,
                      onChanged: (v) {
                        setState(() {
                          _scaleX = v;
                          if (_linkScale) _scaleY = v;
                        });
                        widget.onMatrixChanged(Matrix2D.scaling(_scaleX, _scaleY));
                      },
                    ),
                    _SliderRow(
                      label: 'Escala Y (Sᵧ)',
                      value: _scaleY,
                      defaultMin: -5,
                      defaultMax: 5,
                      colors: colors,
                      onChanged: (v) {
                        setState(() {
                          _scaleY = v;
                          if (_linkScale) _scaleX = v;
                        });
                        widget.onMatrixChanged(Matrix2D.scaling(_scaleX, _scaleY));
                      },
                    ),
                  ],
                ),
              ),
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(
                    icon: Icon(
                      _linkScale ? Icons.link_rounded : Icons.link_off_rounded,
                      color: _linkScale ? colors.accent : colors.subtext,
                    ),
                    tooltip: 'Manter Proporção',
                    onPressed: () {
                      setState(() {
                        _linkScale = !_linkScale;
                        if (_linkScale) {
                          if (_scaleX.abs() < _scaleY.abs()) {
                            _scaleY = _scaleX;
                          } else {
                            _scaleX = _scaleY;
                          }
                          widget.onMatrixChanged(Matrix2D.scaling(_scaleX, _scaleY));
                        }
                      });
                    },
                  ),
                ],
              ),
            ],
          ),
        ];
      default:
        return [];
    }
  }

  Widget _buildMatrixDisplay(List<List<double>> m, AppColors colors) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('[', style: TextStyle(fontSize: 36, color: colors.accent, fontWeight: FontWeight.bold)),
          const SizedBox(width: 8),
          Column(
            children: [
              Row(
                children: [
                  _matrixCell(m[0][0], colors),
                  const SizedBox(width: 12),
                  _matrixCell(m[0][1], colors),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  _matrixCell(m[1][0], colors),
                  const SizedBox(width: 12),
                  _matrixCell(m[1][1], colors),
                ],
              ),
            ],
          ),
          const SizedBox(width: 8),
          Text(']', style: TextStyle(fontSize: 36, color: colors.accent, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _matrixCell(double value, AppColors colors) {
    return Container(
      width: 60,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(
        color: colors.cardAlt,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: colors.border),
      ),
      child: Text(
        value.toStringAsFixed(2),
        textAlign: TextAlign.center,
        style: TextStyle(color: colors.text, fontSize: 13, fontFamily: 'monospace'),
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
  final List<Widget> children;

  const _CardSection({
    required this.icon,
    required this.title,
    required this.colors,
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
              border: Border(bottom: BorderSide(color: colors.border, width: 0.5)),
            ),
            child: Row(
              children: [
                Icon(icon, color: colors.accent, size: 16),
                const SizedBox(width: 8),
                Text(title,
                    style: TextStyle(
                        color: colors.text,
                        fontSize: 12,
                        fontWeight: FontWeight.w600)),
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

class _ActionButton extends StatefulWidget {
  final IconData icon;
  final String label;
  final Color color;
  final AppColors colors;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.colors,
    required this.onTap,
  });

  @override
  State<_ActionButton> createState() => _ActionButtonState();
}

class _ActionButtonState extends State<_ActionButton> {
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
              Text(
                widget.label,
                style: TextStyle(color: widget.color, fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SliderRow extends StatefulWidget {
  final String label;
  final double value;
  final double defaultMin;
  final double defaultMax;
  final AppColors colors;
  final ValueChanged<double> onChanged;

  const _SliderRow({
    super.key,
    required this.label,
    required this.value,
    required this.defaultMin,
    required this.defaultMax,
    required this.colors,
    required this.onChanged,
  });

  @override
  State<_SliderRow> createState() => _SliderRowState();
}

class _SliderRowState extends State<_SliderRow> {
  late double currentMin;
  late double currentMax;
  late TextEditingController _controller;
  FocusNode _focusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    currentMin = widget.defaultMin;
    currentMax = widget.defaultMax;
    _expandBoundsIfNeeded(widget.value);
    _controller = TextEditingController(text: widget.value.toStringAsFixed(1));
    
    _focusNode.addListener(() {
      if (!_focusNode.hasFocus) {
        _submitText();
      }
    });
  }

  @override
  void didUpdateWidget(covariant _SliderRow oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value && !_focusNode.hasFocus) {
      _expandBoundsIfNeeded(widget.value);
      _controller.text = widget.value.toStringAsFixed(1);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _expandBoundsIfNeeded(double v) {
    if (v < currentMin) {
      currentMin = v.floorToDouble();
    }
    if (v > currentMax) {
      currentMax = v.ceilToDouble();
    }
  }

  void _submitText() {
    final double? val = double.tryParse(_controller.text.replaceAll(',', '.'));
    if (val != null) {
      setState(() {
        _expandBoundsIfNeeded(val);
      });
      widget.onChanged(val);
      _controller.text = val.toStringAsFixed(1);
    } else {
      _controller.text = widget.value.toStringAsFixed(1);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(widget.label, style: TextStyle(color: widget.colors.subtext, fontSize: 11)),
          const SizedBox(height: 4),
          Row(
            children: [
              Expanded(
                child: Slider(
                  value: widget.value.clamp(currentMin, currentMax),
                  min: currentMin,
                  max: currentMax,
                  onChanged: (v) {
                    _controller.text = v.toStringAsFixed(1);
                    widget.onChanged(v);
                  },
                ),
              ),
              SizedBox(
                width: 60,
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
                  textAlign: TextAlign.center,
                  style: TextStyle(color: widget.colors.text, fontSize: 12),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
                    isDense: true,
                    filled: true,
                    fillColor: widget.colors.cardAlt,
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(6),
                      borderSide: BorderSide(color: widget.colors.border),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(6),
                      borderSide: BorderSide(color: widget.colors.accent),
                    ),
                  ),
                  onSubmitted: (_) => _submitText(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
