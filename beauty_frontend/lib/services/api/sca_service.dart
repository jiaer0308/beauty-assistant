import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';

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
      'skinType': skinType,
      'sunReaction': sunReaction,
      'veinColor': veinColor,
      'naturalHairColor': naturalHairColor,
      'jewelryPreference': jewelryPreference,
    };
  }
}

class SCAResponse {
  final String season;
  final Map<String, dynamic> analysisDetails;
  
  // Can add more fields based on the actual JSON response
  const SCAResponse({
    required this.season,
    required this.analysisDetails,
  });

  factory SCAResponse.fromJson(Map<String, dynamic> json) {
    return SCAResponse(
      season: json['season'] as String? ?? 'Unknown',
      analysisDetails: json['details'] as Map<String, dynamic>? ?? {},
    );
  }
}

class ScaService {
  final Dio _dio;

  // Initialize with optional Dio instance for testing, otherwise configure default
  ScaService({Dio? dio}) : _dio = dio ?? Dio() {
    // Basic setup, you can inject interceptors or change the BaseUrl
    _dio.options.baseUrl = 'http://10.0.2.2:8000'; // Target Android emulator localhost
    _dio.options.connectTimeout = const Duration(seconds: 30);
    _dio.options.receiveTimeout = const Duration(seconds: 60);
    _dio.options.sendTimeout = const Duration(seconds: 60);
  }

  /// Send image and quiz data to SCA analyze endpoint
  Future<SCAResponse> analyzeColor(File imageFile, QuizData quizData) async {
    try {
      // Create Dio FormData
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          imageFile.path,
          // Explicitly defining filename is a good practice for Android robustness
          filename: imageFile.path.split(Platform.pathSeparator).last,
        ),
        'quiz_data': jsonEncode(quizData.toJson()),
      });

      // Execute POST request
      final response = await _dio.post(
        '/api/v1/sca/analyze',
        data: formData,
      );

      // Handle successful status codes
      if (response.statusCode != null && response.statusCode! >= 200 && response.statusCode! < 300) {
        return SCAResponse.fromJson(response.data as Map<String, dynamic>);
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
