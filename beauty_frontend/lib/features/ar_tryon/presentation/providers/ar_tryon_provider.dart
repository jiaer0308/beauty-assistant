import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/ar_shade_model.dart';
import '../../data/models/ar_tryon_state.dart';

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

final arTryonProvider =
    StateNotifierProvider<ArTryonNotifier, ArTryonState>((ref) {
  return ArTryonNotifier();
});

// ---------------------------------------------------------------------------
// Notifier
// ---------------------------------------------------------------------------

/// Manages the AR Try-On state – shade catalogue, category switching,
/// best-colors filter, and shade selection.
class ArTryonNotifier extends StateNotifier<ArTryonState> {
  ArTryonNotifier() : super(ArTryonState.initial());

  // ── Public API ──────────────────────────────────────────────────────────

  /// Initialises the notifier.
  ///
  /// Fetches (currently mocked) shades for the default category.
  /// If [product] is provided, it tries to infer the category and inserts
  /// the product as the selected shade.
  Future<void> init({dynamic product}) async {
    state = state.copyWith(isLoading: true);

    // Simulate network latency
    await Future.delayed(const Duration(milliseconds: 400));

    String category = 'LIP';
    if (product != null) {
      final name = (product.name as String).toLowerCase();
      if (name.contains('blush') || name.contains('cheek')) {
        category = 'CHEEK';
      } else if (name.contains('eye') || name.contains('shadow')) {
        category = 'EYE';
      }
    }

    List<ArShadeModel> shades = _fetchShadesForCategory(category);
    String? selectedId;

    if (product != null) {
      // Create a temporary shade to represent the product tapped on the dashboard.
      final dynamicShade = ArShadeModel(
        id: 'dynamic_${DateTime.now().millisecondsSinceEpoch}',
        brandName: product.brand,
        productName: product.name,
        shadeName: product.shade,
        // Since the backend doesn't provide a hex code yet, use a fallback
        colorHex: category == 'CHEEK' ? '#D4836E' : (category == 'EYE' ? '#7A5C42' : '#B5453A'),
        isBestColor: true,
      );
      shades = [dynamicShade, ...shades];
      selectedId = dynamicShade.id;
    } else {
      selectedId = _firstFilteredId(shades, state.isBestColorsFilterActive);
    }

    state = state.copyWith(
      isLoading: false,
      activeCategory: category,
      allShades: shades,
      selectedShadeId: selectedId,
    );
  }

  /// Flips the "Best Colors" filter and resets the selection to the first
  /// item visible under the new filter.
  void toggleFilter() {
    final newFilterState = !state.isBestColorsFilterActive;
    final firstId = _firstFilteredId(state.allShades, newFilterState);

    state = state.copyWith(
      isBestColorsFilterActive: newFilterState,
      selectedShadeId: firstId,
    );
  }

  /// Selects a shade by its [id].
  void selectShade(String id) {
    state = state.copyWith(selectedShadeId: id);
  }

  /// Switches to [newCategory], re-fetches mock shades, and auto-selects
  /// the first visible shade.
  Future<void> changeCategory(String newCategory) async {
    // No artificial delay — local mock data is instant.
    // Real API latency will be felt naturally once backend is integrated.
    final shades = _fetchShadesForCategory(newCategory);
    final firstId = shades.isEmpty
        ? null
        : _firstFilteredId(shades, state.isBestColorsFilterActive);

    state = state.copyWith(
      isLoading: false,
      activeCategory: newCategory,
      allShades: shades,
      selectedShadeId: firstId,
    );
  }

  // ── Private helpers ─────────────────────────────────────────────────────

  /// Returns the id of the first shade that passes the current filter,
  /// or `null` if the list is empty.
  String? _firstFilteredId(List<ArShadeModel> shades, bool filterActive) {
    final visible =
        filterActive ? shades.where((s) => s.isBestColor).toList() : shades;
    return visible.isNotEmpty ? visible.first.id : null;
  }

  /// Mock data provider – returns realistic shades for a **Deep Autumn**
  /// palette based on [category].
  ///
  /// Replace with a real API call when the backend endpoint is ready.
  List<ArShadeModel> _fetchShadesForCategory(String category) {
    switch (category.toUpperCase()) {
      case 'LIP':
        return _mockLipShades;
      case 'EYE':
        return _mockEyeShades;
      case 'CHEEK':
        return _mockCheekShades;
      case 'NONE':
        return const []; // Remove Makeup: no overlay, empty catalogue
      default:
        return _mockLipShades;
    }
  }
}

// ---------------------------------------------------------------------------
// Mock Data – Deep Autumn palette
// ---------------------------------------------------------------------------

const _mockLipShades = [
  ArShadeModel(
    id: 'lip_001',
    brandName: 'MAC',
    productName: 'Matte Lipstick',
    shadeName: 'Marrakesh',
    colorHex: '#B5453A',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'lip_002',
    brandName: 'MAC',
    productName: 'Matte Lipstick',
    shadeName: 'Chili',
    colorHex: '#97312B',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'lip_003',
    brandName: 'Charlotte Tilbury',
    productName: 'Matte Revolution',
    shadeName: 'Walk of No Shame',
    colorHex: '#A33232',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'lip_004',
    brandName: 'NARS',
    productName: 'Audacious Lipstick',
    shadeName: 'Jane',
    colorHex: '#C4635B',
    isBestColor: false,
  ),
  ArShadeModel(
    id: 'lip_005',
    brandName: 'Charlotte Tilbury',
    productName: 'K.I.S.S.I.N.G',
    shadeName: 'Stoned Rose',
    colorHex: '#A8605C',
    isBestColor: false,
  ),
  ArShadeModel(
    id: 'lip_006',
    brandName: 'Rare Beauty',
    productName: 'Soft Pinch Tinted Lip Oil',
    shadeName: 'Serenity',
    colorHex: '#BE7A70',
    isBestColor: true,
  ),
];

const _mockEyeShades = [
  ArShadeModel(
    id: 'eye_001',
    brandName: 'Urban Decay',
    productName: 'Eyeshadow Single',
    shadeName: 'Smog',
    colorHex: '#7A5C42',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'eye_002',
    brandName: 'MAC',
    productName: 'Eye Shadow',
    shadeName: 'Saddle',
    colorHex: '#8B6E53',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'eye_003',
    brandName: 'Charlotte Tilbury',
    productName: 'Luxury Palette',
    shadeName: 'The Dolce Vita',
    colorHex: '#A67B5B',
    isBestColor: false,
  ),
  ArShadeModel(
    id: 'eye_004',
    brandName: 'Tom Ford',
    productName: 'Eye Color Quad',
    shadeName: 'Golden Mink',
    colorHex: '#9C7A42',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'eye_005',
    brandName: 'NARS',
    productName: 'Single Eyeshadow',
    shadeName: 'Mesopotamia',
    colorHex: '#6B4226',
    isBestColor: false,
  ),
];

const _mockCheekShades = [
  ArShadeModel(
    id: 'cheek_001',
    brandName: 'NARS',
    productName: 'Blush',
    shadeName: 'Goulue',
    colorHex: '#C97064',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'cheek_002',
    brandName: 'Rare Beauty',
    productName: 'Soft Pinch Blush',
    shadeName: 'Joy',
    colorHex: '#D4836E',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'cheek_003',
    brandName: 'Charlotte Tilbury',
    productName: 'Cheek to Chic',
    shadeName: 'The Climax',
    colorHex: '#B86B5A',
    isBestColor: false,
  ),
  ArShadeModel(
    id: 'cheek_004',
    brandName: 'MAC',
    productName: 'Powder Blush',
    shadeName: 'Raizin',
    colorHex: '#984B3A',
    isBestColor: true,
  ),
  ArShadeModel(
    id: 'cheek_005',
    brandName: 'Benefit',
    productName: 'WANDERful World Blush',
    shadeName: 'Terra',
    colorHex: '#B8826B',
    isBestColor: false,
  ),
];
