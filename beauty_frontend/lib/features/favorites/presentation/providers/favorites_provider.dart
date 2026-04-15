import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../services/api/favorites_service.dart';
import '../../data/models/favorite_item_model.dart';

class FavoritesState {
  final List<FavoriteItemModel> items;
  final int total;
  final int currentPage;
  final bool hasNext;
  final bool isLoadingMore;

  const FavoritesState({
    required this.items,
    required this.total,
    required this.currentPage,
    required this.hasNext,
    required this.isLoadingMore,
  });

  FavoritesState copyWith({
    List<FavoriteItemModel>? items,
    int? total,
    int? currentPage,
    bool? hasNext,
    bool? isLoadingMore,
  }) {
    return FavoritesState(
      items: items ?? this.items,
      total: total ?? this.total,
      currentPage: currentPage ?? this.currentPage,
      hasNext: hasNext ?? this.hasNext,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
    );
  }
}

final favoritesProvider =
    AsyncNotifierProvider<FavoritesNotifier, FavoritesState>(
  FavoritesNotifier.new,
);

class FavoritesNotifier extends AsyncNotifier<FavoritesState> {
  static const int _limit = 20;

  @override
  Future<FavoritesState> build() async {
    return _fetchInitial();
  }

  Future<FavoritesState> _fetchInitial() async {
    final service = ref.read(favoritesServiceProvider);
    final response = await service.getFavorites(page: 1, limit: _limit);

    return FavoritesState(
      items: response.items,
      total: response.total,
      currentPage: response.page,
      hasNext: response.hasNext,
      isLoadingMore: false,
    );
  }

  Future<void> fetchNextPage() async {
    if (state.value == null) return;
    if (state.value!.isLoadingMore || !state.value!.hasNext) return;

    // Set loading state
    state = AsyncData(state.value!.copyWith(isLoadingMore: true));

    try {
      final service = ref.read(favoritesServiceProvider);
      final nextPage = state.value!.currentPage + 1;
      final response =
          await service.getFavorites(page: nextPage, limit: _limit);

      final newItems = List<FavoriteItemModel>.from(state.value!.items)
        ..addAll(response.items);

      state = AsyncData(state.value!.copyWith(
        items: newItems,
        total: response.total,
        currentPage: response.page,
        hasNext: response.hasNext,
        isLoadingMore: false,
      ));
    } catch (e, st) {
      // Revert loading state on error
      state = AsyncData(state.value!.copyWith(isLoadingMore: false));
    }
  }

  /// Removes a favorite by ID optimistically
  Future<void> removeFavorite(int cosmeticId) async {
    final currentState = state.value;
    if (currentState == null) return;

    final previousState = currentState.copyWith();
    final service = ref.read(favoritesServiceProvider);

    try {
      final newItems =
          currentState.items.where((e) => e.id != cosmeticId).toList();
      state = AsyncData(currentState.copyWith(
        items: newItems,
        total: currentState.total > 0 ? currentState.total - 1 : 0,
      ));

      await service.removeFavorite(cosmeticId);
    } catch (e) {
      // Rollback on failure
      state = AsyncData(previousState);
    }
  }

  /// Adds a favorite by ID and refreshes the list in the background
  /// since we don't have the full product details to do a pure optimistic insert.
  Future<void> addFavorite(int cosmeticId) async {
    final service = ref.read(favoritesServiceProvider);
    try {
      await service.addFavorite(cosmeticId);
      // Wait slightly then refresh so the new item shows up at the top
      await refresh();
    } catch (e) {
      // Error handling can be managed by listeners if needed
    }
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetchInitial);
  }
}
