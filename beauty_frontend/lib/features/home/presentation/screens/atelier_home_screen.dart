import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../../core/constants/season_constants.dart';
import '../../../camera/data/models/color_analysis_response.dart';
import '../../../camera/presentation/widgets/product_match_card.dart';
import '../providers/dashboard_provider.dart';
import 'package:go_router/go_router.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/models/auth_state.dart';
import '../../../auth/presentation/widgets/auth_bottom_sheet.dart';

// ✅ 增加一个简单的 String 扩展，用于处理首字母大写和替换下划线
extension StringExtension on String {
  String toTitleCase() {
    return split('_').map((word) => word.isNotEmpty 
      ? '${word[0].toUpperCase()}${word.substring(1).toLowerCase()}' 
      : '').join(' ');
  }
}

class AtelierHomeScreen extends ConsumerWidget {
  const AtelierHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardState = ref.watch(dashboardProvider);
    
    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.account_circle, color: GlowTheme.deepTaupe),
          onPressed: () => context.push('/profile'),
        ),
        centerTitle: true,
        title: Text(
          'ATELIER',
          style: GoogleFonts.playfairDisplay(
            color: GlowTheme.deepTaupe,
            letterSpacing: 2.0,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history, color: GlowTheme.deepTaupe),
            onPressed: () => context.push('/history'),
          ),
        ],
      ),
      body: () {
        // Show full screen loader only if there's no existing data
        if (dashboardState.isLoading && !dashboardState.hasValue) {
          return const Center(
            child: CircularProgressIndicator(color: GlowTheme.deepTaupe),
          );
        } else if (dashboardState.hasError && !dashboardState.hasValue) {
          return _buildEmptyState(context);
        } else {
          final dashboardData = dashboardState.value;
          if (dashboardData != null && dashboardData.result != null) {
             final isRefreshing = dashboardState.isLoading;
             return _buildDashboard(dashboardData.toColorAnalysisResponse(), isRefreshing);
          }
          return _buildEmptyState(context);
        }
      }()
    );
  }

  Widget _buildDashboard(ColorAnalysisResponse analysisData, bool isRefreshing) {
    final rawSeasonName = analysisData.result?.displayName ?? 'unknown';
    final displaySeasonName = rawSeasonName.toTitleCase();

    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 16),
            HeroIdentityCard(analysisData: analysisData),
            const SizedBox(height: 24),
            const OnboardingActionPanel(),
            const SizedBox(height: 40),
            CuratedGridSection(seasonName: displaySeasonName, analysisData: analysisData, isRefreshing: isRefreshing),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.face_retouching_natural, size: 64, color: GlowTheme.champagneGold),
            const SizedBox(height: 24),
            Text(
              'Discover Your Colors',
              style: GoogleFonts.playfairDisplay(
                fontSize: 28,
                color: GlowTheme.deepTaupe,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              'Complete your Seasonal Color Analysis to unlock personalized makeup recommendations.',
              style: GoogleFonts.plusJakartaSans(
                fontSize: 14,
                color: GlowTheme.deepTaupe.withValues(alpha: 0.7),
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () => context.push('/onboarding'),
              style: ElevatedButton.styleFrom(
                backgroundColor: GlowTheme.deepTaupe,
                foregroundColor: GlowTheme.pearlWhite,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              ),
              child: Text(
                'START ANALYSIS',
                style: GoogleFonts.plusJakartaSans(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  fontSize: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class OnboardingActionPanel extends StatelessWidget {
  const OnboardingActionPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: GlowTheme.oatmeal.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: GlowTheme.oatmeal, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.star_rounded, color: GlowTheme.deepTaupe),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Complete Your Profile',
                  style: GoogleFonts.playfairDisplay(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: GlowTheme.deepTaupe,
                  ),
                  softWrap: true,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'Tell us more about your skin type, concerns, and makeup preferences for highly personalized product matches.',
            style: GoogleFonts.plusJakartaSans(
              fontSize: 14,
              color: GlowTheme.deepTaupe.withValues(alpha: 0.8),
              height: 1.5,
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => context.push('/onboarding'),
            style: ElevatedButton.styleFrom(
              backgroundColor: GlowTheme.deepTaupe,
              foregroundColor: GlowTheme.pearlWhite,
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
            child: Text(
              'TAKE THE QUIZ',
              style: GoogleFonts.plusJakartaSans(
                fontWeight: FontWeight.bold,
                letterSpacing: 1.0,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class HeroIdentityCard extends StatelessWidget {
  final ColorAnalysisResponse? analysisData;
  const HeroIdentityCard({super.key, this.analysisData});

  @override
  Widget build(BuildContext context) {
    final rawSeasonName = analysisData?.result?.displayName ?? 'unknown';
    final seasonColor = SeasonTheme.getSeasonColor(rawSeasonName); 
    final displaySeasonName = rawSeasonName.toTitleCase();

    return Container(
      width: double.infinity,
      height: 250,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        color: seasonColor,
      ),
      child: Stack(
        fit: StackFit.expand,
        children: [
          Container(color: seasonColor.withValues(alpha: 0.1)),
          DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [
                  Colors.black.withValues(alpha: 0.8),
                  Colors.black.withValues(alpha: 0.0),
                ],
                stops: const [0.0, 0.5],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(32.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Text(
                  'YOUR IDENTITY',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    color: Colors.white,
                    fontSize: 10,
                    letterSpacing: 2.0,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  displaySeasonName, 
                  style: GoogleFonts.playfairDisplay(
                    color: Colors.white,
                    fontSize: 36,
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class CuratedGridSection extends ConsumerWidget {
  final String seasonName;
  final ColorAnalysisResponse? analysisData;
  final bool isRefreshing;

  const CuratedGridSection({
    super.key,
    required this.seasonName,
    this.analysisData,
    this.isRefreshing = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final products = analysisData?.recommendedProducts ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Expanded(
              child: Text(
                'Curated for $seasonName',
                style: GoogleFonts.playfairDisplay(
                  color: GlowTheme.deepTaupe,
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            Container(
              height: 40,
              width: 40,
              alignment: Alignment.center,
              child: isRefreshing 
                ? const SizedBox(
                    width: 20, 
                    height: 20, 
                    child: CircularProgressIndicator(
                      color: GlowTheme.deepTaupe, 
                      strokeWidth: 2
                    )
                  )
                : IconButton(
                    icon: const Icon(Icons.refresh_rounded, color: GlowTheme.deepTaupe),
                    tooltip: 'Refresh recommendations',
                    onPressed: () => ref.read(dashboardProvider.notifier).refresh(),
                  ),
            ),
          ],
        ),
        const SizedBox(height: 8), // 缩减了一点点间距，因为 Button 自身带有 padding
        Container(
          height: 1,
          width: 80,
          color: GlowTheme.oatmeal,
        ),
        const SizedBox(height: 24),
        if (products.isEmpty)
          const Center(
            child: Padding(
              padding: EdgeInsets.symmetric(vertical: 40.0),
              child: Text('No recommendations available yet.'),
            ),
          )
        else
          Stack(
            children: [
              AnimatedOpacity(
                duration: const Duration(milliseconds: 300),
                opacity: isRefreshing ? 0.3 : 1.0,
                child: GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 0.52,
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
                              isMandatory: true,
                              onSuccess: () {
                                context.push('/ar-tryon', extra: {
                                  'dashboardProducts': products,
                                  'selectedId': products[index].id,
                                });
                              },
                            );
                          }
                        },
                      );
                    },
                ),
              ),
            ],
          ),
      ],
    );
  }
}