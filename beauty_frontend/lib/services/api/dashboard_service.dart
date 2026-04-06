import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_provider.dart';
import '../../features/camera/data/models/color_analysis_response.dart';

final dashboardServiceProvider = Provider<DashboardService>((ref) {
  final dio = ref.read(dioProvider);
  return DashboardService(dio: dio);
});

/// Lightweight model that mirrors the backend DashboardResponse schema.
class DashboardData {
  final bool success;
  final AnalysisResult? result;
  final List<ProductRecommendation> recommendedProducts;

  const DashboardData({
    required this.success,
    this.result,
    this.recommendedProducts = const [],
  });

  factory DashboardData.fromJson(Map<String, dynamic> json) {
    final rawProducts = json['recommended_products'] as List<dynamic>? ?? [];
    return DashboardData(
      success: json['success'] as bool? ?? false,
      result: json['result'] != null
          ? AnalysisResult.fromJson(json['result'] as Map<String, dynamic>)
          : null,
      recommendedProducts: rawProducts
          .map((e) => _productFromDashboard(e as Map<String, dynamic>))
          .toList(),
    );
  }

  /// Convert the dashboard's compact product schema to the shared
  /// [ProductRecommendation] model used by the UI.
  static ProductRecommendation _productFromDashboard(Map<String, dynamic> json) {
    return ProductRecommendation(
      id: json['id'] as int? ?? 0,
      brand: json['brand'] as String? ?? '',
      name: json['name'] as String? ?? '',
      shade: json['shade'] as String? ?? '',
      matchPercentage: json['matchPercentage'] as int? ?? 0,
      imageUrl: json['image_url'] as String? ?? '',
      categoryId: json['category_id'] as int?,
      hexCode: json['hex_code'] as String?,
    );
  }

  /// Convert to the shared [ColorAnalysisResponse] so the UI can consume it
  /// using the same `currentAnalysisProvider`.
  ColorAnalysisResponse toColorAnalysisResponse() {
    return ColorAnalysisResponse(
      success: success,
      result: result,
      recommendedProducts: recommendedProducts,
    );
  }
}

class DashboardService {
  final Dio _dio;

  DashboardService({required Dio dio}) : _dio = dio;

  /// Fetch the user's most recent analysis dashboard.
  /// Authentication (guest or registered) is handled by the [AuthInterceptor].
  Future<DashboardData> getDashboard() async {
    try {
      final response = await _dio.get('/api/v1/dashboard');
      if (response.statusCode != null &&
          response.statusCode! >= 200 &&
          response.statusCode! < 300) {
        return DashboardData.fromJson(response.data as Map<String, dynamic>);
      }
      throw Exception('Dashboard request failed: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response != null) {
        throw Exception(
            'Server error: ${e.response?.statusCode} - ${e.response?.data}');
      }
      throw Exception('Network error: ${e.message}');
    }
  }
}
