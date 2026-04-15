import 'package:flutter/material.dart';
import '../../../../core/theme/glow_theme.dart';

class StickyArFooter extends StatelessWidget {
  final VoidCallback onPressed;
  final String label;
  final Color? buttonColor;
  final Color? foregroundColor;

  const StickyArFooter({
    super.key,
    required this.onPressed,
    this.label = 'Try AR Makeup',
    this.buttonColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: GlowTheme.pearlWhite,
        border: Border(
          top: BorderSide(
            color: GlowTheme.oatmeal,
            width: 1.0,
          ),
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: ElevatedButton(
            onPressed: onPressed,
            style: ElevatedButton.styleFrom(
              backgroundColor: buttonColor ?? GlowTheme.champagneGold,
              foregroundColor: foregroundColor ?? GlowTheme.deepTaupe,
              elevation: 0,
              minimumSize: const Size.fromHeight(56),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
