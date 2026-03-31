import 'package:flutter/material.dart';

class SeasonTheme {
  static const Map<String, Color> seasonColors = {
    'Light Spring': Color(0xFFFDEBB3),
    'True Spring': Color(0xFFF4A261),
    'Bright Spring': Color(0xFFE76F51),
    'Light Summer': Color(0xFFE2C2C6),
    'True Summer': Color(0xFFA1ADC7),
    'Soft Summer': Color(0xFF9CB3A1),
    'Soft Autumn': Color(0xFFD4A373),
    'True Autumn': Color(0xFFCB793A),
    'Dark Autumn': Color(0xFF8B5A2B), // Also known as Deep Autumn
    'Deep Autumn': Color(0xFF8B5A2B),
    'Dark Winter': Color(0xFF55323E),
    'True Winter': Color(0xFF1E3F5A),
    'Bright Winter': Color(0xFF5B3C68),
  };

  static Color getSeasonColor(String? seasonName) {
    if (seasonName == null) return Colors.grey;
    
    // Normalize string for lookup
    final normalized = seasonName.trim();
    
    // Check direct match
    if (seasonColors.containsKey(normalized)) {
      return seasonColors[normalized]!;
    }
    
    // Fuzzy matching (case-insensitive)
    for (var entry in seasonColors.entries) {
      if (entry.key.toLowerCase() == normalized.toLowerCase()) {
        return entry.value;
      }
    }

    return seasonColors['Deep Autumn']!; // Fallback
  }

  static List<Color> get allColors => [
    seasonColors['Light Spring']!,
    seasonColors['True Spring']!,
    seasonColors['Bright Spring']!,
    seasonColors['Light Summer']!,
    seasonColors['True Summer']!,
    seasonColors['Soft Summer']!,
    seasonColors['Soft Autumn']!,
    seasonColors['True Autumn']!,
    seasonColors['Dark Autumn']!,
    seasonColors['Dark Winter']!,
    seasonColors['True Winter']!,
    seasonColors['Bright Winter']!,
  ];
}
