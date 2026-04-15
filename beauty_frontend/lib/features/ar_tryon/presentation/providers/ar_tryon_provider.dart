import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../features/camera/data/models/color_analysis_response.dart';
import '../../../../features/camera/data/repositories/cosmetic_repository.dart';
import '../../data/models/ar_shade_model.dart';
import '../../data/models/ar_tryon_state.dart';

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

final arTryonProvider =
    StateNotifierProvider<ArTryonNotifier, ArTryonState>((ref) {
  final cosmeticRepo = ref.watch(cosmeticRepositoryProvider);
  return ArTryonNotifier(cosmeticRepo);
});

// ---------------------------------------------------------------------------
// Notifier
// ---------------------------------------------------------------------------

/// Manages the AR Try-On state – shade catalogue, category switching,
/// best-colors filter, and shade selection.
///
/// Supports two entry modes:
/// 1. **SCA Mode** (`recommendations` list provided): converts the
///    recommendation list from the analysis result into AR shades.
///    Each shade carries the hex code already returned by the SCA pipeline.
/// 2. **Dashboard Mode** (`product` provided, no `recommendations`): the
///    single selected product is displayed first; hex codes for all products
///    are fetched from `/api/v1/cosmetics/shades` if IDs are available.


class ArTryonNotifier extends StateNotifier<ArTryonState> {
  final CosmeticRepository _cosmeticRepo;
  
  // Keep all shades in memory mapped by category
  Map<String, List<ArShadeModel>> _categorisedShades = {
    'LIP': [],
    'CHEEK': [],
    'EYE': [],
  };

  ArTryonNotifier(this._cosmeticRepo) : super(ArTryonState.initial());

  // ── Public API ──────────────────────────────────────────────────────────

  Future<void> init({
    int? sessionId,
    List<ProductRecommendation>? dashboardProducts,
    int? selectedDashboardId,
  }) async {
    state = state.copyWith(
      isLoading: true,
      isBestColorsFilterActive: true, // Reset to default when entering screen
    );

    // Branch 1 (Session Mode): sessionId is provided, selectedDashboardId is null
    if (sessionId != null && selectedDashboardId == null) {
      state = state.copyWith(isSessionMode: true);
      await _initFromSession(sessionId);
      return;
    }

    // Branch 2 (Single Product Mode): selectedDashboardId is provided
    if (selectedDashboardId != null && dashboardProducts != null && dashboardProducts.isNotEmpty) {
      state = state.copyWith(isSessionMode: false);
      await _initFromDashboard(dashboardProducts, selectedDashboardId);
      return;
    }

    state = state.copyWith(isLoading: false);
  }

  // ── Filter & selection ──────────────────────────────────────────────────

  void toggleFilter() {
    final newFilterState = !state.isBestColorsFilterActive;
    final categoryShades = _categorisedShades[state.activeCategory] ?? [];
    
    if (newFilterState) {
      // Toggling BACK to "My Best Colors"
      // 1. Restore the full category list so the getter can filter them all
      // 2. See if the currently selected shade is still a "best color"
      final currentlySelected = categoryShades.cast<ArShadeModel?>().firstWhere(
        (s) => s?.id == state.selectedShadeId, 
        orElse: () => null
      );
      
      String? newSelectedId = state.selectedShadeId;
      if (currentlySelected == null || !currentlySelected.isBestColor) {
        // Fallback to the first available "best color" in this category
        final bestColors = categoryShades.where((s) => s.isBestColor).toList();
        newSelectedId = bestColors.isNotEmpty ? bestColors.first.id : null;
      }
      
      state = state.copyWith(
        isBestColorsFilterActive: true,
        allShades: categoryShades,
        selectedShadeId: newSelectedId,
      );
    } else {
      // Toggling TO "Explore Collection"
      final currentlySelected = categoryShades.cast<ArShadeModel?>().firstWhere(
        (s) => s?.id == state.selectedShadeId, 
        orElse: () => null
      );
      
      if (currentlySelected != null) {
        final productId = currentlySelected.productId;
        final productFullSeries = categoryShades.where((s) => s.productId == productId).toList();
        
        state = state.copyWith(
          isBestColorsFilterActive: false,
          allShades: productFullSeries,
          selectedShadeId: state.selectedShadeId, // Preserved
        );
      } else {
        state = state.copyWith(
          isBestColorsFilterActive: false,
          allShades: categoryShades,
        );
      }
    }
  }

  void selectShade(String id) {
    state = state.copyWith(selectedShadeId: id);
  }

  Future<void> changeCategory(String newCategory) async {
    final shades = _categorisedShades[newCategory] ?? [];
    final firstId = shades.isEmpty
        ? null
        : _firstFilteredId(shades, state.isBestColorsFilterActive);

    List<ArShadeModel> activeShades = shades;
    
    // If we are currently exploring a collection, lock it to the first available product's series
    if (!state.isBestColorsFilterActive && firstId != null) {
      final firstShade = shades.firstWhere((s) => s.id == firstId);
      activeShades = shades.where((s) => s.productId == firstShade.productId).toList();
    }

    state = state.copyWith(
      isLoading: false,
      activeCategory: newCategory,
      allShades: activeShades,
      selectedShadeId: firstId,
    );
  }

  // ── Private init helpers ─────────────────────────────────────────────────

  String _inferCategory(String name) {
    name = name.toLowerCase();
    if (name.contains('blush') || name.contains('cheek')) return 'CHEEK';
    if (name.contains('eye') || name.contains('shadow')) return 'EYE';
    return 'LIP';
  }

  Future<void> _initFromSession(int sessionId) async {
    final sessionData = await _cosmeticRepo.getSessionCosmetics(sessionId);
    if (sessionData == null) {
      state = state.copyWith(isLoading: false);
      return;
    }

    _categorisedShades = {'LIP': [], 'CHEEK': [], 'EYE': []};

    int idx = 0;
    for (final item in sessionData.cosmetics) {
      final category = _inferCategory(item.productName);
      _categorisedShades[category]!.add(ArShadeModel(
        id: 'session_${item.id}_$idx',
        productId: item.id,
        cosmeticId: item.id,
        brandName: 'Recommended',
        productName: item.productName,
        shadeName: item.shadeName,
        colorHex: item.hexCode,
        isBestColor: true,
      ));
      idx++;
    }

    final lipShades = _categorisedShades['LIP']!;
    final selectedId = lipShades.isNotEmpty ? lipShades.first.id : null;

    state = state.copyWith(
      isLoading: false,
      activeCategory: 'LIP',
      allShades: lipShades,
      selectedShadeId: selectedId,
    );
  }

  Future<void> _initFromDashboard(List<ProductRecommendation> products, int? selectedId) async {
    await Future.delayed(const Duration(milliseconds: 300));

    _categorisedShades = {'LIP': [], 'CHEEK': [], 'EYE': []};
    String activeCategory = 'LIP';
    String? initialSelectedShadeId;

    // 1. Only fetch shades for AR-compatible products (Lip categories: 6, 7, 8)
    //    Non-lip products (Blush, Eye, etc.) are excluded from the AR catalogue.
    const arCompatibleCategoryIds = {6, 7, 8};
    final validProducts = products.where((p) =>
      p.id != 0 &&
      (p.categoryId == null || arCompatibleCategoryIds.contains(p.categoryId))
    ).toList();
    final List<CosmeticSessionResponse?> results = await Future.wait(
      validProducts.map((p) => _cosmeticRepo.getProductShades(p.id))
    );

    // 2. Process results
    for (int i = 0; i < validProducts.length; i++) {
      final product = validProducts[i];
      final productData = results[i];
      final category = _inferCategory(product.name);

      if (productData != null && productData.cosmetics.isNotEmpty) {
        for (final item in productData.cosmetics) {
          final isOriginalRecommendation = (item.id == product.id);
          final dynamicShade = ArShadeModel(
            id: 'dash_${item.id}_${DateTime.now().millisecondsSinceEpoch}',
            productId: product.id,
            cosmeticId: item.id,
            brandName: product.brand,
            productName: item.productName,
            shadeName: item.shadeName,
            colorHex: item.hexCode,
            isBestColor: isOriginalRecommendation,
          );

          _categorisedShades[category]!.add(dynamicShade);

          if (isOriginalRecommendation && product.id == selectedId) {
            activeCategory = category;
            initialSelectedShadeId = dynamicShade.id;
          }
        }
      } else {
        // Fallback if the API doesn't return data for this product
        final dynamicShade = ArShadeModel(
          id: 'dash_${product.id}_${DateTime.now().millisecondsSinceEpoch}',
          productId: product.id,
          cosmeticId: product.id,
          brandName: product.brand,
          productName: product.name,
          shadeName: product.shade,
          colorHex: _fallbackHexForCategory(category),
          isBestColor: true,
        );
        _categorisedShades[category]!.add(dynamicShade);

        if (product.id == selectedId) {
          activeCategory = category;
          initialSelectedShadeId = dynamicShade.id;
        }
      }
    }

    final activeShades = _categorisedShades[activeCategory] ?? [];
    if (initialSelectedShadeId == null) {
      initialSelectedShadeId = _firstFilteredId(activeShades, state.isBestColorsFilterActive);
    }

    state = state.copyWith(
      isLoading: false,
      activeCategory: activeCategory,
      allShades: activeShades,
      selectedShadeId: initialSelectedShadeId,
    );
  }

  // ── Private utilities ────────────────────────────────────────────────────

  String? _firstFilteredId(List<ArShadeModel> shades, bool filterActive) {
    final visible =
        filterActive ? shades.where((s) => s.isBestColor).toList() : shades;
    return visible.isNotEmpty ? visible.first.id : null;
  }

  String _fallbackHexForCategory(String category) {
    switch (category.toUpperCase()) {
      case 'CHEEK': return '#D4836E';
      case 'EYE':   return '#7A5C42';
      default:      return '#B5453A'; // LIP
    }
  }
}

// Removed mock data.
