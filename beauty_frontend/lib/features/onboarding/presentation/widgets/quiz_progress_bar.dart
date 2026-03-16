import 'package:flutter/material.dart';
import '../../../../core/theme/glow_theme.dart';

class QuizProgressBar extends StatelessWidget {
  final int currentStep;
  final int totalSteps;

  const QuizProgressBar({
    super.key,
    required this.currentStep,
    required this.totalSteps,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'STEP $currentStep OF $totalSteps',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                      color: GlowTheme.deepTaupe.withAlpha(150),
                    ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: List.generate(totalSteps, (index) {
              final isCompleted = index < currentStep;
              return Expanded(
                child: Container(
                  height: 4,
                  margin: EdgeInsets.only(right: index == totalSteps - 1 ? 0 : 4),
                  decoration: BoxDecoration(
                    color: isCompleted ? GlowTheme.champagneGold : GlowTheme.oatmeal,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }
}
