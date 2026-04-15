import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../auth/presentation/widgets/auth_bottom_sheet.dart';
import '../../../../features/auth/models/auth_state.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../data/models/color_analysis_response.dart';
import '../widgets/result_hero_section.dart';
import '../widgets/color_swatch_item.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/product_match_card.dart';
import '../widgets/sticky_ar_footer.dart';

class ResultDashboardScreen extends ConsumerWidget {
  final ColorAnalysisResponse? analysisData;

  const ResultDashboardScreen({super.key, this.analysisData});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // If data is null, provide a graceful fallback or empty set
    final data = analysisData ?? ColorAnalysisResponse(success: false);
    final isSuccess = data.success && data.result != null;

    final displayName = isSuccess ? data.result!.displayName : 'Unknown Season';
    final bestColors = data.bestColors;
    final neutralColors = data.neutralColors;
    final avoidColors = data.avoidColors;
    final products = data.recommendedProducts;
    final authState = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: GlowTheme.deepTaupe),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history, color: GlowTheme.deepTaupe),
            onPressed: () => context.push('/history'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // HERO SECTION
            ResultHeroSection(displayName: displayName),

            // BEST COLORS SECTION
            if (bestColors.isNotEmpty) ...[
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
                child: Text(
                  'Your Best Colors',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: GlowTheme.deepTaupe,
                  ),
                ),
              ),
              SizedBox(
                height: 120, // Height to accommodate circle and text
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  scrollDirection: Axis.horizontal,
                  itemCount: bestColors.length,
                  itemBuilder: (context, index) {
                    return ColorSwatchItem(colorInfo: bestColors[index]);
                  },
                ),
              ),
              const SizedBox(height: 24),
            ],

            // NEUTRAL COLORS SECTION
            if (neutralColors.isNotEmpty) ...[
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
                child: Text(
                  'Your Neutral Colors',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: GlowTheme.deepTaupe,
                  ),
                ),
              ),
              SizedBox(
                height: 120,
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  scrollDirection: Axis.horizontal,
                  itemCount: neutralColors.length,
                  itemBuilder: (context, index) {
                    return ColorSwatchItem(colorInfo: neutralColors[index]);
                  },
                ),
              ),
              const SizedBox(height: 24),
            ],

            // AVOID COLORS SECTION
            if (avoidColors.isNotEmpty) ...[
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
                child: Text(
                  'Colors to Avoid',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: GlowTheme.deepTaupe,
                  ),
                ),
              ),
              SizedBox(
                height: 120,
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  scrollDirection: Axis.horizontal,
                  itemCount: avoidColors.length,
                  itemBuilder: (context, index) {
                    return ColorSwatchItem(colorInfo: avoidColors[index]);
                  },
                ),
              ),
              const SizedBox(height: 24),
            ],

            
            // RECOMMENDED PRODUCTS SECTION
            if (products.isNotEmpty) ...[
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
                child: Text(
                  'Recommended Products',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: GlowTheme.deepTaupe,
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: GridView.builder(
                  physics: const NeverScrollableScrollPhysics(),
                  shrinkWrap: true,
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16.0,
                    mainAxisSpacing: 16.0,
                    childAspectRatio: 0.55,
                  ),
                  itemCount: products.length,
                  itemBuilder: (context, index) {
                    return ProductMatchCard(
                      product: products[index],
                      onTap: () {
                        if (authState.status == AuthStatus.authenticated) {
                          context.push('/ar-tryon', extra: {
                            'dashboardProducts': products,
                            'selectedId': products[index].id,
                          });
                        } else {
                          AuthBottomSheet.show(
                            context,
                            discoveredSeason: displayName,
                            isMandatory: true,
                            onSuccess: () {
                              context.push('/ar-tryon', extra: {
                                'dashboardProducts': products,
                                'selectedId': products[index].id,
                                'isNewUserFlow': true,
                              });
                            },
                          );
                        }
                      },
                    );
                  },
                ),
              ),
              const SizedBox(height: 48), // Padding before sticky footer
            ],
            
            // Empty State Handling
            if (bestColors.isEmpty && products.isEmpty)
               const Padding(
                  padding: EdgeInsets.all(32.0),
                  child: Center(
                    child: Text(
                      'No specific recommendations could be generated for your profile at this time.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: GlowTheme.deepTaupe,
                        fontSize: 16,
                      ),
                    ),
                  ),
               ),
          ],
        ),
      ),
      bottomNavigationBar: StickyArFooter(
        label: authState.status == AuthStatus.authenticated
            ? 'To Home Page'
            : 'Try AR Makeup',
        buttonColor: authState.status == AuthStatus.authenticated
            ? GlowTheme.deepTaupe
            : null, // defaults to champagneGold
        foregroundColor: authState.status == AuthStatus.authenticated
            ? GlowTheme.pearlWhite
            : null,
        onPressed: () {
          if (authState.status == AuthStatus.authenticated) {
            context.go('/dashboard');
          } else {
            AuthBottomSheet.show(
              context,
              discoveredSeason: displayName,
              isMandatory: true,
              onSuccess: () {
                context.push('/ar-tryon', extra: {
                  'sessionId': data.sessionId,
                  'isNewUserFlow': true,
                });
              },
            );
          }
        },
      ),
    );
  }
}
