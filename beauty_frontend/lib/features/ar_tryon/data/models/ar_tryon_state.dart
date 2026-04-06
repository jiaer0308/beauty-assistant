import 'ar_shade_model.dart';

/// Immutable state for the AR Try-On feature.
///
/// Holds the full shade catalogue for the active category, the current
/// filter toggle, and the user's selected shade.  The [filteredShades]
/// getter applies the "Best Colors" filter when active.
class ArTryonState {
  final bool isLoading;
  final String activeCategory;
  final List<ArShadeModel> allShades;
  final bool isBestColorsFilterActive;
  final String? selectedShadeId;
  final bool isSessionMode;

  const ArTryonState({
    this.isLoading = false,
    this.activeCategory = 'LIP',
    this.allShades = const [],
    this.isBestColorsFilterActive = true,
    this.selectedShadeId,
    this.isSessionMode = false,
  });

  /// Returns only shades where [isBestColor] is true when the filter is
  /// active, otherwise returns the complete [allShades] list.
  List<ArShadeModel> get filteredShades {
    if (isBestColorsFilterActive) {
      return allShades.where((s) => s.isBestColor).toList();
    }
    return allShades;
  }

  factory ArTryonState.initial() => const ArTryonState();

  ArTryonState copyWith({
    bool? isLoading,
    String? activeCategory,
    List<ArShadeModel>? allShades,
    bool? isBestColorsFilterActive,
    // Use a wrapper to allow explicitly setting selectedShadeId to null.
    Object? selectedShadeId = _sentinel,
    bool? isSessionMode,
  }) {
    return ArTryonState(
      isLoading: isLoading ?? this.isLoading,
      activeCategory: activeCategory ?? this.activeCategory,
      allShades: allShades ?? this.allShades,
      isBestColorsFilterActive:
          isBestColorsFilterActive ?? this.isBestColorsFilterActive,
      selectedShadeId: identical(selectedShadeId, _sentinel)
          ? this.selectedShadeId
          : selectedShadeId as String?,
      isSessionMode: isSessionMode ?? this.isSessionMode,
    );
  }

  @override
  String toString() =>
      'ArTryonState(loading: $isLoading, category: $activeCategory, '
      'shades: ${allShades.length}, filterActive: $isBestColorsFilterActive, '
      'selected: $selectedShadeId, sessionMode: $isSessionMode)';
}

/// Private sentinel used by [copyWith] to distinguish between "not provided"
/// and "explicitly set to null".
const Object _sentinel = Object();
