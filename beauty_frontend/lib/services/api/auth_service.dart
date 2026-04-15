import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_provider.dart';

final authServiceProvider = Provider<AuthService>((ref) {
  final dio = ref.read(dioProvider);
  return AuthService(dio);
});

class AuthService {
  final Dio _dio;

  AuthService(this._dio);

  /// Create a guest user session
  Future<Map<String, dynamic>> createGuest() async {
    final response = await _dio.post('/api/v1/auth/guest');
    return response.data;
  }

  /// Register a user (upgrades current guest if guest_token is present)
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    String? guestToken,
  }) async {
    final response = await _dio.post(
      '/api/v1/auth/register',
      data: {
        'email': email,
        'password': password,
        if (guestToken != null) 'guest_token': guestToken,
      },
    );
    return response.data;
  }

  /// Login user
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post(
      '/api/v1/auth/login',
      data: {
        'username': email,
        'password': password,
        'grant_type': 'password',
      },
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );
    return response.data;
  }

  /// Verify token and get current user profile
  Future<Map<String, dynamic>> verifyToken(String token) async {
    final response = await _dio.get(
      '/api/v1/auth/me',
      options: Options(
        headers: {'Authorization': 'Bearer $token'},
      ),
    );
    return response.data;
  }

  /// Request a password reset email. Always returns 200 (generic message).
  Future<Map<String, dynamic>> forgotPassword({required String email}) async {
    final response = await _dio.post(
      '/api/v1/auth/forgot-password',
      data: {'email': email},
    );
    return response.data;
  }

  /// Reset password with a one-time token received via email.
  Future<Map<String, dynamic>> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    final response = await _dio.post(
      '/api/v1/auth/reset-password',
      data: {
        'token': token,
        'new_password': newPassword,
      },
    );
    return response.data;
  }
}
