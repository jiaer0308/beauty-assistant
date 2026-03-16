import 'package:flutter/material.dart';
import '../../../../core/theme/glow_theme.dart';

class QuizOptionCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool isSelected;
  final bool isChipMode;

  const QuizOptionCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.isSelected = false,
    this.isChipMode = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isChipMode) {
      return InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(24),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? GlowTheme.champagneGold : GlowTheme.pureWhite,
            borderRadius: BorderRadius.circular(24),
            border: isSelected 
                ? null 
                : Border.all(color: GlowTheme.oatmeal, width: 1.0),
          ),
          child: Text(
            title,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: GlowTheme.deepTaupe,
            ),
          ),
        ),
      );
    }

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: GlowTheme.pureWhite,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? GlowTheme.champagneGold : GlowTheme.oatmeal,
            width: isSelected ? 2.0 : 1.0,
          ),
          boxShadow: const [], // Strict rule: No shadows
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontSize: 18,
                      color: GlowTheme.deepTaupe,
                    ),
                  ),
                  if (subtitle.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: GlowTheme.deepTaupe.withAlpha(150),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            if (isSelected)
              const Icon(
                Icons.check_circle,
                color: GlowTheme.champagneGold,
                size: 28,
              ),
          ],
        ),
      ),
    );
  }
}
