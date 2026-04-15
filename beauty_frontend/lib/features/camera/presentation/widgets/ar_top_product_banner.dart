import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../ar_tryon/data/models/ar_shade_model.dart';
import '../../../favorites/presentation/providers/favorites_provider.dart';

/// Top-of-screen banner that shows the currently active shade's brand and
/// product details inside the AR Try-On view.
///
/// Accepts a nullable [selectedShade]. When null (initial loading) the text
/// areas are replaced by subtle oatmeal-tinted placeholders that blend
/// naturally into the Cashmere Cream design system without any hard spinner.
class ArTopProductBanner extends ConsumerWidget {
  final ArShadeModel? selectedShade;

  const ArTopProductBanner({
    super.key,
    required this.selectedShade,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favoritesState = ref.watch(favoritesProvider);
    final cosmeticId = selectedShade?.cosmeticId ?? selectedShade?.productId ?? 0;
    
    final isFavorited = selectedShade != null &&
        favoritesState.value?.items.any((e) => e.id == cosmeticId) == true;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
        child: Container(
          decoration: BoxDecoration(
            color: GlowTheme.pearlWhite,
            borderRadius: BorderRadius.circular(16.0),
            border: Border.all(color: GlowTheme.oatmeal, width: 1.0),
          ),
          padding:
              const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: selectedShade == null
                    ? _buildLoadingState()
                    : _buildShadeInfo(selectedShade!),
              ),
              if (selectedShade != null)
                IconButton(
                  onPressed: () {
                    final notifier = ref.read(favoritesProvider.notifier);
                    if (isFavorited) {
                      notifier.removeFavorite(cosmeticId);
                    } else {
                      notifier.addFavorite(cosmeticId);
                    }
                  },
                  icon: Icon(
                    isFavorited ? Icons.favorite : Icons.favorite_border,
                    color: GlowTheme.deepTaupe,
                  ),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
            ],
          ),
        ),
      ),
    );
  }

  /// Populated state: brand name in caps + "Product Name - Shade Name" below.
  Widget _buildShadeInfo(ArShadeModel shade) {
    final subtitle = '${shade.productName} – ${shade.shadeName}';
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          shade.brandName.toUpperCase(),
          style: const TextStyle(
            color: GlowTheme.deepTaupe,
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: TextStyle(
            fontFamily: 'PlayfairDisplay',
            color: GlowTheme.deepTaupe.withValues(alpha: 0.75),
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  /// Null / loading state: two muted oatmeal bars that mimic text dimensions
  /// without any jarring spinner, staying true to the zero-elevation aesthetic.
  Widget _buildLoadingState() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 80,
          height: 10,
          decoration: BoxDecoration(
            color: GlowTheme.oatmeal.withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(height: 6),
        Container(
          width: 140,
          height: 8,
          decoration: BoxDecoration(
            color: GlowTheme.oatmeal.withValues(alpha: 0.35),
            borderRadius: BorderRadius.circular(4),
          ),
        ),
      ],
    );
  }
}
