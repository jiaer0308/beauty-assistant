import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:app_links/app_links.dart';
import 'core/theme/glow_theme.dart';
import 'core/router/app_router.dart';
import 'features/auth/presentation/providers/reset_password_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: BeautyAssistantApp()));
}

class BeautyAssistantApp extends ConsumerStatefulWidget {
  const BeautyAssistantApp({super.key});

  @override
  ConsumerState<BeautyAssistantApp> createState() => _BeautyAssistantAppState();
}

class _BeautyAssistantAppState extends ConsumerState<BeautyAssistantApp> {
  late final AppLinks _appLinks;

  @override
  void initState() {
    super.initState();
    _initDeepLinks();
  }

  void _initDeepLinks() {
    _appLinks = AppLinks();

    // ── Warm start: app already running, receives link via stream ──
    _appLinks.uriLinkStream.listen(
      (uri) {
        debugPrint('Deep link (stream): $uri');
        _handleUri(uri);
      },
      onError: (err) => debugPrint('Deep link error: $err'),
    );

    // ── Cold start: app launched by tapping the deep link ──
    // Uses addPostFrameCallback so the router & providers are initialised first.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _appLinks.getInitialLink().then((uri) {
        if (uri != null) {
          debugPrint('Deep link (initial / cold-start): $uri');
          _handleUri(uri);
        }
      });
    });
  }

  /// Handles a `beautyassistant://reset-password?token=<uuid>` URI.
  ///
  /// Strategy:
  ///   1. Try to navigate immediately via GoRouter (works when app is fully
  ///      initialised and already past the splash screen — i.e. warm start).
  ///   2. Also write the token to [pendingResetTokenProvider] as a safety net.
  ///      The SplashScreen reads this after auth-init and will navigate to
  ///      /reset-password before it goes to /dashboard or /welcome.
  void _handleUri(Uri uri) {
    if (uri.scheme != 'beautyassistant') return;

    final isResetPassword =
        uri.host == 'reset-password' ||
        uri.path == 'reset-password' ||
        uri.path.startsWith('/reset-password');

    if (!isResetPassword) return;

    final token = uri.queryParameters['token'] ?? '';
    if (token.isEmpty) return;

    debugPrint('Deep link: reset token = $token');

    // Always store the token so SplashScreen can pick it up (cold start safety)
    ref.read(pendingResetTokenProvider.notifier).state = token;

    // Also attempt immediate navigation (works for warm start)
    try {
      final router = ref.read(appRouterProvider);
      router.go('/reset-password?token=$token');
      debugPrint('Deep link: navigated immediately to /reset-password');
    } catch (e) {
      debugPrint('Deep link: immediate navigation failed (cold start?) — token stored for SplashScreen: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'Glow Beauty Assistant',
      theme: GlowTheme.lightTheme,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
