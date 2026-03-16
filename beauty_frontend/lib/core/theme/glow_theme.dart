import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class GlowTheme {
  // Brand Colors (Cashmere Cream Design System)
  static const Color pearlWhite = Color(0xFFFAF8F5);
  static const Color champagneGold = Color(0xFFF3C382);
  static const Color deepTaupe = Color(0xFF4A4138);
  static const Color oatmeal = Color(0xFFD4CABA);
  static const Color pureWhite = Color(0xFFFFFFFF);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: pearlWhite,
      appBarTheme: const AppBarTheme(
        backgroundColor: pearlWhite,
        elevation: 0,
        scrolledUnderElevation: 0,
        iconTheme: IconThemeData(color: deepTaupe),
      ),
      colorScheme: ColorScheme.fromSeed(
        seedColor: champagneGold,
        primary: champagneGold,
        secondary: deepTaupe,
        surface: pearlWhite,
        onSurface: deepTaupe,
      ),
      textTheme: GoogleFonts.plusJakartaSansTextTheme().copyWith(
        displayLarge: GoogleFonts.playfairDisplay(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: deepTaupe,
        ),
        displayMedium: GoogleFonts.playfairDisplay(
          fontSize: 28,
          fontWeight: FontWeight.w600,
          color: deepTaupe,
        ),
        titleLarge: GoogleFonts.playfairDisplay(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: deepTaupe,
        ),
        bodyLarge: GoogleFonts.plusJakartaSans(
          fontSize: 16,
          color: deepTaupe,
          fontWeight: FontWeight.w500,
        ),
        bodyMedium: GoogleFonts.plusJakartaSans(
          fontSize: 14,
          color: deepTaupe.withAlpha(180), // Muted for subtitles
        ),
      ),
      cardTheme: CardTheme(
        color: pureWhite,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: oatmeal, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: champagneGold,
          foregroundColor: deepTaupe,
          minimumSize: const Size(double.infinity, 56),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
          textStyle: GoogleFonts.plusJakartaSans(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
