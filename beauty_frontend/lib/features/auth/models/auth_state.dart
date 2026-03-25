enum AuthStatus {
  initial,
  authenticated,
  guest,
  unauthenticated,
  loading,
  error,
}

class AuthState {
  final AuthStatus status;
  final String? token;
  final String? guestToken;
  final String? email;
  final String? errorMessage;

  AuthState({
    required this.status,
    this.token,
    this.guestToken,
    this.email,
    this.errorMessage,
  });

  factory AuthState.initial() => AuthState(status: AuthStatus.initial);

  AuthState copyWith({
    AuthStatus? status,
    String? token,
    String? guestToken,
    String? email,
    String? errorMessage,
  }) {
    return AuthState(
      status: status ?? this.status,
      token: token ?? this.token,
      guestToken: guestToken ?? this.guestToken,
      email: email ?? this.email,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}
