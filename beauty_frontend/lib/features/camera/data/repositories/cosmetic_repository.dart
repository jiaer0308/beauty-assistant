import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/dio_provider.dart';

/// Represents a single shade returned by /api/v1/cosmetics/shades.
class CosmeticShadeResult {
  final int id;
  final String hexCode;

  const CosmeticShadeResult({required this.id, required this.hexCode});

  factory CosmeticShadeResult.fromJson(Map<String, dynamic> json) {
    return CosmeticShadeResult(
      id: json['id'] as int,
      hexCode: json['hex_code'] as String? ?? '#B5453A',
    );
  }
}

/// Fetches cosmetic shade data from the backend.
class CosmeticRepository {
  final Dio _dio;

  CosmeticRepository(this._dio);

  /// GET /api/v1/cosmetics/shades?ids=1&ids=2
  ///
  /// Returns a map of { cosmeticId → hexCode } for all found IDs.
  /// Unknown IDs are silently omitted by the backend.
  Future<Map<int, String>> getShadeHexCodes(List<int> ids) async {
    if (ids.isEmpty) return {};

    try {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/cosmetics/shades',
        queryParameters: {'ids': ids},
      );

      final body = response.data;
      if (body == null) return {};

      final shadesList = body['shades'] as List<dynamic>? ?? [];
      return {
        for (final item in shadesList)
          (item['id'] as int): (item['hex_code'] as String? ?? '#B5453A'),
      };
    } on DioException catch (_) {
      // Silently return empty — callers will use fallback colours.
      return {};
    }
  }

  /// GET /api/v1/cosmetics/shades?id={id}
  /// 
  /// Returns a full list of cosmetic items (all shades) for the specified target product ID.
  Future<CosmeticSessionResponse?> getProductShades(int id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/cosmetics/shades',
        queryParameters: {'id': id},
      );

      final body = response.data;
      if (body == null) return null;

      // The response format for this is identical to what the session endpoint uses (array inside 'shades').
      // We can safely reuse CosmeticSessionResponse.
      return CosmeticSessionResponse.fromJson(body);
    } on DioException catch (_) {
      return null;
    }
  }
  /// GET /api/v1/cosmetics/sessions/{sessionId}
  ///
  /// Returns a full list of cosmetic items with their hex codes for a given session.
  Future<CosmeticSessionResponse?> getSessionCosmetics(int sessionId) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/cosmetics/sessions/$sessionId',
      );

      final body = response.data;
      if (body == null) return null;

      return CosmeticSessionResponse.fromJson(body);
    } on DioException catch (_) {
      return null;
    }
  }
}

/// Represents a single cosmetic item returned within a session.
class CosmeticSessionItem {
  final int id;
  final String productName;
  final String shadeName;
  final String hexCode;
  final String? imageUrl;

  const CosmeticSessionItem({
    required this.id,
    required this.productName,
    required this.shadeName,
    required this.hexCode,
    this.imageUrl,
  });

  factory CosmeticSessionItem.fromJson(Map<String, dynamic> json) {
    return CosmeticSessionItem(
      id: json['id'] as int,
      productName: json['product_name'] as String? ?? 'Product',
      shadeName: json['shade_name'] as String? ?? 'Shade',
      hexCode: json['hex_code'] as String? ?? '#B5453A',
      imageUrl: json['image_url'] as String?,
    );
  }
}

/// Represents the response from /api/v1/cosmetics/sessions/{sessionId}
class CosmeticSessionResponse {
  final int sessionId;
  final List<CosmeticSessionItem> cosmetics;

  const CosmeticSessionResponse({
    required this.sessionId,
    required this.cosmetics,
  });

  factory CosmeticSessionResponse.fromJson(Map<String, dynamic> json) {
    final cosmeticsList = json['shades'] as List<dynamic>? ?? [];
    return CosmeticSessionResponse(
      sessionId: json['session_id'] as int? ?? 0,
      cosmetics: cosmeticsList
          .map((item) => CosmeticSessionItem.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

// ---------------------------------------------------------------------------
// Riverpod provider
// ---------------------------------------------------------------------------

final cosmeticRepositoryProvider = Provider<CosmeticRepository>((ref) {
  final dio = ref.watch(dioProvider);
  return CosmeticRepository(dio);
});
