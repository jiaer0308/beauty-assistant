import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_provider.dart';

final historyServiceProvider = Provider<HistoryService>((ref) {
  final dio = ref.read(dioProvider);
  return HistoryService(dio);
});

class HistoryService {
  final Dio _dio;

  HistoryService(this._dio);

  /// Fetch user's recommendation history
  Future<List<dynamic>> getHistory() async {
    final response = await _dio.get('/api/v1/history/');
    return response.data; // Backend returns a list of sessions
  }

  /// Get details of a specific session
  Future<Map<String, dynamic>> getSessionDetails(int sessionId) async {
    final response = await _dio.get('/api/v1/history/session/$sessionId');
    return response.data;
  }
}
