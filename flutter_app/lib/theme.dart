import 'package:flutter/material.dart';

class AppColors {
  final Color bg;
  final Color panel;
  final Color card;
  final Color cardAlt;
  final Color border;
  final Color borderGlow;
  final Color text;
  final Color subtext;
  final Color accent;
  final Color accent2;
  final Color success;
  final Color warn;
  final Color danger;
  final Color shadow;
  final Color gridOrig;
  final Color gridTrans;
  final Color axis;
  final Color origShape;
  final Color shapeFill;
  final Color shapeOutline;
  final List<Color> vertexPalette;

  const AppColors({
    required this.bg,
    required this.panel,
    required this.card,
    required this.cardAlt,
    required this.border,
    required this.borderGlow,
    required this.text,
    required this.subtext,
    required this.accent,
    required this.accent2,
    required this.success,
    required this.warn,
    required this.danger,
    required this.shadow,
    required this.gridOrig,
    required this.gridTrans,
    required this.axis,
    required this.origShape,
    required this.shapeFill,
    required this.shapeOutline,
    required this.vertexPalette,
  });
}

const darkColors = AppColors(
  bg: Color(0xFF0f0f17),
  panel: Color(0xFF16161f),
  card: Color(0xFF1e1e2c),
  cardAlt: Color(0xFF252535),
  border: Color(0xFF2e2e42),
  borderGlow: Color(0xFF7c6af7),
  text: Color(0xFFe4e4f0),
  subtext: Color(0xFF7878a0),
  accent: Color(0xFF7c6af7),
  accent2: Color(0xFF56b0f5),
  success: Color(0xFF4ecb91),
  warn: Color(0xFFf5a742),
  danger: Color(0xFFf56b6b),
  shadow: Color(0xFF0a0a12),
  gridOrig: Color(0xFF1a1a2e),
  gridTrans: Color(0x557c6af7),
  axis: Color(0xFF3a3a5a),
  origShape: Color(0xFF4a4a6a),
  shapeFill: Color(0x55bd93f9),
  shapeOutline: Color(0xFFbd93f9),
  vertexPalette: [
    Color(0xFFff79c6),
    Color(0xFFffb86c),
    Color(0xFFbd93f9),
    Color(0xFF50fa7b),
    Color(0xFF8be9fd),
    Color(0xFFf1fa8c),
  ],
);

const lightColors = AppColors(
  bg: Color(0xFFf0f0f5),
  panel: Color(0xFFffffff),
  card: Color(0xFFf8f8fa),
  cardAlt: Color(0xFFf0f0f5),
  border: Color(0xFFd0d0d8),
  borderGlow: Color(0xFF7c6af7),
  text: Color(0xFF1a1a24),
  subtext: Color(0xFF5a5a70),
  accent: Color(0xFF5a48d0),
  accent2: Color(0xFF2d88d4),
  success: Color(0xFF2d9e68),
  warn: Color(0xFFd98218),
  danger: Color(0xFFd94c4c),
  shadow: Color(0x22000000),
  gridOrig: Color(0xFFe5e5ea),
  gridTrans: Color(0x555a48d0),
  axis: Color(0xFFc0c0c8),
  origShape: Color(0xFFa0a0b0),
  shapeFill: Color(0x559e75df),
  shapeOutline: Color(0xFF9e75df),
  vertexPalette: [
    Color(0xFFd65a9f),
    Color(0xFFd98218),
    Color(0xFF9e75df),
    Color(0xFF2d9e68),
    Color(0xFF2d88d4),
    Color(0xFFb5bf21),
  ],
);

extension ThemeColorsExt on BuildContext {
  AppColors get colors => Theme.of(this).brightness == Brightness.dark ? darkColors : lightColors;
}

class AppTheme {
  static ThemeData get darkTheme {
    return _buildTheme(Brightness.dark, darkColors);
  }

  static ThemeData get lightTheme {
    return _buildTheme(Brightness.light, lightColors);
  }

  static ThemeData _buildTheme(Brightness brightness, AppColors colors) {
    return ThemeData(
      brightness: brightness,
      scaffoldBackgroundColor: colors.bg,
      fontFamily: 'Segoe UI',
      colorScheme: ColorScheme.fromSeed(
        seedColor: colors.accent,
        brightness: brightness,
        surface: colors.panel,
        error: colors.danger,
      ),
      cardTheme: CardTheme(
        color: colors.card,
        elevation: brightness == Brightness.dark ? 4 : 2,
        shadowColor: colors.shadow,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(10)),
        ),
      ),
      sliderTheme: SliderThemeData(
        activeTrackColor: colors.accent,
        inactiveTrackColor: colors.cardAlt,
        thumbColor: colors.accent,
        overlayColor: colors.accent.withOpacity(0.2),
        trackHeight: 4,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colors.cardAlt,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.border, width: 1),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.border, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.accent, width: 1.5),
        ),
        labelStyle: TextStyle(color: colors.subtext, fontSize: 12),
        hintStyle: TextStyle(color: colors.subtext, fontSize: 12),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: colors.accent,
          foregroundColor: brightness == Brightness.dark ? colors.bg : Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: colors.accent,
        ),
      ),
      dropdownMenuTheme: DropdownMenuThemeData(
        textStyle: TextStyle(color: colors.text, fontSize: 13),
        menuStyle: MenuStyle(
          backgroundColor: WidgetStatePropertyAll(colors.card),
          elevation: const WidgetStatePropertyAll(8),
        ),
      ),
    );
  }
}
