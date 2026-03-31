import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../services/api/dashboard_service.dart';
import '../../../camera/presentation/providers/color_analysis_provider.dart';

/// Fetches the user's latest analysis dashboard from the backend.
///
/// The provider is kept as an [AsyncNotifierProvider] so the UI can
/// react to loading / error / data states gracefully.
///
/// It also writes the result into [currentAnalysisProvider] so the home
/// screen and any other widget watching that provider stay in sync.
final dashboardProvider =
    AsyncNotifierProvider<DashboardNotifier, DashboardData?>(
        DashboardNotifier.new);

class DashboardNotifier extends AsyncNotifier<DashboardData?> {
  @override
  Future<DashboardData?> build() async {
    return _fetch();
  }

  Future<DashboardData?> _fetch() async {
    final service = ref.read(dashboardServiceProvider);
    try {
      final data = await service.getDashboard();

      // Keep the global in-memory provider in sync so ResultScreen
      // and any other widget watching it get the persisted result.
      if (data.result != null) {
        ref.read(currentAnalysisProvider.notifier).state =
            data.toColorAnalysisResponse();
      }

      return data;
    } catch (_) {
      // Swallow the error gracefully – guest/unauthenticated state returns 401
      // which is expected when the user hasn't completed a scan yet.
      return null;
    }
  }

  /// Call this to manually trigger a refresh (e.g. after a new scan).
  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetch);
  }
}
