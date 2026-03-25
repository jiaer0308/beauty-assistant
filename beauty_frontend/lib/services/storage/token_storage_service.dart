import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final tokenStorageServiceProvider = Provider<TokenStorageService>((ref) {
  return TokenStorageService();
});

class TokenStorageService {
  final FlutterSecureStorage _storage;

  TokenStorageService({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  static const String _tokenKey = 'auth_token';
  static const String _guestTokenKey = 'guest_token';

  /// Save JWT token
  Future<void> saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  /// Get JWT token
  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  /// Delete JWT token
  Future<void> deleteToken() async {
    await _storage.delete(key: _tokenKey);
  }

  /// Save Guest Token (UUID)
  Future<void> saveGuestToken(String token) async {
    await _storage.write(key: _guestTokenKey, value: token);
  }

  /// Get Guest Token (UUID)
  Future<String?> getGuestToken() async {
    return await _storage.read(key: _guestTokenKey);
  }

  /// Delete Guest Token (UUID)
  Future<void> deleteGuestToken() async {
    await _storage.delete(key: _guestTokenKey);
  }

  /// Clear all stored tokens
  Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}
