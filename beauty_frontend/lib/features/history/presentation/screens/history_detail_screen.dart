import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../../../core/theme/glow_theme.dart';
import '../../../camera/data/models/color_analysis_response.dart';
import '../../../camera/presentation/widgets/product_match_card.dart';
import '../../data/models/history_models.dart';
import '../providers/history_provider.dart';

class HistoryDetailScreen extends ConsumerWidget {
  final int sessionId;

  const HistoryDetailScreen({super.key, required this.sessionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(historyDetailProvider(sessionId));

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: GlowTheme.deepTaupe),
          onPressed: () => context.pop(),
        ),
        centerTitle: true,
        title: Text(
          'ARCHIVE DETAIL',
          style: GoogleFonts.plusJakartaSans(
            color: GlowTheme.deepTaupe,
            fontSize: 11,
            letterSpacing: 2.0,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: detailAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: GlowTheme.champagneGold),
        ),
        error: (err, _) => _buildErrorState(context, ref),
        data: (detail) => _buildContent(context, detail),
      ),
    );
  }

  // ── Content ───────────────────────────────────────────────────────────────

  Widget _buildContent(BuildContext context, HistorySessionDetail detail) {
    final products = detail.asProductRecommendations;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeroHeader(detail),
          const SizedBox(height: 24),

          if (products.isEmpty)
            _buildNoProductsState()
          else ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Recommended Products',
                    style: GoogleFonts.playfairDisplay(
                      color: GlowTheme.deepTaupe,
                      fontSize: 22,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(height: 1, width: 64, color: GlowTheme.oatmeal),
                  const SizedBox(height: 6),
                  Text(
                    'Tap any product to try it on with AR',
                    style: GoogleFonts.plusJakartaSans(
                      color: GlowTheme.deepTaupe.withOpacity(0.55),
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 20),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  childAspectRatio: 0.55,
                ),
                itemCount: products.length,
                itemBuilder: (context, index) {
                  return ProductMatchCard(
                    product: products[index],
                    onTap: () => _onProductTap(context, products, products[index]),
                  );
                },
              ),
            ),
            const SizedBox(height: 48),
          ],
        ],
      ),
    );
  }

  // ── Hero header ───────────────────────────────────────────────────────────

  Widget _buildHeroHeader(HistorySessionDetail detail) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    final d = detail.createdAt;
    final dateStr = '${months[d.month - 1]} ${d.day}, ${d.year}';
    final analysisLabel = detail.analysisType
        .split('_')
        .map((w) => w.isEmpty
            ? ''
            : '${w[0].toUpperCase()}${w.substring(1).toLowerCase()}')
        .join(' ');

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(24, 0, 24, 0),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: GlowTheme.oatmeal.withOpacity(0.18),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: GlowTheme.oatmeal, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            detail.seasonDisplayName.toUpperCase(),
            style: GoogleFonts.plusJakartaSans(
              color: GlowTheme.deepTaupe,
              fontSize: 10,
              letterSpacing: 2.0,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            detail.seasonDisplayName,
            style: GoogleFonts.playfairDisplay(
              color: GlowTheme.deepTaupe,
              fontSize: 28,
              fontStyle: FontStyle.italic,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _metaChip(Icons.calendar_today_outlined, dateStr),
              const SizedBox(width: 8),
              // _metaChip(Icons.auto_awesome, analysisLabel),
              // const SizedBox(width: 8),
              _metaChip(
                Icons.checkroom_outlined,
                '${detail.itemCount} product${detail.itemCount == 1 ? '' : 's'}',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metaChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: GlowTheme.oatmeal, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 11, color: GlowTheme.deepTaupe.withOpacity(0.6)),
          const SizedBox(width: 4),
          Text(
            label,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 10,
              color: GlowTheme.deepTaupe.withOpacity(0.7),
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  // ── AR entry with permission check (Task 3.2 core) ────────────────────────

  Future<void> _onProductTap(
    BuildContext context,
    List<ProductRecommendation> allProducts,
    ProductRecommendation tapped,
  ) async {
    // 1. Check camera permission
    final status = await Permission.camera.status;

    if (status.isGranted) {
      if (context.mounted) _launchAr(context, allProducts, tapped.id);
      return;
    }

    if (status.isPermanentlyDenied) {
      if (context.mounted) {
        _showPermanentDeniedDialog(context);
      }
      return;
    }

    // 2. Request permission
    final result = await Permission.camera.request();

    if (!context.mounted) return;

    if (result.isGranted) {
      _launchAr(context, allProducts, tapped.id);
    } else if (result.isPermanentlyDenied) {
      _showPermanentDeniedDialog(context);
    } else {
      // Denied but not permanently — show 2D fallback option
      _showDeniedDialog(context, allProducts, tapped);
    }
  }

  void _launchAr(
    BuildContext context,
    List<ProductRecommendation> allProducts,
    int selectedId,
  ) {
    context.push('/ar-tryon', extra: {
      'dashboardProducts': allProducts,
      'selectedId': selectedId,
    });
  }

  /// Camera permission denied (not permanently) — offer 2D fallback.
  void _showDeniedDialog(
    BuildContext context,
    List<ProductRecommendation> allProducts,
    ProductRecommendation product,
  ) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: GlowTheme.pearlWhite,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(
          'Camera Access Needed',
          style: GoogleFonts.playfairDisplay(
            color: GlowTheme.deepTaupe,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Text(
          'Camera access is required for the AR try-on experience. '
          'You can view a 2D product preview instead.',
          style: GoogleFonts.plusJakartaSans(
            color: GlowTheme.deepTaupe.withOpacity(0.8),
            height: 1.5,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(
              'Cancel',
              style: GoogleFonts.plusJakartaSans(
                color: GlowTheme.deepTaupe.withOpacity(0.6),
              ),
            ),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: GlowTheme.deepTaupe,
              foregroundColor: GlowTheme.pearlWhite,
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () {
              Navigator.of(ctx).pop();
              if (context.mounted) {
                _showProductPreviewSheet(context, product);
              }
            },
            child: Text(
              'View 2D Preview',
              style: GoogleFonts.plusJakartaSans(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  /// Camera permanently denied — direct the user to device settings.
  void _showPermanentDeniedDialog(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: GlowTheme.pearlWhite,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(
          'Camera Permission Required',
          style: GoogleFonts.playfairDisplay(
            color: GlowTheme.deepTaupe,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Text(
          'Camera access has been permanently denied. '
          'Please enable it in your device Settings to use AR try-on.',
          style: GoogleFonts.plusJakartaSans(
            color: GlowTheme.deepTaupe.withOpacity(0.8),
            height: 1.5,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(
              'Not Now',
              style: GoogleFonts.plusJakartaSans(
                  color: GlowTheme.deepTaupe.withOpacity(0.6)),
            ),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: GlowTheme.deepTaupe,
              foregroundColor: GlowTheme.pearlWhite,
              elevation: 0,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () {
              Navigator.of(ctx).pop();
              openAppSettings();
            },
            child: Text(
              'Open Settings',
              style: GoogleFonts.plusJakartaSans(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  // ── 2D Product preview bottom sheet (graceful AR fallback) ────────────────

  void _showProductPreviewSheet(
      BuildContext context, ProductRecommendation product) {
    final imageUrl = product.imageUrl.startsWith('//')
        ? 'https:${product.imageUrl}'
        : product.imageUrl;

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        decoration: const BoxDecoration(
          color: GlowTheme.pearlWhite,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Drag handle
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    margin: const EdgeInsets.only(bottom: 24),
                    decoration: BoxDecoration(
                      color: GlowTheme.oatmeal,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),

                // Product image
                if (imageUrl.isNotEmpty && imageUrl != 'url')
                  ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Image.network(
                      imageUrl,
                      height: 220,
                      width: double.infinity,
                      fit: BoxFit.contain,
                      errorBuilder: (_, __, ___) => Container(
                        height: 220,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: GlowTheme.oatmeal.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Icon(
                          Icons.image_not_supported_outlined,
                          size: 64,
                          color: GlowTheme.oatmeal,
                        ),
                      ),
                    ),
                  ),
                const SizedBox(height: 20),

                // Brand
                Text(
                  product.brand.toUpperCase(),
                  style: const TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    color: GlowTheme.deepTaupe,
                    fontSize: 10,
                    letterSpacing: 1.5,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),

                // Product name
                Text(
                  product.name,
                  style: const TextStyle(
                    fontFamily: 'PlayfairDisplay',
                    color: GlowTheme.deepTaupe,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),

                // Shade
                if (product.shade.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      if (product.hexCode != null) ...[
                        Container(
                          width: 14,
                          height: 14,
                          decoration: BoxDecoration(
                            color: _hexToColor(product.hexCode!),
                            shape: BoxShape.circle,
                            border: Border.all(
                                color: GlowTheme.oatmeal, width: 1),
                          ),
                        ),
                        const SizedBox(width: 6),
                      ],
                      Text(
                        product.shade,
                        style: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          color: GlowTheme.deepTaupe.withOpacity(0.7),
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ],

                const SizedBox(height: 8),

                // "No camera" notice
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: GlowTheme.oatmeal.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.info_outline,
                          size: 14, color: GlowTheme.deepTaupe),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Enable camera access to experience the full AR try-on.',
                          style: GoogleFonts.plusJakartaSans(
                            fontSize: 11,
                            color: GlowTheme.deepTaupe.withOpacity(0.7),
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  Color _hexToColor(String hex) {
    try {
      final s = hex.replaceFirst('#', '');
      return Color(int.parse(s.length == 6 ? 'FF$s' : s, radix: 16));
    } catch (_) {
      return GlowTheme.champagneGold;
    }
  }

  Widget _buildNoProductsState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 32),
        child: Column(
          children: [
            const Icon(Icons.shopping_bag_outlined,
                size: 48, color: GlowTheme.oatmeal),
            const SizedBox(height: 16),
            Text(
              'No products in this session',
              style: GoogleFonts.playfairDisplay(
                color: GlowTheme.deepTaupe,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'This archive does not have any product recommendations.',
              textAlign: TextAlign.center,
              style: GoogleFonts.plusJakartaSans(
                color: GlowTheme.deepTaupe.withOpacity(0.6),
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.cloud_off_outlined,
                size: 48, color: GlowTheme.oatmeal),
            const SizedBox(height: 16),
            Text(
              'Could not load session',
              style: GoogleFonts.playfairDisplay(
                color: GlowTheme.deepTaupe,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.refresh(historyDetailProvider(sessionId)),
              style: ElevatedButton.styleFrom(
                backgroundColor: GlowTheme.deepTaupe,
                foregroundColor: GlowTheme.pearlWhite,
              ),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}
