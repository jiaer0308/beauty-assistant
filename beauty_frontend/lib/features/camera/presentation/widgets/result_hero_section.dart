import 'package:flutter/material.dart';
import '../../../../core/theme/glow_theme.dart';

class ResultHeroSection extends StatelessWidget {
  final String displayName;

  const ResultHeroSection({super.key, required this.displayName});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
      child: Center(
        child: RichText(
          textAlign: TextAlign.center,
          text: TextSpan(
            text: 'You are a\n',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w400,
              color: GlowTheme.deepTaupe,
              height: 1.5,
            ),
            children: [
              TextSpan(
                text: displayName,
                style: const TextStyle(
                  fontSize: 36,
                  fontStyle: FontStyle.italic,
                  fontWeight: FontWeight.bold,
                  color: GlowTheme.champagneGold,
                  height: 1.2,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
