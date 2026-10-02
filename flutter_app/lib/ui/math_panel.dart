/// ui/math_panel.dart
import 'package:flutter/material.dart';
import '../core/shape_manager.dart';
import '../core/matrix2d.dart';
import '../theme.dart';

class MathPanel extends StatelessWidget {
  final ShapeManager shapeManager;
  final List<List<double>> currentMatrix;
  final String currentPreset;

  const MathPanel({
    super.key,
    required this.shapeManager,
    required this.currentMatrix,
    required this.currentPreset,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final mTotal = shapeManager.getTotalMatrix(currentMatrix);
    final ptsOrig = shapeManager.basePoints;
    final ptsTrans = shapeManager.getTransformedPoints(currentMatrix);
    
    List<List<double>>? mInverse;
    try {
      mInverse = Matrix2D.inverse(mTotal);
    } catch (_) {
      mInverse = null;
    }

    // Preparar lista da T Direta
    final directMatrices = <List<List<double>>>[];
    final directLabels = <String>[];
    
    if (!Matrix2D.isIdentity(currentMatrix)) {
      directMatrices.add(currentMatrix);
      directLabels.add(currentPreset);
    }
    for (int i = shapeManager.matrixStack.length - 1; i >= 0; i--) {
      directMatrices.add(shapeManager.matrixStack[i]);
      directLabels.add(shapeManager.matrixNamesStack[i]);
    }
    if (directMatrices.isEmpty) {
      directMatrices.add(Matrix2D.identity());
      directLabels.add('Identidade');
    }

    // Preparar lista da T Reversa
    final reverseMatrices = <List<List<double>>>[];
    final reverseLabels = <String>[];
    for (int i = 0; i < shapeManager.matrixStack.length; i++) {
      final inv = Matrix2D.inverse(shapeManager.matrixStack[i]);
      if (inv != null) {
        reverseMatrices.add(inv);
        reverseLabels.add('${shapeManager.matrixNamesStack[i]}⁻¹');
      }
    }
    if (!Matrix2D.isIdentity(currentMatrix)) {
      final inv = Matrix2D.inverse(currentMatrix);
      if (inv != null) {
        reverseMatrices.add(inv);
        reverseLabels.add('${currentPreset}⁻¹');
      }
    }
    if (reverseMatrices.isEmpty && mInverse != null) {
      reverseMatrices.add(mInverse);
      reverseLabels.add('Identidade⁻¹');
    }

    return Container(
      color: colors.bg,
      width: double.infinity,
      height: double.infinity,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text(
              'Álgebra Linear na Prática',
              style: TextStyle(color: colors.accent, fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Veja como as transformações acontecem matricialmente em tempo real.',
              style: TextStyle(color: colors.subtext, fontSize: 14),
            ),
            const SizedBox(height: 48),

            // ================== DIRETA ================== //
            _buildSectionTitle('1. Composição da Transformação Total', colors),
            const SizedBox(height: 24),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: _buildEquation(directMatrices, directLabels, mTotal, 'T_Total', colors),
              ),
            ),
            
            const SizedBox(height: 24),
            _buildSectionTitle('2. Aplicação nos Pontos Originais', colors),
            const SizedBox(height: 24),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildTransformMatrix(mTotal, 'T_Total', colors),
                  _buildOperator('×', colors),
                  _buildPointsMatrix(ptsOrig, 'P (Originais)', colors),
                  _buildOperator('=', colors),
                  _buildPointsMatrix(ptsTrans, 'P\' (Transformados)', colors, highlight: true),
                ],
              ),
            ),

            const SizedBox(height: 64),
            
            // ================== REVERSA ================== //
            _buildSectionTitle('3. Matriz Inversa (Desfazendo a Transformação)', colors),
            const SizedBox(height: 24),
            if (mInverse == null)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: colors.danger.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text('A matriz de transformação total possui determinante 0 e não pode ser invertida.', style: TextStyle(color: colors.danger)),
              )
            else ...[
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: _buildEquation(reverseMatrices, reverseLabels, mInverse, 'T_Total⁻¹', colors, isExponent: true),
                ),
              ),
              const SizedBox(height: 24),
              _buildSectionTitle('4. Projeção Reversa para Encontrar Origem', colors),
              const SizedBox(height: 24),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _buildTransformMatrix(mInverse, 'T_Total⁻¹', colors, exponent: true),
                    _buildOperator('×', colors),
                    _buildPointsMatrix(ptsTrans, 'P\' (Transformados)', colors),
                    _buildOperator('=', colors),
                    _buildPointsMatrix(ptsOrig, 'P (Originais)', colors, highlight: true),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 64),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildEquation(List<List<List<double>>> mats, List<String> labels, List<List<double>> resMat, String resLabel, AppColors colors, {bool isExponent = false}) {
    List<Widget> widgets = [];
    for (int i = 0; i < mats.length; i++) {
      widgets.add(_buildTransformMatrix(mats[i], labels[i], colors, exponent: isExponent));
      if (i < mats.length - 1) {
        widgets.add(_buildOperator('×', colors));
      }
    }
    widgets.add(_buildOperator('=', colors));
    widgets.add(_buildTransformMatrix(resMat, resLabel, colors, exponent: isExponent, highlight: true));
    return widgets;
  }

  Widget _buildSectionTitle(String title, AppColors colors) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: colors.card,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colors.border),
      ),
      child: Text(
        title,
        style: TextStyle(color: colors.text, fontSize: 16, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildOperator(String op, AppColors colors) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Text(
        op,
        style: TextStyle(color: colors.text, fontSize: 32, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildTransformMatrix(List<List<double>> m, String label, AppColors colors, {bool exponent = false, bool highlight = false}) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(color: highlight ? colors.accent : colors.subtext, fontSize: 14, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: highlight ? colors.accent.withOpacity(0.05) : colors.cardAlt,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: highlight ? colors.accent : colors.border, width: highlight ? 2 : 1),
          ),
          child: Row(
            children: [
              Text('[', style: TextStyle(fontSize: 64, color: colors.accent, fontWeight: FontWeight.w300)),
              const SizedBox(width: 16),
              Column(
                children: [
                  Row(
                    children: [
                      _cell(m[0][0], colors),
                      const SizedBox(width: 16),
                      _cell(m[0][1], colors),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      _cell(m[1][0], colors),
                      const SizedBox(width: 16),
                      _cell(m[1][1], colors),
                    ],
                  ),
                ],
              ),
              const SizedBox(width: 16),
              Text(']', style: TextStyle(fontSize: 64, color: colors.accent, fontWeight: FontWeight.w300)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPointsMatrix(List<Point2D> pts, String label, AppColors colors, {bool highlight = false}) {
    if (pts.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: colors.cardAlt,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: highlight ? colors.accent : colors.border),
        ),
        child: Text('Nenhum Ponto', style: TextStyle(color: colors.subtext)),
      );
    }
    
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(color: highlight ? colors.accent : colors.subtext, fontSize: 14, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: highlight ? colors.accent.withOpacity(0.05) : colors.cardAlt,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: highlight ? colors.accent : colors.border, width: highlight ? 2 : 1),
          ),
          child: Row(
            children: [
              Text('[', style: TextStyle(fontSize: 64, color: colors.accent, fontWeight: FontWeight.w300)),
              const SizedBox(width: 16),
              Column(
                children: [
                  Row(
                    children: pts.map((p) => Container(
                      width: 60,
                      alignment: Alignment.center,
                      child: Text(p.x.toStringAsFixed(2), style: TextStyle(color: colors.text, fontSize: 16, fontFamily: 'monospace')),
                    )).toList(),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: pts.map((p) => Container(
                      width: 60,
                      alignment: Alignment.center,
                      child: Text(p.y.toStringAsFixed(2), style: TextStyle(color: colors.text, fontSize: 16, fontFamily: 'monospace')),
                    )).toList(),
                  ),
                ],
              ),
              const SizedBox(width: 16),
              Text(']', style: TextStyle(fontSize: 64, color: colors.accent, fontWeight: FontWeight.w300)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _cell(double val, AppColors colors) {
    return Container(
      width: 60,
      alignment: Alignment.center,
      child: Text(
        val.toStringAsFixed(2),
        style: TextStyle(color: colors.text, fontSize: 16, fontFamily: 'monospace', fontWeight: FontWeight.bold),
      ),
    );
  }
}
