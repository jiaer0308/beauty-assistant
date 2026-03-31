import 'dart:developer' as dev;
import 'package:dio/dio.dart';
import '../storage/token_storage_service.dart';

/// Intercepts every Dio request to attach the appropriate auth header.
///
/// Priority:
///   1. JWT Bearer token  (registered user)
///   2. X-Guest-Token     (anonymous / guest user)
///
/// On a 401 response the interceptor will:
///   - Clear any stale guest token from storage.
///   - Request a fresh guest session from the backend.
///   - Retry the original request once with the new guest token.
///
/// This handles the common scenario where the backend database was reset
/// but the device still holds an old, now-invalid guest token.
class AuthInterceptor extends Interceptor {
  final TokenStorageService _tokenStorage;

  /// A minimal Dio instance used *only* to call `/api/v1/auth/guest`.
  /// We keep it separate to avoid infinite retry loops through this
  /// interceptor.
  final Dio _authDio;

  AuthInterceptor(this._tokenStorage, {required String baseUrl})
      : _authDio = Dio(BaseOptions(baseUrl: baseUrl));

  // ─────────────────────────────────────────────────────────
  // onRequest — attach auth headers
  // ─────────────────────────────────────────────────────────

  @override
  void onRequest(
      RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _tokenStorage.getToken();

    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
      dev.log('[AuthInterceptor] Attaching Bearer token (JWT)',
          name: 'AuthInterceptor');
    } else {
      final guestToken = await _tokenStorage.getGuestToken();
      if (guestToken != null) {
        options.headers['X-Guest-Token'] = guestToken;
        dev.log(
            '[AuthInterceptor] Attaching X-Guest-Token: ${guestToken.substring(0, 8)}…',
            name: 'AuthInterceptor');
      } else {
        dev.log(
            '[AuthInterceptor] WARNING: No auth token found — request will be unauthenticated.',
            name: 'AuthInterceptor');
      }
    }

    return handler.next(options);
  }

  // ─────────────────────────────────────────────────────────
  // onError — auto-recover from stale guest token (401)
  // ─────────────────────────────────────────────────────────

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      dev.log(
          '[AuthInterceptor] 401 Unauthorized for ${err.requestOptions.path}',
          name: 'AuthInterceptor');

      // Only attempt auto-recovery when the user was in guest mode
      // (no JWT present, meaning we were relying on X-Guest-Token).
      final jwt = await _tokenStorage.getToken();
      final oldGuestToken = await _tokenStorage.getGuestToken();

      if (jwt == null && oldGuestToken != null) {
        dev.log(
            '[AuthInterceptor] Stale guest token detected. Requesting fresh guest session…',
            name: 'AuthInterceptor');

        try {
          // 1. Clear the stale token
          await _tokenStorage.deleteGuestToken();

          // 2. Request a new guest session
          final response = await _authDio.post('/api/v1/auth/guest');
          final newGuestToken = response.data['guest_token'] as String?;

          if (newGuestToken != null) {
            await _tokenStorage.saveGuestToken(newGuestToken);
            dev.log(
                '[AuthInterceptor] New guest token obtained: ${newGuestToken.substring(0, 8)}…',
                name: 'AuthInterceptor');

            // 3. Retry the original request with the fresh token
            final retryOptions = err.requestOptions;
            retryOptions.headers['X-Guest-Token'] = newGuestToken;
            // Remove any stale header
            retryOptions.headers.remove('Authorization');

            // Use the same base Dio (without this interceptor) to retry
            try {
              final retryResponse = await _authDio.fetch(retryOptions);
              return handler.resolve(retryResponse);
            } on DioException catch (retryErr) {
              dev.log(
                  '[AuthInterceptor] Retry after guest refresh also failed: ${retryErr.response?.statusCode}',
                  name: 'AuthInterceptor');
              return handler.next(retryErr);
            }
          }
        } catch (e) {
          dev.log('[AuthInterceptor] Failed to refresh guest session: $e',
              name: 'AuthInterceptor');
        }
      } else if (jwt != null) {
        dev.log(
            '[AuthInterceptor] Stale JWT detected (user not found in DB). Clearing and falling back to guest session…',
            name: 'AuthInterceptor');

        try {
          // 1. Clear the stale JWT
          await _tokenStorage.deleteToken();

          // 2. Also clear any existing guest token for a clean slate
          await _tokenStorage.deleteGuestToken();

          // 3. Request a brand-new guest session
          final response = await _authDio.post('/api/v1/auth/guest');
          final newGuestToken = response.data['guest_token'] as String?;

          if (newGuestToken != null) {
            await _tokenStorage.saveGuestToken(newGuestToken);
            dev.log(
                '[AuthInterceptor] New guest token obtained after JWT invalidation: ${newGuestToken.substring(0, 8)}…',
                name: 'AuthInterceptor');

            // 4. Retry the original request with the fresh guest token
            final retryOptions = err.requestOptions;
            retryOptions.headers.remove('Authorization');
            retryOptions.headers['X-Guest-Token'] = newGuestToken;

            try {
              final retryResponse = await _authDio.fetch(retryOptions);
              return handler.resolve(retryResponse);
            } on DioException catch (retryErr) {
              dev.log(
                  '[AuthInterceptor] Retry after JWT fallback also failed: ${retryErr.response?.statusCode}',
                  name: 'AuthInterceptor');
              return handler.next(retryErr);
            }
          }
        } catch (e) {
          dev.log(
              '[AuthInterceptor] Failed to recover from stale JWT: $e',
              name: 'AuthInterceptor');
        }
      }
    }

    return handler.next(err);
  }
}
