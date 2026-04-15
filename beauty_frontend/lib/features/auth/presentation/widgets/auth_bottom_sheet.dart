import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import '../providers/auth_provider.dart';
import '../../models/auth_state.dart';
import '../providers/reset_password_provider.dart';

enum AuthViewState { options, login, signup, forgotPassword }

class AuthBottomSheet extends ConsumerStatefulWidget {
  final String discoveredSeason;
  final VoidCallback? onSuccess;
  /// When true, the 'MAYBE LATER' button is hidden,
  /// forcing the user to register/login to proceed.
  final bool isMandatory;

  const AuthBottomSheet({
    super.key,
    this.discoveredSeason = 'Deep Autumn',
    this.onSuccess,
    this.isMandatory = false,
  });

  static void show(
    BuildContext context, {
    String discoveredSeason = 'Deep Autumn',
    VoidCallback? onSuccess,
    bool isMandatory = false,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      isDismissible: !isMandatory,
      enableDrag: !isMandatory,
      builder: (context) => AuthBottomSheet(
        discoveredSeason: discoveredSeason,
        onSuccess: onSuccess,
        isMandatory: isMandatory,
      ),
    );
  }

  @override
  ConsumerState<AuthBottomSheet> createState() => _AuthBottomSheetState();
}

class _AuthBottomSheetState extends ConsumerState<AuthBottomSheet> {
  AuthViewState _currentView = AuthViewState.options;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;

  // Inline feedback messages (same pattern as ResetPasswordScreen)
  String? _errorMessage;
  String? _successMessage;

  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _switchView(AuthViewState view) {
    setState(() {
      _currentView = view;
      _errorMessage = null;
      _successMessage = null;
    });
  }

  void _clearMessages() {
    setState(() {
      _errorMessage = null;
      _successMessage = null;
    });
  }

  // ── Validation helpers ──────────────────────────────────────────────────────

  bool _isValidEmail(String email) {
    return RegExp(r'^[\w\-.]+@[\w\-.]+\.[a-zA-Z]{2,}$').hasMatch(email);
  }

  // ── Login ────────────────────────────────────────────────────────────────────

  Future<void> _handleLogin() async {
    _clearMessages();
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      setState(() => _errorMessage = 'Please fill in all fields.');
      return;
    }
    if (!_isValidEmail(email)) {
      setState(() => _errorMessage = 'Please enter a valid email address.');
      return;
    }

    setState(() => _isLoading = true);
    await ref.read(authProvider.notifier).login(email: email, password: password);
    if (!mounted) return;
    setState(() => _isLoading = false);
    _handleAuthResult(isLogin: true);
  }

  // ── Signup ───────────────────────────────────────────────────────────────────

  Future<void> _handleSignup() async {
    _clearMessages();
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    final confirmPassword = _confirmPasswordController.text.trim();

    if (email.isEmpty || password.isEmpty || confirmPassword.isEmpty) {
      setState(() => _errorMessage = 'Please fill in all fields.');
      return;
    }
    if (!_isValidEmail(email)) {
      setState(() => _errorMessage = 'Please enter a valid email address.');
      return;
    }
    if (password.length < 8) {
      setState(() => _errorMessage = 'Password must be at least 8 characters.');
      return;
    }
    if (password != confirmPassword) {
      setState(() => _errorMessage = 'Passwords do not match.');
      return;
    }

    setState(() => _isLoading = true);
    await ref.read(authProvider.notifier).register(email: email, password: password);
    if (!mounted) return;
    setState(() => _isLoading = false);
    _handleAuthResult(isLogin: false);
  }

  // ── Result handling ─────────────────────────────────────────────────────────

  void _handleAuthResult({required bool isLogin}) {
    final authState = ref.read(authProvider);
    if (authState.status == AuthStatus.authenticated) {
      if (widget.onSuccess != null) {
        widget.onSuccess!();
      }
      if (mounted) Navigator.of(context).pop();
    } else if (authState.status == AuthStatus.error) {
      setState(() {
        _errorMessage = authState.errorMessage ?? (isLogin
            ? 'Incorrect email or password.'
            : 'Registration failed. Please try again.');
      });
    }
  }

  Future<void> _handleForgotPassword() async {
    _clearMessages();
    final email = _emailController.text.trim();

    if (email.isEmpty) {
      setState(() => _errorMessage = 'Please enter your email address.');
      return;
    }
    if (!_isValidEmail(email)) {
      setState(() => _errorMessage = 'Please enter a valid email address.');
      return;
    }

    setState(() => _isLoading = true);
    await ref.read(resetPasswordProvider.notifier).forgotPassword(email);
    if (!mounted) return;
    setState(() => _isLoading = false);

    final resetState = ref.read(resetPasswordProvider);
    if (resetState.status == ResetPasswordStatus.success) {
      // Switch to login view and show a success message there
      setState(() {
        _currentView = AuthViewState.login;
        _errorMessage = null;
        _successMessage = 'If that email is registered, a password reset link has been sent. Check your inbox!';
      });
    } else if (resetState.status == ResetPasswordStatus.error) {
      setState(() {
        _errorMessage = resetState.errorMessage ?? 'Failed to send reset email. Please try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Keep the reset password provider alive while the bottom sheet is open
    ref.watch(resetPasswordProvider);
    // Do NOT watch authProvider's loading status globally here.
    // We use a local _isLoading flag so splash screen init doesn't affect this sheet.
    return Container(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      decoration: const BoxDecoration(
        color: GlowTheme.pearlWhite,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
            child: _isLoading
              ? const SizedBox(
                  height: 200,
                  child: Center(child: CircularProgressIndicator(color: GlowTheme.champagneGold)),
                )
              : AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  transitionBuilder: (child, animation) {
                    return FadeTransition(opacity: animation, child: child);
                  },
                  child: _buildCurrentView(),
                ),
          ),
        ),
      ),
    );
  }

  Widget _buildCurrentView() {
    switch (_currentView) {
      case AuthViewState.options:
        return _buildOptionsView(key: const ValueKey('options'));
      case AuthViewState.login:
        return _buildLoginView(key: const ValueKey('login'));
      case AuthViewState.signup:
        return _buildSignupView(key: const ValueKey('signup'));
      case AuthViewState.forgotPassword:
        return _buildForgotPasswordView(key: const ValueKey('forgotPassword'));
    }
  }

  Widget _buildOptionsView({required Key key}) {
    return Column(
      key: key,
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Save Your Profile & Unlock AR',
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: GlowTheme.deepTaupe,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Create an account to save your ${widget.discoveredSeason} profile.',
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 16,
            color: GlowTheme.deepTaupe,
          ),
        ),
        const SizedBox(height: 16),
        
        // _buildOutlineButton(
        //   icon: Icons.supervised_user_circle_outlined,
        //   label: 'Continue with Google',
        //   onPressed: () {
        //     ScaffoldMessenger.of(context).showSnackBar(
        //       const SnackBar(content: Text('Google sign-in coming soon!')),
        //     );
        //   },
        // ),
        const SizedBox(height: 16),
        
        _buildOutlineButton(
          icon: Icons.mail_outline,
          label: 'Continue with Email',
          onPressed: () => _switchView(AuthViewState.login),
        ),
        
        const SizedBox(height: 32),
        if (!widget.isMandatory)
          TextButton(
            onPressed: () => Navigator.pop(context),
            style: TextButton.styleFrom(
              foregroundColor: GlowTheme.oatmeal,
            ),
            child: const Text(
              'MAYBE LATER',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                letterSpacing: 1.0,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildLoginView({required Key key}) {
    return Column(
      key: key,
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildHeader(
          title: 'Continue with Email',
          onBack: () => _switchView(AuthViewState.options),
        ),
        const SizedBox(height: 24),

        // ── Inline messages ─────────────────────────────────────
        if (_errorMessage != null) ...[
          _buildMessageBanner(
            message: _errorMessage!,
            isError: true,
          ),
          const SizedBox(height: 16),
        ],
        if (_successMessage != null) ...[
          _buildMessageBanner(
            message: _successMessage!,
            isError: false,
          ),
          const SizedBox(height: 16),
        ],

        _buildTextField(
          controller: _emailController,
          hintText: 'Email',
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 16),
        _buildTextField(
          controller: _passwordController,
          hintText: 'Password',
          isPassword: true,
          obscureText: _obscurePassword,
          onToggleVisibility: () {
            setState(() => _obscurePassword = !_obscurePassword);
          },
        ),
        
        const SizedBox(height: 24),
        _buildSolidButton(
          label: 'Log In',
          onPressed: _handleLogin,
        ),
        
        const SizedBox(height: 16),
        Center(
          child: TextButton(
            onPressed: () => _switchView(AuthViewState.forgotPassword),
            style: TextButton.styleFrom(
              foregroundColor: GlowTheme.deepTaupe,
              textStyle: const TextStyle(fontSize: 14)),
            child: const Text('Forgot password?'),
          ),
        ),
        Center(
          child: TextButton(
            onPressed: () => _switchView(AuthViewState.signup),
            style: TextButton.styleFrom(
              foregroundColor: GlowTheme.deepTaupe,
              textStyle: const TextStyle(fontSize: 14)),
            child: const Text('Don\'t have an account? Create one'),
          ),
        ),
      ],
    );
  }

  Widget _buildSignupView({required Key key}) {
    return Column(
      key: key,
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildHeader(
          title: 'Create Account',
          onBack: () => _switchView(AuthViewState.options),
        ),
        const SizedBox(height: 24),

        // ── Inline messages ─────────────────────────────────────
        if (_errorMessage != null) ...[
          _buildMessageBanner(
            message: _errorMessage!,
            isError: true,
          ),
          const SizedBox(height: 16),
        ],
        if (_successMessage != null) ...[
          _buildMessageBanner(
            message: _successMessage!,
            isError: false,
          ),
          const SizedBox(height: 16),
        ],
        
        _buildLabeledTextField(
          label: 'Email Address', 
          controller: _emailController,
          hintText: 'email@example.com',
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 16),
        _buildLabeledTextField(
          label: 'Password',
          controller: _passwordController,
          hintText: 'Min. 8 characters',
          isPassword: true,
          obscureText: _obscurePassword,
          onToggleVisibility: () {
            setState(() => _obscurePassword = !_obscurePassword);
          },
        ),
        const SizedBox(height: 16),
        _buildLabeledTextField(
          label: 'Confirm Password',
          controller: _confirmPasswordController,
          hintText: 'Repeat password',
          isPassword: true,
          obscureText: _obscureConfirmPassword,
          onToggleVisibility: () {
            setState(() => _obscureConfirmPassword = !_obscureConfirmPassword);
          },
        ),
        
        const SizedBox(height: 32),
        _buildSolidButton(
          label: 'Create Account',
          onPressed: _handleSignup,
        ),
        
        const SizedBox(height: 16),
        Center(
          child: TextButton(
            onPressed: () => _switchView(AuthViewState.login),
            style: TextButton.styleFrom(
              foregroundColor: GlowTheme.deepTaupe,
              textStyle: const TextStyle(fontSize: 14)),
            child: const Text('Already have an account? Log In'),
          ),
        ),
      ],
    );
  }

  Widget _buildForgotPasswordView({required Key key}) {
    return Column(
      key: key,
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildHeader(
          title: 'Reset Password',
          onBack: () => _switchView(AuthViewState.login),
        ),
        const SizedBox(height: 16),
        const Text(
          'Enter your email address and we will send you a link to reset your password.',
          style: TextStyle(
            fontSize: 14,
            color: GlowTheme.deepTaupe,
            height: 1.5,
          ),
        ),
        const SizedBox(height: 20),

        // ── Inline messages ─────────────────────────────────────
        if (_errorMessage != null) ...[
          _buildMessageBanner(
            message: _errorMessage!,
            isError: true,
          ),
          const SizedBox(height: 16),
        ],

        _buildTextField(
          controller: _emailController,
          hintText: 'Email',
          keyboardType: TextInputType.emailAddress,
        ),
        
        const SizedBox(height: 24),
        _buildSolidButton(
          label: 'Send Reset Link',
          onPressed: _handleForgotPassword,
        ),
        
        const SizedBox(height: 16),
        Center(
          child: TextButton(
            onPressed: () => _switchView(AuthViewState.login),
            style: TextButton.styleFrom(
              foregroundColor: GlowTheme.deepTaupe,
              textStyle: const TextStyle(fontSize: 14)),
            child: const Text('Back to Log In'),
          ),
        ),
      ],
    );
  }

  // ── Inline message banner (matching ResetPasswordScreen style) ─────────────

  Widget _buildMessageBanner({required String message, required bool isError}) {
    return AnimatedSize(
      duration: const Duration(milliseconds: 200),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isError ? Colors.red.shade50 : Colors.green.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isError ? Colors.red.shade200 : Colors.green.shade200,
          ),
        ),
        child: Row(
          children: [
            Icon(
              isError ? Icons.error_outline : Icons.check_circle_outline,
              color: isError ? Colors.red.shade700 : Colors.green.shade700,
              size: 20,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                message,
                style: TextStyle(
                  color: isError ? Colors.red.shade700 : Colors.green.shade700,
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            GestureDetector(
              onTap: _clearMessages,
              child: Icon(
                Icons.close,
                size: 16,
                color: isError ? Colors.red.shade400 : Colors.green.shade400,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader({required String title, required VoidCallback onBack}) {
    return Row(
      children: [
        IconButton(
          icon: const Icon(Icons.arrow_back, color: GlowTheme.deepTaupe),
          onPressed: onBack,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
        Expanded(
          child: Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: GlowTheme.deepTaupe,
            ),
          ),
        ),
        const SizedBox(width: 24),
      ],
    );
  }

  Widget _buildOutlineButton({required IconData icon, required String label, required VoidCallback onPressed}) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, color: GlowTheme.deepTaupe),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.white,
        foregroundColor: GlowTheme.deepTaupe,
        elevation: 0,
        minimumSize: const Size.fromHeight(56),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: GlowTheme.oatmeal, width: 1),
        ),
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildSolidButton({required String label, required VoidCallback onPressed}) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: GlowTheme.champagneGold,
        foregroundColor: GlowTheme.deepTaupe,
        elevation: 0,
        minimumSize: const Size.fromHeight(56),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
      child: Text(label),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String hintText,
    bool isPassword = false,
    bool obscureText = false,
    VoidCallback? onToggleVisibility,
    TextInputType? keyboardType,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      style: const TextStyle(color: GlowTheme.deepTaupe),
      decoration: InputDecoration(
        hintText: hintText,
        hintStyle: const TextStyle(color: GlowTheme.oatmeal),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: GlowTheme.oatmeal, width: 1),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: GlowTheme.oatmeal, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: GlowTheme.deepTaupe, width: 1),
        ),
        suffixIcon: isPassword
            ? IconButton(
                icon: Icon(
                  obscureText ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                  color: GlowTheme.deepTaupe,
                ),
                onPressed: onToggleVisibility,
              )
            : null,
      ),
    );
  }

  Widget _buildLabeledTextField({
    required String label,
    required TextEditingController controller,
    required String hintText,
    bool isPassword = false,
    bool obscureText = false,
    VoidCallback? onToggleVisibility,
    TextInputType? keyboardType,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: GlowTheme.deepTaupe,
          ),
        ),
        const SizedBox(height: 8),
        _buildTextField(
          controller: controller,
          hintText: hintText,
          isPassword: isPassword,
          obscureText: obscureText,
          onToggleVisibility: onToggleVisibility,
          keyboardType: keyboardType,
        ),
      ],
    );
  }
}
