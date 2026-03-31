import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../services/api/auth_service.dart';
import '../../../../services/storage/token_storage_service.dart';
import '../../models/auth_state.dart';

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authService = ref.read(authServiceProvider);
  final tokenStorage = ref.read(tokenStorageServiceProvider);
  return AuthNotifier(authService, tokenStorage);
});

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;
  final TokenStorageService _tokenStorage;

  AuthNotifier(this._authService, this._tokenStorage) : super(AuthState.initial());

  /// Initialize auth state (check for existing tokens and verify them)
  Future<void> init() async {
    state = state.copyWith(status: AuthStatus.loading);
    try {
      final token = await _tokenStorage.getToken();
      final guestToken = await _tokenStorage.getGuestToken();
      final email = await _tokenStorage.getEmail();

      if (token != null) {
        try {
          // Verify token validity with backend
          await _authService.verifyToken(token);
          state = state.copyWith(status: AuthStatus.authenticated, token: token, email: email);
        } catch (e) {
          // Token is invalid (e.g., expired or user deleted)
          print('Token verification failed: $e');
          await _tokenStorage.deleteToken(); // Clean up invalid token
          
          if (guestToken != null) {
            state = state.copyWith(status: AuthStatus.guest, guestToken: guestToken);
          } else {
            state = state.copyWith(status: AuthStatus.unauthenticated);
          }
        }
      } else if (guestToken != null) {
        // Here we could also verify guestToken if there was a specific guest verify endpoint, 
        // but typically guest tokens just get a 401 on standard routes if invalid.
        state = state.copyWith(status: AuthStatus.guest, guestToken: guestToken);
      } else {
        state = state.copyWith(status: AuthStatus.unauthenticated);
      }
    } catch (e) {
      state = state.copyWith(status: AuthStatus.error, errorMessage: e.toString());
    }
  }

  /// Create a new guest session
  Future<void> loginAsGuest() async {
    state = state.copyWith(status: AuthStatus.loading);
    try {
      final data = await _authService.createGuest();
      final guestToken = data['guest_token'];
      await _tokenStorage.saveGuestToken(guestToken);
      state = state.copyWith(status: AuthStatus.guest, guestToken: guestToken);
    } catch (e) {
      state = state.copyWith(status: AuthStatus.error, errorMessage: e.toString());
    }
  }

  /// Register/Upgrade to full user
  Future<void> register({required String email, required String password}) async {
    state = state.copyWith(status: AuthStatus.loading);
    try {
      final guestToken = await _tokenStorage.getGuestToken();
      final data = await _authService.register(
        email: email,
        password: password,
        guestToken: guestToken,
      );
      
      final token = data['token']['access_token'];
      await _tokenStorage.saveToken(token);
      await _tokenStorage.saveEmail(email);
      // Remove guest token after successful upgrade
      await _tokenStorage.deleteGuestToken();
      
      state = state.copyWith(status: AuthStatus.authenticated, token: token, email: email);
    } catch (e) {
      state = state.copyWith(status: AuthStatus.error, errorMessage: e.toString());
    }
  }

  /// Login as existing user
  Future<void> login({required String email, required String password}) async {
    state = state.copyWith(status: AuthStatus.loading);
    try {
      final data = await _authService.login(email: email, password: password);
      final token = data['token']['access_token'];
      await _tokenStorage.saveToken(token);
      await _tokenStorage.saveEmail(email);
      
      // Also cleanup guest token if it exists
      await _tokenStorage.deleteGuestToken();
      
      state = state.copyWith(status: AuthStatus.authenticated, token: token, email: email);
    } catch (e) {
      state = state.copyWith(status: AuthStatus.error, errorMessage: e.toString());
    }
  }

  /// Logout
  Future<void> logout() async {
    await _tokenStorage.clearAll();
    state = state.copyWith(status: AuthStatus.unauthenticated, token: null, guestToken: null, email: null);
  }
}
