import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import '../providers/reset_password_provider.dart';

/// Full-screen password reset form, opened via the deep link:
///   beautyassistant://reset-password?token=<uuid>
///
/// The [token] is extracted from the URL by [AppRouter] and passed here.
class ResetPasswordScreen extends ConsumerStatefulWidget {
  final String token;

  const ResetPasswordScreen({super.key, required this.token});

  @override
  ConsumerState<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final success = await ref.read(resetPasswordProvider.notifier).resetPassword(
          token: widget.token,
          newPassword: _passwordController.text.trim(),
        );

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Password updated! Please log in with your new password.'),
          backgroundColor: GlowTheme.champagneGold,
        ),
      );
      // Navigate back to welcome so the user logs in fresh
      context.go('/welcome');
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(resetPasswordProvider);
    final isLoading = state.status == ResetPasswordStatus.loading;

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      // ── AppBar ─────────────────────────────────────────────────────────────
      appBar: AppBar(
        backgroundColor: GlowTheme.pearlWhite,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: GlowTheme.deepTaupe),
          onPressed: () => context.go('/welcome'),
        ),
        title: const Text(
          'Reset Password',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: GlowTheme.deepTaupe,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: isLoading
              ? const SizedBox(
                  height: 300,
                  child: Center(
                    child: CircularProgressIndicator(color: GlowTheme.champagneGold),
                  ),
                )
              : Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // ── Header copy ──────────────────────────────────────
                      const Text(
                        'Choose a new password',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: GlowTheme.deepTaupe,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Your new password must be at least 8 characters.',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 14, color: GlowTheme.oatmeal),
                      ),
                      const SizedBox(height: 40),

                      // ── New password ─────────────────────────────────────
                      _buildLabeledField(
                        label: 'New Password',
                        controller: _passwordController,
                        hintText: 'Min. 8 characters',
                        obscureText: _obscurePassword,
                        onToggle: () => setState(() => _obscurePassword = !_obscurePassword),
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return 'Please enter a password.';
                          if (v.trim().length < 8) return 'Password must be at least 8 characters.';
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      // ── Confirm password ─────────────────────────────────
                      _buildLabeledField(
                        label: 'Confirm Password',
                        controller: _confirmPasswordController,
                        hintText: 'Repeat your new password',
                        obscureText: _obscureConfirm,
                        onToggle: () => setState(() => _obscureConfirm = !_obscureConfirm),
                        validator: (v) {
                          if (v != _passwordController.text) return 'Passwords do not match.';
                          return null;
                        },
                      ),
                      const SizedBox(height: 32),

                      // ── Error banner ─────────────────────────────────────
                      if (state.status == ResetPasswordStatus.error &&
                          state.errorMessage != null) ...[
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.red.shade50,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.red.shade200),
                          ),
                          child: Text(
                            state.errorMessage!,
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.red.shade700, fontSize: 14),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],

                      // ── Submit button ────────────────────────────────────
                      _buildSolidButton(
                        label: 'Save New Password',
                        onPressed: _submit,
                      ),

                      const SizedBox(height: 16),
                      // Back to login link
                      Center(
                        child: TextButton(
                          onPressed: () => context.go('/welcome'),
                          style: TextButton.styleFrom(
                            foregroundColor: GlowTheme.deepTaupe,
                            textStyle: const TextStyle(fontSize: 14),
                          ),
                          child: const Text('Back to Login'),
                        ),
                      ),
                    ],
                  ),
                ),
        ),
      ),
    );
  }

  // ── Reusable Widgets (matching auth_bottom_sheet.dart style) ───────────────

  Widget _buildLabeledField({
    required String label,
    required TextEditingController controller,
    required String hintText,
    required bool obscureText,
    required VoidCallback onToggle,
    String? Function(String?)? validator,
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
        TextFormField(
          controller: controller,
          obscureText: obscureText,
          validator: validator,
          style: const TextStyle(color: GlowTheme.deepTaupe),
          decoration: InputDecoration(
            hintText: hintText,
            hintStyle: const TextStyle(color: GlowTheme.oatmeal),
            filled: true,
            fillColor: Colors.white,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
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
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.red.shade300, width: 1),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.red.shade400, width: 1.5),
            ),
            suffixIcon: IconButton(
              icon: Icon(
                obscureText
                    ? Icons.visibility_off_outlined
                    : Icons.visibility_outlined,
                color: GlowTheme.deepTaupe,
              ),
              onPressed: onToggle,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSolidButton({
    required String label,
    required VoidCallback onPressed,
  }) {
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
}
