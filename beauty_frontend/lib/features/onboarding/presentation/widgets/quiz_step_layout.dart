import 'package:flutter/material.dart';
import '../../../../shared/widgets/quiz_option_card.dart';
import '../screens/onboarding_quiz_screen.dart';

class QuizStepLayout extends StatelessWidget {
  final String title;
  final String subtitle;
  final List<QuizOption> options;
  final String? selectedOption;
  final List<String>? selectedOptions; // For chip (multi-select) mode
  final Function(dynamic) onOptionSelected;
  final bool isChipMode;

  const QuizStepLayout({
    super.key,
    required this.title,
    required this.subtitle,
    required this.options,
    required this.onOptionSelected,
    this.selectedOption,
    this.selectedOptions,
    this.isChipMode = false,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontSize: 28,
                ),
          ),
          if (subtitle.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
          const SizedBox(height: 32),
          Expanded(
            child: isChipMode
                ? SingleChildScrollView(
                    child: Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: options.map((option) {
                        final currentList = selectedOptions ?? [];
                        final isSelected = currentList.contains(option.title);
                        return IntrinsicWidth(
                          child: QuizOptionCard(
                            title: option.title,
                            subtitle: option.description,
                            isSelected: isSelected,
                            isChipMode: true,
                            onTap: () {
                              // Toggle: add if absent, remove if present
                              final updated = List<String>.from(currentList);
                              if (isSelected) {
                                updated.remove(option.title);
                              } else {
                                updated.add(option.title);
                              }
                              onOptionSelected(updated);
                            },
                          ),
                        );
                      }).toList(),
                    ),
                  )
                : ListView.separated(
                    itemCount: options.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 16),
                    itemBuilder: (context, index) {
                      final option = options[index];
                      return QuizOptionCard(
                        title: option.title,
                        subtitle: option.description,
                        isSelected: selectedOption == option.title,
                        onTap: () => onOptionSelected(option.title),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
