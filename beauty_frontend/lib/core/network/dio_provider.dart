import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../services/api/auth_interceptor.dart';
import '../../services/storage/token_storage_service.dart';

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio();
  final tokenStorage = ref.read(tokenStorageServiceProvider);

  // Allow setting API_URL via --dart-define, otherwise fallback to current IP
  const baseUrl = String.fromEnvironment(
    'API_URL', 
    defaultValue: 'http://192.168.68.101:8000'
  );
  dio.options.baseUrl = baseUrl; 
  dio.options.connectTimeout = const Duration(seconds: 10);
  dio.options.receiveTimeout = const Duration(seconds: 30);
  dio.options.sendTimeout = const Duration(seconds: 30);

  dio.interceptors.addAll([
    AuthInterceptor(tokenStorage, baseUrl: baseUrl),
    LogInterceptor(
      request: true,
      requestHeader: true,
      requestBody: true,
      responseHeader: true,
      responseBody: true,
      error: true,
    ),
  ]);

  return dio;
});
