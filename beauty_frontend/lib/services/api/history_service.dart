import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_provider.dart';
import '../../features/history/data/models/history_models.dart';

final historyServiceProvider = Provider<HistoryService>((ref) {
  final dio = ref.read(dioProvider);
  return HistoryService(dio);
});

class HistoryService {
  final Dio _dio;

  HistoryService(this._dio);

  /// Fetch the current user's recommendation history (list view).
  Future<List<HistorySession>> getHistory() async {
    final response = await _dio.get('/api/v1/history/');
    final raw = response.data as List<dynamic>;
    return raw
        .map((e) => HistorySession.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Fetch full details (including enriched product list) for one session.
  Future<HistorySessionDetail> getSessionDetails(int sessionId) async {
    final response = await _dio.get('/api/v1/history/$sessionId');
    return HistorySessionDetail.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// Soft-delete a session (maps to backend soft-archive via is_archived flag).
  Future<void> deleteSession(int sessionId) async {
    await _dio.delete('/api/v1/history/$sessionId');
  }
}
