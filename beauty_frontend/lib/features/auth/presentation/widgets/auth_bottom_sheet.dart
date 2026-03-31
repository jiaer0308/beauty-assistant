import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/glow_theme.dart';
import '../providers/auth_provider.dart';
import '../../models/auth_state.dart';

enum AuthViewState { options, login, signup }

class AuthBottomSheet extends ConsumerStatefulWidget {
  final String discoveredSeason;
  final VoidCallback? onSuccess;
  
  const AuthBottomSheet({
    super.key, 
    this.discoveredSeason = 'Deep Autumn', // Fallback context
    this.onSuccess,
  });

  static void show(BuildContext context, {String discoveredSeason = 'Deep Autumn', VoidCallback? onSuccess}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => AuthBottomSheet(
        discoveredSeason: discoveredSeason,
        onSuccess: onSuccess,
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
    });
  }

  Future<void> _handleLogin() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all fields')),
      );
      return;
    }

    await ref.read(authProvider.notifier).login(email: email, password: password);
    _handleAuthResult();
  }

  Future<void> _handleSignup() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    final confirmPassword = _confirmPasswordController.text.trim();

    if (email.isEmpty || password.isEmpty || confirmPassword.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all fields')),
      );
      return;
    }

    if (password != confirmPassword) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Passwords do not match')),
      );
      return;
    }

    await ref.read(authProvider.notifier).register(email: email, password: password);
    _handleAuthResult();
  }

  void _handleAuthResult() {
    final authState = ref.read(authProvider);
    if (authState.status == AuthStatus.authenticated) {
      Navigator.pop(context);
      if (widget.onSuccess != null) {
        // Need a small delay to allow bottom sheet to pop before pushing new route
        Future.delayed(const Duration(milliseconds: 100), () {
          widget.onSuccess!();
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Welcome back!')),
        );
      }
    } else if (authState.status == AuthStatus.error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(authState.errorMessage ?? 'Authentication failed')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isLoading = authState.status == AuthStatus.loading;

    return Container(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      decoration: const BoxDecoration(
        color: GlowTheme.pearlWhite,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
          child: isLoading 
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
        const SizedBox(height: 32),
        
        _buildOutlineButton(
          icon: Icons.supervised_user_circle_outlined,
          label: 'Continue with Google',
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Google sign-in coming soon!')),
            );
          },
        ),
        const SizedBox(height: 16),
        
        _buildOutlineButton(
          icon: Icons.mail_outline,
          label: 'Continue with Email',
          onPressed: () => _switchView(AuthViewState.login),
        ),
        
        const SizedBox(height: 32),
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
        const SizedBox(height: 32),
        
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
            onPressed: () {},
            style: TextButton.styleFrom(foregroundColor: GlowTheme.deepTaupe),
            child: const Text('Forgot password?'),
          ),
        ),
        Center(
          child: TextButton(
            onPressed: () => _switchView(AuthViewState.signup),
            style: TextButton.styleFrom(foregroundColor: GlowTheme.deepTaupe),
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
        const SizedBox(height: 32),
        
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
            style: TextButton.styleFrom(foregroundColor: GlowTheme.deepTaupe),
            child: const Text('Already have an account? Log In'),
          ),
        ),
      ],
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
