import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../data/models/color_analysis_response.dart';

/// Category IDs that support the AR lip effect.
const Set<int> _arCompatibleCategoryIds = {6, 7, 8};

class ProductMatchCard extends StatelessWidget {
  final ProductRecommendation product;
  /// Caller must provide onTap — the card does not navigate on its own
  /// because it needs access to the full product list for Single Product Mode.
  /// If null or the product is not AR-compatible, the card will be non-interactive.
  final VoidCallback? onTap;

  const ProductMatchCard({
    super.key, 
    required this.product,
    this.onTap,
  });

  bool get _isArCompatible {
    final id = product.categoryId;
    return id != null && _arCompatibleCategoryIds.contains(id);
  }

  @override
  Widget build(BuildContext context) {
    final imageUrl = product.imageUrl.startsWith('//')
        ? 'https:${product.imageUrl}'
        : product.imageUrl;

    return Semantics(
      button: _isArCompatible,
      label: '${product.brand} ${product.name}, ${product.shade}',
      child: Opacity(
        opacity: _isArCompatible ? 1.0 : 0.65,
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: _isArCompatible ? GlowTheme.oatmeal : GlowTheme.oatmeal.withValues(alpha: 0.5),
              width: 1.5,
            ),
          ),
          clipBehavior: Clip.antiAlias,
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              // Only trigger tap if AR-compatible
              onTap: _isArCompatible ? onTap : null,
              splashColor: _isArCompatible
                  ? GlowTheme.champagneGold.withValues(alpha: 0.1)
                  : Colors.transparent,
              highlightColor: Colors.black.withValues(alpha: 0.02),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 1. Top image area
                  AspectRatio(
                    aspectRatio: 1.0,
                    child: Stack(
                      children: [
                        Container(
                          color: GlowTheme.pearlWhite,
                          child: _buildImage(imageUrl),
                        ),
                        // AR-not-supported lock overlay
                        if (!_isArCompatible)
                          Positioned.fill(
                            child: Container(
                              color: Colors.black.withValues(alpha: 0.25),
                              child: const Center(
                                child: Icon(
                                  Icons.no_photography_outlined,
                                  color: Colors.white,
                                  size: 28,
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),

                  // 2. Text area
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.all(10.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Brand + icon
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: Text(
                                  product.brand.toUpperCase(),
                                  style: const TextStyle(
                                    fontFamily: 'Plus Jakarta Sans',
                                    color: GlowTheme.deepTaupe,
                                    fontSize: 10,
                                    letterSpacing: 1.0,
                                    fontWeight: FontWeight.w700,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              Padding(
                                padding: const EdgeInsets.only(left: 4.0),
                                child: Icon(
                                  _isArCompatible ? Icons.auto_awesome : Icons.block,
                                  color: _isArCompatible
                                      ? GlowTheme.champagneGold
                                      : GlowTheme.deepTaupe.withValues(alpha: 0.4),
                                  size: 12,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),

                          // Product name
                          Text(
                            product.name,
                            style: GoogleFonts.playfairDisplay(
                              color: GlowTheme.deepTaupe,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              height: 1.2,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 4),

                          // Shade / "No AR" message
                          if (_isArCompatible)
                            Text(
                              product.shade,
                              style: TextStyle(
                                fontSize: 10,
                                color: GlowTheme.deepTaupe.withValues(alpha: 0.6),
                                fontWeight: FontWeight.w400,
                                fontStyle: FontStyle.italic,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            )
                          else
                            Text(
                              'No AR Try On support',
                              style: TextStyle(
                                fontSize: 9,
                                color: GlowTheme.deepTaupe.withValues(alpha: 0.5),
                                fontWeight: FontWeight.w500,
                                fontStyle: FontStyle.italic,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildImage(String url) {
    if (url.isEmpty || url == 'url') {
      return Center(
        child: Icon(Icons.inventory_2_outlined, color: GlowTheme.oatmeal.withValues(alpha: 0.5), size: 48),
      );
    }

    return Image.network(
      url,
      fit: BoxFit.cover,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return Center(
          child: CircularProgressIndicator(
            value: loadingProgress.expectedTotalBytes != null
                ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                : null,
            strokeWidth: 2,
            color: GlowTheme.oatmeal,
          ),
        );
      },
      errorBuilder: (context, error, stackTrace) => Center(
        child: Icon(Icons.image_not_supported, color: GlowTheme.oatmeal.withValues(alpha: 0.5), size: 48),
      ),
    );
  }
}
