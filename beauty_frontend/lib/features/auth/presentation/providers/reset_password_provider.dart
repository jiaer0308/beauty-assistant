import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../services/api/auth_service.dart';

// ── State ──────────────────────────────────────────────────────────────────────

enum ResetPasswordStatus { idle, loading, success, error }

class ResetPasswordState {
  final ResetPasswordStatus status;
  final String? errorMessage;

  const ResetPasswordState({
    this.status = ResetPasswordStatus.idle,
    this.errorMessage,
  });

  ResetPasswordState copyWith({
    ResetPasswordStatus? status,
    String? errorMessage,
  }) {
    return ResetPasswordState(
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

// ── Notifier ───────────────────────────────────────────────────────────────────

class ResetPasswordNotifier extends StateNotifier<ResetPasswordState> {
  final AuthService _authService;

  ResetPasswordNotifier(this._authService) : super(const ResetPasswordState());

  /// Request a password reset email for [email].
  /// Always completes with [success] from the API's generic 200 response.
  Future<void> forgotPassword(String email) async {
    state = state.copyWith(status: ResetPasswordStatus.loading, errorMessage: null);
    try {
      await _authService.forgotPassword(email: email);
      state = state.copyWith(status: ResetPasswordStatus.success);
    } catch (e) {
      state = state.copyWith(
        status: ResetPasswordStatus.error,
        errorMessage: _friendly(e),
      );
    }
  }

  /// Submit a new password using the one-time [token] from the email link.
  Future<bool> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    state = state.copyWith(status: ResetPasswordStatus.loading, errorMessage: null);
    try {
      await _authService.resetPassword(token: token, newPassword: newPassword);
      state = state.copyWith(status: ResetPasswordStatus.success);
      return true;
    } catch (e) {
      state = state.copyWith(
        status: ResetPasswordStatus.error,
        errorMessage: _friendly(e),
      );
      return false;
    }
  }

  void reset() => state = const ResetPasswordState();

  String _friendly(Object e) {
    final s = e.toString();
    if (s.contains('400')) return 'Invalid or expired reset link. Please request a new one.';
    if (s.contains('500')) return 'Server error. Please try again later.';
    if (s.contains('SocketException') || s.contains('Connection')) {
      return 'No internet connection.';
    }
    return 'Something went wrong. Please try again.';
  }
}

// ── Provider ───────────────────────────────────────────────────────────────────

final resetPasswordProvider =
    StateNotifierProvider.autoDispose<ResetPasswordNotifier, ResetPasswordState>(
  (ref) => ResetPasswordNotifier(ref.read(authServiceProvider)),
);

// ── Pending deep-link token ─────────────────────────────────────────────────────
// Stores a reset token received via deep link before the router is fully ready.
// SplashScreen reads and clears this after its auth init, then navigates to
// /reset-password if a token is waiting.
final pendingResetTokenProvider = StateProvider<String?>((ref) => null);
