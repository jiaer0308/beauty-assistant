import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import '../providers/auth_provider.dart';
import '../../models/auth_state.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    final authNotifier = ref.read(authProvider.notifier);
    await authNotifier.init();
    
    if (!mounted) return;

    final authState = ref.read(authProvider);
    
    if (authState.status == AuthStatus.authenticated) {
      context.go('/dashboard');
    } else if (authState.status == AuthStatus.guest) {
      context.go('/onboarding');
    } else {
      await authNotifier.loginAsGuest();
      if (mounted) context.go('/onboarding');
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'GLOW',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                letterSpacing: 4.0,
                color: GlowTheme.deepTaupe,
              ),
            ),
            SizedBox(height: 24),
            CircularProgressIndicator(color: GlowTheme.champagneGold),
          ],
        ),
      ),
    );
  }
}
