import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../ar_tryon/presentation/providers/ar_tryon_provider.dart';

class ArSwatchBottomPanel extends ConsumerWidget {
  const ArSwatchBottomPanel({super.key});

  /// Parses a CSS-style hex string (with or without leading '#') into a
  /// Flutter [Color]. Returns a warm terracotta fallback if parsing fails.
  Color _hexToColor(String hex) {
    try {
      final sanitised = hex.replaceFirst('#', '');
      final value = int.parse(
        sanitised.length == 6 ? 'FF$sanitised' : sanitised,
        radix: 16,
      );
      return Color(value);
    } catch (_) {
      return const Color(0xFF982A2A); // Deep Autumn fallback
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(arTryonProvider);
    final notifier = ref.read(arTryonProvider.notifier);
    // Cache to avoid calling the getter (which internally .toList()s) twice.
    final filteredShades = state.filteredShades;

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Filter Pill
        Center(
          child: Container(
            margin: const EdgeInsets.only(bottom: 16.0),
            decoration: BoxDecoration(
              color: GlowTheme.pearlWhite.withValues(alpha: 0.9),
              borderRadius: BorderRadius.circular(24.0),
              border: Border.all(color: GlowTheme.oatmeal, width: 1.0),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildFilterButton('My Best Colors', true, state.isBestColorsFilterActive, notifier),
                _buildFilterButton('Explore Collection', false, state.isBestColorsFilterActive, notifier),
              ],
            ),
          ),
        ),

        // Swatches horizontally scrolling row
        SizedBox(
          height: 64,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: EdgeInsets.zero,
            itemCount: filteredShades.length,
            itemBuilder: (context, index) {
              final shade = filteredShades[index];
              final color = _hexToColor(shade.colorHex);
              final isSelected = shade.id == state.selectedShadeId;

              return GestureDetector(
                onTap: () => notifier.selectShade(shade.id),
                child: Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: color,
                    border: isSelected
                        ? Border.all(color: GlowTheme.pearlWhite, width: 2)
                        : null,
                  ),
                  child: isSelected
                      ? Container(
                          margin: const EdgeInsets.all(2),
                          decoration: BoxDecoration(
                            border: Border.all(
                                color: GlowTheme.champagneGold, width: 2),
                          ),
                        )
                      : null,
                ),
              );
            },
          ),
        ),

        // Sephora Navigation Bar
        Container(
          color: GlowTheme.deepTaupe,
          padding: EdgeInsets.only(
            left: 24.0,
            right: 24.0,
            top: 16.0,
            bottom: MediaQuery.of(context).padding.bottom + 16.0,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Left: Category
              GestureDetector(
                onTap: () {
                  _showCategorySheet(context, state.activeCategory, notifier);
                },
                child: Row(
                  children: [
                    Text(
                      state.activeCategory.toUpperCase(),
                      style: const TextStyle(
                        color: GlowTheme.pearlWhite,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(width: 4),
                    const Icon(
                      Icons.keyboard_arrow_up,
                      color: GlowTheme.pearlWhite,
                      size: 20,
                    ),
                  ],
                ),
              ),

              // Center: Camera Shutter
              GestureDetector(
                onTap: () {
                  // Take photo
                },
                child: Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: GlowTheme.pearlWhite, width: 3),
                  ),
                  child: Center(
                    child: Container(
                      width: 44,
                      height: 44,
                      decoration: const BoxDecoration(
                        color: GlowTheme.pearlWhite,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                ),
              ),

              // Right: MY LOOKS
              GestureDetector(
                onTap: () {
                  // View saved looks
                },
                child: const Text(
                  'MY LOOKS',
                  style: TextStyle(
                    color: GlowTheme.pearlWhite,
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                    letterSpacing: 1.2,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFilterButton(String text, bool isBestColors, bool currentActive, ArTryonNotifier notifier) {
    final isActive = currentActive == isBestColors;
    return GestureDetector(
      onTap: () {
        if (!isActive) {
          notifier.toggleFilter();
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
        decoration: BoxDecoration(
          color: isActive ? GlowTheme.champagneGold : Colors.transparent,
          borderRadius: BorderRadius.circular(24.0),
        ),
        child: Text(
          text,
          style: TextStyle(
            color: isActive ? GlowTheme.pearlWhite : GlowTheme.deepTaupe,
            fontWeight: FontWeight.w600,
            fontSize: 12,
          ),
        ),
      ),
    );
  }

  void _showCategorySheet(BuildContext context, String activeCategory, ArTryonNotifier notifier) {
    showModalBottomSheet(
      context: context,
      backgroundColor: GlowTheme.pearlWhite,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24.0)),
      ),
      builder: (sheetContext) {
        final categoryMap = {
          'Lip': 'LIP',
          'Eyeshadow': 'EYE',
          'Blush': 'CHEEK',
          'Remove Makeup': 'NONE',
        };
        final categories = categoryMap.keys.toList();

        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: categories.map((uiCategory) {
                final mappedValue = categoryMap[uiCategory]!;
                final isActive = activeCategory == mappedValue;

                return ListTile(
                  onTap: () {
                    notifier.changeCategory(mappedValue);
                    Navigator.pop(sheetContext); // use builder's context
                  },
                  title: Text(
                    uiCategory,
                    style: TextStyle(
                      color: GlowTheme.deepTaupe,
                      fontSize: 16,
                      fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                  trailing: isActive
                      ? const Icon(Icons.check, color: GlowTheme.champagneGold)
                      : null,
                );
              }).toList(),
            ),
          ),
        );
      },
    );
  }
}
