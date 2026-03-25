import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/dio_provider.dart';

import '../../features/camera/data/models/color_analysis_response.dart';

final scaServiceProvider = Provider<ScaService>((ref) {
  final dio = ref.read(dioProvider);
  return ScaService(dio: dio);
});

class QuizData {
  final String skinType;
  final String sunReaction;
  final String veinColor;
  final String naturalHairColor;
  final String jewelryPreference;

  const QuizData({
    required this.skinType,
    required this.sunReaction,
    required this.veinColor,
    required this.naturalHairColor,
    required this.jewelryPreference,
  });

  Map<String, dynamic> toJson() {
    return {
      'skin_type': skinType,
      'sun_reaction': sunReaction,
      'vein_color': veinColor,
      'natural_hair_color': naturalHairColor,
      'jewelry_preference': jewelryPreference,
    };
  }
}

class ScaService {
  final Dio _dio;

  // Initialize with optional Dio instance for testing, otherwise configure default
  ScaService({Dio? dio}) : _dio = dio ?? Dio();

  /// Send image and quiz data to SCA analyze endpoint
  Future<ColorAnalysisResponse> analyzeImage(String imagePath, QuizData? quizData) async {
    final imageFile = File(imagePath);
    try {
      // Create Dio FormData
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          imageFile.path,
          // Explicitly defining filename is a good practice for Android robustness
          filename: imageFile.path.split(Platform.pathSeparator).last,
        ),
        'quiz_data': quizData != null ? jsonEncode(quizData.toJson()) : null,
      });

      // Execute POST request
      final response = await _dio.post(
        '/api/v1/sca/analyze',
        data: formData,
      );

      // Handle successful status codes
      if (response.statusCode != null && response.statusCode! >= 200 && response.statusCode! < 300) {
        return ColorAnalysisResponse.fromJson(response.data as Map<String, dynamic>);
      } else {
        throw Exception('Failed to analyze color: ${response.statusCode}');
      }
    } on DioException catch (e) {
      // Provide robust network error handling
      if (e.response != null) {
        throw Exception('Server error: ${e.response?.statusCode} - ${e.response?.data}');
      } else {
        throw Exception('Network error: ${e.message}');
      }
    } catch (e) {
      // General error catch-all
      throw Exception('Unexpected error: $e');
    }
  }
}
