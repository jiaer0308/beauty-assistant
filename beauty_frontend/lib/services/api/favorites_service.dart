import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_provider.dart';
import '../../features/favorites/data/models/favorites_response_model.dart';

final favoritesServiceProvider = Provider<FavoritesService>((ref) {
  final dio = ref.read(dioProvider);
  return FavoritesService(dio: dio);
});

class FavoritesService {
  final Dio _dio;

  FavoritesService({required Dio dio}) : _dio = dio;

  /// Fetches a paginated list of favorites.
  Future<FavoritesResponseModel> getFavorites({int page = 1, int limit = 20}) async {
    try {
      final response = await _dio.get(
        '/api/v1/favorites/',
        queryParameters: {
          'page': page,
          'limit': limit,
        },
      );
      if (response.statusCode != null &&
          response.statusCode! >= 200 &&
          response.statusCode! < 300) {
        return FavoritesResponseModel.fromJson(response.data as Map<String, dynamic>);
      }
      throw Exception('Failed to fetch favorites: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response != null) {
        throw Exception(
            'Server error: ${e.response?.statusCode} - ${e.response?.data}');
      }
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Adds a cosmetic item to favorites.
  Future<void> addFavorite(int cosmeticId) async {
    try {
      final response = await _dio.post('/api/v1/favorites/$cosmeticId');
      if (response.statusCode != null &&
          response.statusCode! >= 200 &&
          response.statusCode! < 300) {
        return;
      }
      throw Exception('Failed to add favorite: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response != null) {
        throw Exception(
            'Server error: ${e.response?.statusCode} - ${e.response?.data}');
      }
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Removes a cosmetic item from favorites.
  Future<void> removeFavorite(int cosmeticId) async {
    try {
      final response = await _dio.delete('/api/v1/favorites/$cosmeticId');
      if (response.statusCode != null &&
          response.statusCode! >= 200 &&
          response.statusCode! < 300) {
        return;
      }
      throw Exception('Failed to remove favorite: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response != null) {
        throw Exception(
            'Server error: ${e.response?.statusCode} - ${e.response?.data}');
      }
      throw Exception('Network error: ${e.message}');
    }
  }
}
