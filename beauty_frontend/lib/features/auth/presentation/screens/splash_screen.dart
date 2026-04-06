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
  bool _hasError = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    setState(() {
      _hasError = false;
      _errorMessage = null;
    });

    debugPrint('SplashScreen: Initializing app...');
    final authNotifier = ref.read(authProvider.notifier);
    
    try {
      debugPrint('SplashScreen: Calling authNotifier.init()...');
      await authNotifier.init().timeout(const Duration(seconds: 15));
      debugPrint('SplashScreen: authNotifier.init() completed.');
    } catch (e) {
      debugPrint('SplashScreen: Error during authNotifier.init(): $e');
      // If it times out or fails, we might still want to try guest login or show error
    }
    
    if (!mounted) return;

    final authState = ref.read(authProvider);
    debugPrint('SplashScreen: Current AuthStatus: ${authState.status}');
    
    if (authState.status == AuthStatus.authenticated) {
      context.go('/dashboard');
    } else if (authState.status == AuthStatus.guest) {
      context.go('/welcome');
    } else {
      debugPrint('SplashScreen: Attempting loginAsGuest()...');
      try {
        await authNotifier.loginAsGuest().timeout(const Duration(seconds: 15));
        debugPrint('SplashScreen: loginAsGuest() completed.');
        
        if (mounted) {
          final newState = ref.read(authProvider);
          if (newState.status == AuthStatus.error) {
            setState(() {
              _hasError = true;
              _errorMessage = newState.errorMessage ?? 'Connection failed';
            });
            return;
          }
          context.go('/welcome');
        }
      } catch (e) {
        debugPrint('SplashScreen: Error during loginAsGuest(): $e');
        if (mounted) {
          setState(() {
            _hasError = true;
            _errorMessage = 'Could not connect to server. Please check your internet.';
          });
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Listen for state changes and navigate automatically
    ref.listen<AuthState>(authProvider, (previous, next) {
      debugPrint('SplashScreen: State change detected: ${next.status}');
      if (next.status == AuthStatus.authenticated) {
        debugPrint('SplashScreen: Navigating to /dashboard');
        context.go('/dashboard');
      } else if (next.status == AuthStatus.guest) {
        debugPrint('SplashScreen: Navigating to /welcome');
        context.go('/welcome');
      }
    });

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'GLOW',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                letterSpacing: 4.0,
                color: GlowTheme.deepTaupe,
              ),
            ),
            const SizedBox(height: 48),
            if (_hasError) ...[
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: Text(
                  _errorMessage ?? 'An error occurred',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.redAccent),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _initializeApp,
                style: ElevatedButton.styleFrom(
                  backgroundColor: GlowTheme.champagneGold,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Retry Connection'),
              ),
            ] else ...[
              const CircularProgressIndicator(color: GlowTheme.champagneGold),
              const SizedBox(height: 16),
              const Text(
                'Connecting...',
                style: TextStyle(color: GlowTheme.deepTaupe, fontSize: 12),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
