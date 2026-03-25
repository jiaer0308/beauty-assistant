import 'package:flutter/material.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../data/models/color_analysis_response.dart';

class ProductMatchCard extends StatelessWidget {
  final ProductRecommendation product;

  const ProductMatchCard({super.key, required this.product});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: GlowTheme.oatmeal,
          width: 1,
        ),
      ),
      // Set to 0 to strictly avoid any drop shadows per design system rules
      // elevation: 0 conceptually mapped to no boxShadow
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Image / Top Area
          Expanded(
            child: Stack(
              children: [
                // Product Image
                Container(
                  decoration: const BoxDecoration(
                    color: GlowTheme.pearlWhite,
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(11),
                      topRight: Radius.circular(11),
                    ),
                  ),
                  child: Center(
                    child: product.imageUrl.isNotEmpty && product.imageUrl != 'url'
                        ? Image.network(
                            product.imageUrl,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) =>
                                const Icon(Icons.image_not_supported, color: GlowTheme.oatmeal),
                          )
                        : const Icon(Icons.inventory_2_outlined, color: GlowTheme.oatmeal, size: 48),
                  ),
                ),
                // Match Percentage Pill
                // Positioned(
                //   top: 8,
                //   right: 8,
                //   child: Container(
                //     padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                //     decoration: BoxDecoration(
                //       color: GlowTheme.champagneGold,
                //       borderRadius: BorderRadius.circular(16),
                //     ),
                //     child: Text(
                //       '${product.matchPercentage}% MATCH',
                //       style: const TextStyle(
                //         fontSize: 10,
                //         fontWeight: FontWeight.bold,
                //         color: GlowTheme.deepTaupe,
                //       ),
                //     ),
                //   ),
                // ),
              ],
            ),
          ),
          
          // Bottom Text Area
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  product.brand.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: GlowTheme.deepTaupe,
                    letterSpacing: 0.5,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  product.name,
                  style: const TextStyle(
                    fontSize: 14,
                    color: GlowTheme.deepTaupe,
                    fontWeight: FontWeight.w400,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  product.shade,
                  style: const TextStyle(
                    fontSize: 14,
                    color: GlowTheme.deepTaupe,
                    fontWeight: FontWeight.w400,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
