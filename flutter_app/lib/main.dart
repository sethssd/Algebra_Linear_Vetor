/// main.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'core/matrix2d.dart';
import 'core/shape_manager.dart';
import 'theme.dart';
import 'ui/canvas_view.dart';
import 'ui/controls_panel.dart';
import 'ui/vector_panel.dart';
import 'ui/math_panel.dart';

void main() {
  runApp(const TransformadorApp());
}

class TransformadorApp extends StatefulWidget {
  const TransformadorApp({super.key});

  static _TransformadorAppState of(BuildContext context) {
    return context.findAncestorStateOfType<_TransformadorAppState>()!;
  }

  @override
  State<TransformadorApp> createState() => _TransformadorAppState();
}

class _TransformadorAppState extends State<TransformadorApp> {
  ThemeMode _themeMode = ThemeMode.dark;

  void toggleTheme() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Transformador Linear 2D',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: _themeMode,
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with SingleTickerProviderStateMixin {
  late final ShapeManager _shapeManager;

  // Estado de transformação
  String _preset = 'Identidade';
  List<List<double>> _targetMatrix = Matrix2D.identity();
  double _morphT = 1.0;
  bool _isAnimating = false;
  AnimationController? _animController;
  bool _showMathPanel = false;

  // Opções de visualização
  String _viewMode = 'Ambos';
  bool _showOrigGrid = true;
  bool _showTransGrid = false;
  bool _showOrigShape = true;
  bool _showLabels = true;

  // Cores da figura
  Color? _shapeFill;
  Color? _shapeOutline;

  @override
  void initState() {
    super.initState();
    _shapeManager = ShapeManager();
    _shapeManager.addListener(_onShapeChanged);
  }

  @override
  void dispose() {
    _shapeManager.removeListener(_onShapeChanged);
    _animController?.dispose();
    super.dispose();
  }

  void _onShapeChanged() => setState(() {});

  List<List<double>> get _currentMatrix {
    return Matrix2D.interpolate(Matrix2D.identity(), _targetMatrix, _morphT);
  }

  void _onPresetChanged(String preset) {
    final mCurrent = _currentMatrix;
    if (!Matrix2D.isIdentity(mCurrent)) {
      _shapeManager.applyTransformation(mCurrent, _preset);
    }

    setState(() {
      _preset = preset;
      _morphT = 1.0;

      switch (preset) {
        case 'Identidade':
          _targetMatrix = Matrix2D.identity();
        case 'Rotação':
          _targetMatrix = Matrix2D.identity();
        case 'Escala':
          _targetMatrix = Matrix2D.identity();
        case 'Reflexão no Eixo X':
          _targetMatrix = Matrix2D.reflectX();
        case 'Reflexão no Eixo Y':
          _targetMatrix = Matrix2D.reflectY();
        case 'Reflexão na Reta Y = X':
          _targetMatrix = Matrix2D.reflectYX();
      }
    });
  }

  void _onMatrixChanged(List<List<double>> m) {
    setState(() => _targetMatrix = m);
  }

  void _onMorphChanged(double v) {
    setState(() => _morphT = v);
  }

  void _onUndo() {
    final mCurrent = _currentMatrix;
    if (!Matrix2D.isIdentity(mCurrent)) {
      // Cancelar pré-visualização ativa
      setState(() {
        _preset = 'Identidade';
        _targetMatrix = Matrix2D.identity();
        _morphT = 1.0;
      });
      return;
    }
    // Caso contrário, dar pop no histórico completo
    _shapeManager.popHistory();
  }

  void _onReset() {
    if (_shapeManager.restoreInitialState()) {
      setState(() {
        _preset = 'Identidade';
        _targetMatrix = Matrix2D.identity();
        _morphT = 1.0;
      });
    }
  }

  void _onColorPick() async {
    final colors = [
      context.colors.shapeFill,
      const Color(0x55ff79c6),
      const Color(0x5550fa7b),
      const Color(0x55ffb86c),
      const Color(0x558be9fd),
      const Color(0x55f1fa8c),
    ];
    final outlines = [
      context.colors.shapeOutline,
      const Color(0xFFff79c6),
      const Color(0xFF50fa7b),
      const Color(0xFFffb86c),
      const Color(0xFF8be9fd),
      const Color(0xFFf1fa8c),
    ];
    final result = await showDialog<int>(
      context: context,
      builder: (ctx) => Dialog(
        backgroundColor: context.colors.bg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Escolha a cor da figura',
                  style: TextStyle(color: context.colors.text, fontSize: 14)),
              const SizedBox(height: 16),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: List.generate(
                  outlines.length,
                  (i) => GestureDetector(
                    onTap: () => Navigator.pop(ctx, i),
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: outlines[i],
                        borderRadius: BorderRadius.circular(8),
                        border: outlines[i] == (_shapeOutline ?? context.colors.shapeOutline)
                            ? Border.all(color: Colors.white, width: 2)
                            : null,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
    if (result != null) {
      setState(() {
        _shapeFill = colors[result];
        _shapeOutline = outlines[result];
      });
    }
  }

  void _onAnimate() {
    if (_isAnimating) {
      _animController?.stop();
      setState(() => _isAnimating = false);
      return;
    }

    _animController?.dispose();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );

    if (_morphT >= 1.0) {
      setState(() => _morphT = 0.0);
    }

    _animController!.addListener(() {
      setState(() {
        _morphT = _animController!.value;
      });
    });
    _animController!.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        setState(() => _isAnimating = false);
      }
    });

    _animController!.forward(from: _morphT);
    setState(() => _isAnimating = true);
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    
    // Fallbacks para caso o tema mude e não tenha sido forçado
    final sFill = _shapeFill ?? colors.shapeFill;
    final sOutline = _shapeOutline ?? colors.shapeOutline;

    return Scaffold(
      backgroundColor: colors.bg,
      body: CallbackShortcuts(
        bindings: {
          const SingleActivator(LogicalKeyboardKey.keyZ, control: true): _onUndo,
        },
        child: Focus(
          autofocus: true,
          child: Column(
            children: [
              // Header
              _buildHeader(colors),
              Container(height: 1, color: colors.border),

              // Body principal
              Expanded(
                child: _showMathPanel 
                ? MathPanel(
                    shapeManager: _shapeManager,
                    currentMatrix: _currentMatrix,
                    currentPreset: _preset,
                  )
                : Row(
                  children: [
                    // Painel esquerdo (controles)
                    ControlsPanel(
                      shapeManager: _shapeManager,
                      currentMatrix: _currentMatrix,
                      morphT: _morphT,
                      preset: _preset,
                      onPresetChanged: _onPresetChanged,
                      onMatrixChanged: _onMatrixChanged,
                      onMorphChanged: _onMorphChanged,
                      onUndo: _onUndo,
                      onReset: _onReset,
                      onColorPick: _onColorPick,
                      onAnimate: _onAnimate,
                      isAnimating: _isAnimating,
                    ),

                    // Canvas central
                    Expanded(
                      child: Container(
                        margin: const EdgeInsets.symmetric(horizontal: 4),
                        decoration: BoxDecoration(
                          color: colors.panel,
                          border: Border.all(color: colors.border, width: 1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: CanvasView(
                          shapeManager: _shapeManager,
                          currentMatrix: _currentMatrix,
                          viewMode: _viewMode,
                          showOrigGrid: _showOrigGrid,
                          showTransGrid: _showTransGrid,
                          showOrigShape: _showOrigShape,
                          showLabels: _showLabels,
                          shapeFillColor: sFill,
                          shapeOutlineColor: sOutline,
                          onPointAdded: () => setState(() {}),
                        ),
                      ),
                    ),

                    // Painel direito (pontos)
                    VectorPanel(
                      shapeManager: _shapeManager,
                      currentMatrix: _currentMatrix,
                      viewMode: _viewMode,
                      onViewModeChanged: (v) => setState(() => _viewMode = v),
                      onShapeChanged: (v) => setState(() {}),
                      showOrigGrid: _showOrigGrid,
                      showTransGrid: _showTransGrid,
                      showOrigShape: _showOrigShape,
                      showLabels: _showLabels,
                      onOrigGridChanged: (v) => setState(() => _showOrigGrid = v),
                      onTransGridChanged: (v) => setState(() => _showTransGrid = v),
                      onOrigShapeChanged: (v) => setState(() => _showOrigShape = v),
                      onLabelsChanged: (v) => setState(() => _showLabels = v),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(AppColors colors) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      height: 54,
      padding: const EdgeInsets.symmetric(horizontal: 8),
      color: colors.panel,
      child: Row(
        children: [
          // Accent bar
          Container(width: 4, height: 30, decoration: BoxDecoration(
            color: colors.accent,
            borderRadius: BorderRadius.circular(2),
          )),
          const SizedBox(width: 12),

          // Título
          Text(
            'Transformador Linear 2D',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              color: colors.text,
            ),
          ),
          const SizedBox(width: 8),

          // Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: colors.accent,
              borderRadius: BorderRadius.circular(4),
            ),
            child: const Text('2D',
                style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: Colors.white)),
          ),
          const SizedBox(width: 12),

          // Subtítulo
          Text(
            'Visualização interativa de transformações matriciais',
            style: TextStyle(fontSize: 12, color: colors.subtext),
          ),
          const Spacer(),
          IconButton(
            icon: Icon(
              _showMathPanel ? Icons.close_fullscreen_rounded : Icons.calculate_rounded,
              color: colors.accent,
            ),
            tooltip: _showMathPanel ? 'Voltar ao Editor' : 'Visualização Matemática',
            onPressed: () {
              setState(() => _showMathPanel = !_showMathPanel);
            },
          ),
          IconButton(
            icon: Icon(
              isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
              color: colors.text,
            ),
            tooltip: 'Alternar Tema',
            onPressed: () {
              TransformadorApp.of(context).toggleTheme();
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
    );
  }
}
