import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../../core/theme/glow_theme.dart';
import '../../../camera/presentation/widgets/product_match_card.dart';
import '../providers/favorites_provider.dart';
import 'package:go_router/go_router.dart';

class FavoritesScreen extends ConsumerStatefulWidget {
  const FavoritesScreen({super.key});

  @override
  ConsumerState<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends ConsumerState<FavoritesScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    // Check if we reached the bottom thresholds
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(favoritesProvider.notifier).fetchNextPage();
    }
  }

  @override
  Widget build(BuildContext context) {
    final favoritesState = ref.watch(favoritesProvider);

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          'FAVORITES',
          style: GoogleFonts.playfairDisplay(
            color: GlowTheme.deepTaupe,
            letterSpacing: 2.0,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
        iconTheme: const IconThemeData(color: GlowTheme.deepTaupe),
      ),
      body: favoritesState.when(
        data: (state) {
          if (state.items.isEmpty) {
            return _buildEmptyState();
          }

          return CustomScrollView(
            controller: _scrollController,
            slivers: [
              SliverPadding(
                padding: const EdgeInsets.symmetric(
                    horizontal: 24.0, vertical: 16.0),
                sliver: SliverGrid(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 0.52,
                  ),
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final item = state.items[index];
                      final productRec = item.toProductRecommendation();
                      return Stack(
                        children: [
                          ProductMatchCard(
                            product: productRec,
                            onTap: () => context.push('/ar-tryon', extra: {
                              'dashboardProducts': [productRec],
                              'selectedId': productRec.id,
                            }),
                          ),
                          Positioned(
                            top: 8,
                            right: 8,
                            child: Material(
                              color: Colors.white.withValues(alpha: 0.8),
                              shape: const CircleBorder(),
                              elevation: 2,
                              child: IconButton(
                                iconSize: 20,
                                icon: const Icon(
                                  Icons.favorite,
                                  color: GlowTheme.deepTaupe,
                                ),
                                onPressed: () {
                                  ref
                                      .read(favoritesProvider.notifier)
                                      .removeFavorite(item.id);
                                },
                              ),
                            ),
                          ),
                        ],
                      );
                    },
                    childCount: state.items.length,
                  ),
                ),
              ),
              if (state.isLoadingMore)
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 24.0),
                    child: Center(
                      child: CircularProgressIndicator(
                          color: GlowTheme.deepTaupe),
                    ),
                  ),
                ),
              if (!state.hasNext && state.items.isNotEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 24.0),
                    child: Center(
                      child: Text(
                        "You've reached the end, go discover more!",
                        style: GoogleFonts.plusJakartaSans(
                          color: GlowTheme.deepTaupe.withValues(alpha: 0.5),
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(color: GlowTheme.deepTaupe),
        ),
        error: (err, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline,
                  color: GlowTheme.deepTaupe, size: 48),
              const SizedBox(height: 16),
              Text(
                'Failed to load favorites',
                style: GoogleFonts.plusJakartaSans(
                    color: GlowTheme.deepTaupe, fontSize: 16),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  ref.read(favoritesProvider.notifier).refresh();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: GlowTheme.deepTaupe,
                ),
                child: const Text('Retry', style: TextStyle(color: Colors.white)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.favorite_border,
              size: 64, color: GlowTheme.champagneGold),
          const SizedBox(height: 24),
          Text(
            'No Favorites Yet',
            style: GoogleFonts.playfairDisplay(
              fontSize: 28,
              color: GlowTheme.deepTaupe,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Discover products you love and\nsave them here.',
            textAlign: TextAlign.center,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 14,
              color: GlowTheme.deepTaupe.withValues(alpha: 0.7),
            ),
          ),
        ],
      ),
    );
  }
}
