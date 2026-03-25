import 'package:dio/dio.dart';
import '../storage/token_storage_service.dart';

class AuthInterceptor extends Interceptor {
  final TokenStorageService _tokenStorage;

  AuthInterceptor(this._tokenStorage);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // 1. Prioritize registered user JWT
    final token = await _tokenStorage.getToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    } else {
      // 2. Fallback to guest user UUID token
      final guestToken = await _tokenStorage.getGuestToken();
      if (guestToken != null) {
        options.headers['X-Guest-Token'] = guestToken;
      }
    }
    
    return handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Optional: Handle 401 Unauthorized globally
    if (err.response?.statusCode == 401) {
      // Logic for force logout or token refresh
    }
    return handler.next(err);
  }
}
