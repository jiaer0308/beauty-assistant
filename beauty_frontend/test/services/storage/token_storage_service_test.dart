import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:beauty_assistant/services/storage/token_storage_service.dart';

class MockFlutterSecureStorage extends Fake implements FlutterSecureStorage {
  final Map<String, String> _storage = {};

  @override
  Future<void> write({
    required String key,
    required String? value,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    if (value == null) {
      _storage.remove(key);
    } else {
      _storage[key] = value;
    }
  }

  @override
  Future<String?> read({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    return _storage[key];
  }

  @override
  Future<void> delete({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    _storage.remove(key);
  }

  @override
  Future<void> deleteAll({
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    _storage.clear();
  }
}

void main() {
  late TokenStorageService tokenStorageService;
  late MockFlutterSecureStorage mockStorage;

  setUp(() {
    mockStorage = MockFlutterSecureStorage();
    tokenStorageService = TokenStorageService(storage: mockStorage);
  });

  group('TokenStorageService', () {
    test('saveEmail saves email to storage', () async {
      const email = 'test@example.com';
      await tokenStorageService.saveEmail(email);
      expect(await tokenStorageService.getEmail(), email);
    });

    test('getEmail returns null if no email saved', () async {
      expect(await tokenStorageService.getEmail(), isNull);
    });

    test('deleteEmail removes email from storage', () async {
      const email = 'test@example.com';
      await tokenStorageService.saveEmail(email);
      await tokenStorageService.deleteEmail();
      expect(await tokenStorageService.getEmail(), isNull);
    });

    test('saveToken saves token to storage', () async {
      const token = 'test-token';
      await tokenStorageService.saveToken(token);
      expect(await tokenStorageService.getToken(), token);
    });

    test('saveGuestToken saves guest token to storage', () async {
      const token = 'guest-token';
      await tokenStorageService.saveGuestToken(token);
      expect(await tokenStorageService.getGuestToken(), token);
    });

    test('clearAll removes everything', () async {
      await tokenStorageService.saveToken('token');
      await tokenStorageService.saveEmail('email');
      await tokenStorageService.clearAll();
      expect(await tokenStorageService.getToken(), isNull);
      expect(await tokenStorageService.getEmail(), isNull);
    });
  });
}
