import 'package:flutter/material.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../data/models/color_analysis_response.dart';

class ColorSwatchItem extends StatelessWidget {
  final ColorInfo colorInfo;

  const ColorSwatchItem({super.key, required this.colorInfo});

  @override
  Widget build(BuildContext context) {
    // Parse hex string (e.g. "DDA722") to Flutter Color
    final hexString = colorInfo.hex.replaceAll('#', '');
    final color = Color(int.parse('FF$hexString', radix: 16));

    return Padding(
      padding: const EdgeInsets.only(right: 16.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              border: Border.all(
                color: GlowTheme.oatmeal.withAlpha(77), // 30% opacity
                width: 1,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            colorInfo.name.toUpperCase(),
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: GlowTheme.deepTaupe,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}
