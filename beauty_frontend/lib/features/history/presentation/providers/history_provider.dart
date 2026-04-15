import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../services/api/history_service.dart';
import '../../data/models/history_models.dart';

// ---------------------------------------------------------------------------
// History List — AsyncNotifier with optimistic delete
// ---------------------------------------------------------------------------

class HistoryListNotifier extends AsyncNotifier<List<HistorySession>> {
  @override
  Future<List<HistorySession>> build() {
    return ref.read(historyServiceProvider).getHistory();
  }

  /// Refreshes the history list from the server.
  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(historyServiceProvider).getHistory(),
    );
  }

  /// Optimistically removes [sessionId] from the list, then calls the DELETE
  /// endpoint. If the request fails the item is restored and an error is
  /// propagated so the UI can show a SnackBar.
  Future<void> deleteSession(int sessionId) async {
    final previous = state;

    // 1. Optimistic removal — update local state immediately
    state = previous.whenData(
      (list) => list.where((s) => s.id != sessionId).toList(),
    );

    // 2. Backend call — roll back on failure
    try {
      await ref.read(historyServiceProvider).deleteSession(sessionId);
    } catch (e, st) {
      // Rollback: restore previous state
      state = previous;
      // Re-throw so the UI layer can catch it and show an error message
      Error.throwWithStackTrace(e, st);
    }
  }
}

final historyListProvider =
    AsyncNotifierProvider<HistoryListNotifier, List<HistorySession>>(
  HistoryListNotifier.new,
);

// ---------------------------------------------------------------------------
// Session Detail — FutureProvider.family (cached per sessionId)
// ---------------------------------------------------------------------------

final historyDetailProvider =
    FutureProvider.family<HistorySessionDetail, int>((ref, sessionId) {
  return ref.read(historyServiceProvider).getSessionDetails(sessionId);
});
